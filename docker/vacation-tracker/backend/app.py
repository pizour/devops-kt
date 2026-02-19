import hashlib
import os
import sqlite3
from datetime import date, datetime, timedelta

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

try:
    import pam  # type: ignore
except ImportError:  # pragma: no cover - runtime requirement documented in README
    pam = None

try:
    import msal  # type: ignore
except ImportError:  # pragma: no cover - runtime requirement documented in README
    msal = None


def create_app():
    app = Flask(__name__)

    app.config["DATABASE"] = os.environ.get(
        "VACATION_DB_PATH", os.path.join(app.instance_path, "vacations.db")
    )
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-change-me")
    # Expose auth backend choice to templates and helpers.
    app.config["AUTH_BACKEND"] = os.environ.get("AUTH_BACKEND", "pam").lower()

    os.makedirs(app.instance_path, exist_ok=True)

    @app.before_request
    def load_logged_in_user():
        username = session.get("username")
        g.user = username if username else None

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(
                app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(exc=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = get_db()
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS vacations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                edited_at TIMESTAMP,
                comment TEXT,
                slot TEXT
            );

            CREATE TABLE IF NOT EXISTS entra_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                tenant_id TEXT,
                client_id TEXT,
                client_secret TEXT,
                enabled INTEGER NOT NULL DEFAULT 0,
                registration_token TEXT,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        # Ensure new columns exist for older databases.
        user_columns = db.execute("PRAGMA table_info(users)").fetchall()
        user_col_names = {col["name"] for col in user_columns}
        if "is_admin" not in user_col_names:
            db.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0")
        # Ensure edited_at and comment columns exist for older databases.
        columns = db.execute("PRAGMA table_info(vacations)").fetchall()
        col_names = {col["name"] for col in columns}
        if "edited_at" not in col_names:
            db.execute("ALTER TABLE vacations ADD COLUMN edited_at TIMESTAMP")
        if "comment" not in col_names:
            db.execute("ALTER TABLE vacations ADD COLUMN comment TEXT")
        if "slot" not in col_names:
            db.execute("ALTER TABLE vacations ADD COLUMN slot TEXT")
        # Ensure there is a single entra_config row.
        entra_columns = db.execute("PRAGMA table_info(entra_config)").fetchall()
        entra_col_names = {col["name"] for col in entra_columns}
        if "registration_token" not in entra_col_names:
            db.execute("ALTER TABLE entra_config ADD COLUMN registration_token TEXT")
        row = db.execute("SELECT id FROM entra_config WHERE id = 1").fetchone()
        if row is None:
            db.execute("INSERT INTO entra_config (id, enabled) VALUES (1, 0)")
        db.commit()

    @app.cli.command("init-db")
    def init_db_command():
        """Initialize the database tables."""
        init_db()
        print("Initialized the database.")

    def authenticate_with_pam(username: str, password: str) -> bool:
        """Authenticate against local Linux accounts via PAM."""
        if pam is None:
            app.logger.error("PAM module is not available; refusing all logins.")
            return False

        service = os.environ.get("PAM_SERVICE", "login")
        p = pam.pam()
        ok = p.authenticate(username, password, service=service)
        if not ok:
            reason = getattr(p, "reason", "unknown reason")
            app.logger.warning(
                "PAM authentication failed for user '%s' via service '%s': %s",
                username,
                service,
                reason,
            )
        return bool(ok)

    def authenticate_internal(username: str, password: str) -> bool:
        """Authenticate against usernames/passwords stored in the app database."""
        db = get_db()
        row = db.execute(
            "SELECT password_hash FROM users WHERE username = ?", (username,)
        ).fetchone()
        if row is None:
            return False
        return check_password_hash(row["password_hash"], password)

    def active_auth_backend() -> str:
        return app.config.get("AUTH_BACKEND", os.environ.get("AUTH_BACKEND", "pam")).lower()

    def is_admin_user(username: str | None) -> bool:
        if not username:
            return False
        db = get_db()
        row = db.execute(
            "SELECT is_admin FROM users WHERE username = ?", (username,)
        ).fetchone()
        db_flag = bool(row["is_admin"]) if row and "is_admin" in row.keys() else False
        admins_env = os.environ.get("ADMIN_USERS", "")
        admins = {item.strip() for item in admins_env.split(",") if item.strip()}
        env_flag = username in admins
        return db_flag or env_flag

    @app.context_processor
    def inject_role_flags():
        username = getattr(g, "user", None)
        return {
            "is_admin": is_admin_user(username),
            "can_change_password": active_auth_backend() == "internal"
            and session.get("auth_source") != "sso",
        }

    def get_entra_config():
        # Ensure schema exists before reading configuration.
        init_db()
        db = get_db()
        row = db.execute(
            """
            SELECT tenant_id, client_id, client_secret, enabled, registration_token
            FROM entra_config
            WHERE id = 1
            """
        ).fetchone()
        if row is None:
            return None
        return {
            "tenant_id": row["tenant_id"],
            "client_id": row["client_id"],
            "client_secret": row["client_secret"],
            "enabled": bool(row["enabled"]),
            "registration_token": row["registration_token"],
        }

    def build_msal_app(config: dict):
        if msal is None:
            return None
        authority = f"https://login.microsoftonline.com/{config['tenant_id']}"
        return msal.ConfidentialClientApplication(
            config["client_id"],
            authority=authority,
            client_credential=config["client_secret"],
        )

    @app.route("/login", methods=["GET", "POST"])
    def login():
        backend = active_auth_backend()
        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"]

            if not username or not password:
                flash("Username and password are required.", "error")
            else:
                if backend == "internal":
                    ok = authenticate_internal(username, password)
                else:
                    ok = authenticate_with_pam(username, password)

                if not ok:
                    flash("Invalid username or password.", "error")
                else:
                    session.clear()
                    session["username"] = username
                    session["auth_source"] = backend
                    flash(f"Logged in as {username}.", "success")
                    return redirect(url_for("calendar_view"))

        return render_template("login.html")

    @app.route("/login/sso")
    def login_sso():
        config = get_entra_config()
        if msal is None:
            flash("SSO is not available on this server (msal library missing).", "error")
            return redirect(url_for("login"))
        if not config or not config.get("enabled") or not all(
            [config.get("tenant_id"), config.get("client_id"), config.get("client_secret")]
        ):
            flash(
                "SSO is not configured. Please contact Devops-KT developer",
                "error",
            )
            return redirect(url_for("login"))

        client = build_msal_app(config)
        if client is None:
            flash("SSO is not available on this server.", "error")
            return redirect(url_for("login"))

        redirect_uri = url_for("entra_callback", _external=True)
        # Use a non-reserved scope for sign-in (e.g. Microsoft Graph "User.Read").
        auth_url = client.get_authorization_request_url(
            scopes=["User.Read"],
            redirect_uri=redirect_uri,
        )
        return redirect(auth_url)

    @app.route("/auth/entra/callback")
    def entra_callback():
        if msal is None:
            flash("SSO is not available on this server.", "error")
            return redirect(url_for("login"))

        config = get_entra_config()
        if not config or not config.get("enabled"):
            flash(
                "SSO is not configured. Please contact Devops-KT developer",
                "error",
            )
            return redirect(url_for("login"))

        code = request.args.get("code")
        if not code:
            flash("SSO login failed: missing authorization code.", "error")
            return redirect(url_for("login"))

        client = build_msal_app(config)
        if client is None:
            flash("SSO is not available on this server.", "error")
            return redirect(url_for("login"))

        redirect_uri = url_for("entra_callback", _external=True)
        result = client.acquire_token_by_authorization_code(
            code,
            scopes=["User.Read"],
            redirect_uri=redirect_uri,
        )

        id_claims = result.get("id_token_claims") or {}
        # Prefer display name from Entra over email-style identifiers.
        username = (
            id_claims.get("name")
            or id_claims.get("preferred_username")
            or id_claims.get("upn")
            or id_claims.get("email")
        )
        if not username:
            flash("SSO login failed: no username in identity token.", "error")
            return redirect(url_for("login"))

        username = username.lower()

        # Ensure a local user record exists for this SSO account.
        db = get_db()
        existing = db.execute(
            "SELECT username FROM users WHERE username = ?", (username,)
        ).fetchone()
        if existing is None:
            # Create with a random placeholder password hash; password is not used for SSO accounts.
            placeholder_password = generate_password_hash(os.urandom(16).hex())
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, placeholder_password),
            )
            db.commit()

        session.clear()
        session["username"] = username
        session["auth_source"] = "sso"
        flash(f"Logged in via SSO as {username}.", "success")
        return redirect(url_for("calendar_view"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if active_auth_backend() != "internal":
            flash("Registration is disabled when PAM authentication is active.", "error")
            return redirect(url_for("login"))

        username_value = ""

        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"]
            confirm = request.form["confirm_password"]
            registration_token = request.form.get("registration_token", "").strip()
            config = get_entra_config()
            expected_token = ""
            if config and config.get("registration_token"):
                expected_token = config["registration_token"].strip()
            else:
                expected_token = os.environ.get("REGISTRATION_TOKEN", "").strip()
            username_value = username
            is_initial_admin = username.lower() == "admin"

            if not expected_token and not is_initial_admin:
                flash("Registration is currently disabled (registration token not configured).", "error")
                return redirect(url_for("login"))

            if not username or not password or (not registration_token and not is_initial_admin):
                flash("Username, password and registration token are required.", "error")
            elif password != confirm:
                flash("Passwords do not match.", "error")
            elif registration_token != expected_token and not is_initial_admin:
                flash("Invalid registration token.", "error")
            else:
                db = get_db()
                try:
                    db.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        (username, generate_password_hash(password)),
                    )
                    db.commit()
                except sqlite3.IntegrityError:
                    flash("Username is already taken.", "error")
                else:
                    flash("Account created. You can now log in.", "success")
                    return redirect(url_for("login"))

        return render_template("register.html", username=username_value)

    @app.route("/change-password", methods=["GET", "POST"])
    def change_password():
        if g.user is None:
            return redirect(url_for("login"))

        if active_auth_backend() != "internal":
            flash("Password changes are only available for internal accounts.", "error")
            return redirect(url_for("calendar_view"))

        if session.get("auth_source") == "sso":
            flash("Password changes are not available for SSO accounts.", "error")
            return redirect(url_for("calendar_view"))

        if request.method == "POST":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not current_password or not new_password:
                flash("All password fields are required.", "error")
            elif new_password != confirm_password:
                flash("New passwords do not match.", "error")
            elif not authenticate_internal(g.user, current_password):
                flash("Current password is incorrect.", "error")
            else:
                db = get_db()
                db.execute(
                    "UPDATE users SET password_hash = ? WHERE username = ?",
                    (generate_password_hash(new_password), g.user),
                )
                db.commit()
                flash("Password updated successfully.", "success")
                return redirect(url_for("calendar_view"))

        return render_template("change_password.html")

    @app.route("/admin/users")
    def admin_users():
        if g.user is None:
            return redirect(url_for("login"))
        if active_auth_backend() != "internal":
            flash("User management is only available for internal accounts.", "error")
            return redirect(url_for("calendar_view"))
        if not is_admin_user(g.user):
            flash("You must be an admin to manage users.", "error")
            return redirect(url_for("calendar_view"))

        db = get_db()
        users = db.execute(
            """
            SELECT username, created_at, is_admin
            FROM users
            ORDER BY username
            """
        ).fetchall()

        return render_template("admin_users.html", users=users)

    @app.route("/admin/users/<username>/admin", methods=["POST"])
    def admin_set_admin(username: str):
        if g.user is None:
            return redirect(url_for("login"))
        if active_auth_backend() != "internal":
            flash("User management is only available for internal accounts.", "error")
            return redirect(url_for("calendar_view"))
        if not is_admin_user(g.user):
            flash("You must be an admin to manage users.", "error")
            return redirect(url_for("calendar_view"))

        action = request.form.get("action")
        if action not in {"grant", "revoke"}:
            flash("Invalid admin action.", "error")
            return redirect(url_for("admin_users"))

        db = get_db()
        user_row = db.execute(
            "SELECT username FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user_row is None:
            flash("User not found.", "error")
            return redirect(url_for("admin_users"))

        is_admin_value = 1 if action == "grant" else 0
        db.execute(
            "UPDATE users SET is_admin = ? WHERE username = ?",
            (is_admin_value, username),
        )
        db.commit()
        if action == "grant":
            flash(f"User {username} is now an admin.", "success")
        else:
            flash(f"User {username} is no longer an admin.", "success")
        return redirect(url_for("admin_users"))

    @app.route("/admin/entra", methods=["GET", "POST"])
    def admin_entra():
        if g.user is None:
            return redirect(url_for("login"))
        if not is_admin_user(g.user):
            flash("You must be an admin to manage SSO settings.", "error")
            return redirect(url_for("calendar_view"))

        db = get_db()
        row = db.execute(
            "SELECT tenant_id, client_id, client_secret, enabled, registration_token FROM entra_config WHERE id = 1"
        ).fetchone()
        current = {
            "tenant_id": row["tenant_id"] if row else "",
            "client_id": row["client_id"] if row else "",
            "client_secret": bool(row and row["client_secret"]),
            "enabled": bool(row and row["enabled"]),
            "registration_token": row["registration_token"] if row else "",
        }

        if request.method == "POST":
            tenant_id = request.form.get("tenant_id", "").strip()
            client_id = request.form.get("client_id", "").strip()
            client_secret = request.form.get("client_secret", "")
            registration_token = request.form.get("registration_token", "").strip()
            enabled = bool(request.form.get("enabled"))

            if enabled and (not tenant_id or not client_id):
                flash("Tenant ID and Client ID are required when enabling SSO.", "error")
            else:
                # Keep existing secret if the field is left blank.
                if client_secret.strip():
                    db.execute(
                        """
                        UPDATE entra_config
                        SET tenant_id = ?, client_id = ?, client_secret = ?, registration_token = ?, enabled = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = 1
                        """,
                        (tenant_id, client_id, client_secret, registration_token, int(enabled)),
                    )
                else:
                    db.execute(
                        """
                        UPDATE entra_config
                        SET tenant_id = ?, client_id = ?, registration_token = ?, enabled = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = 1
                        """,
                        (tenant_id, client_id, registration_token, int(enabled)),
                    )
                db.commit()
                flash("SSO settings updated.", "success")
                return redirect(url_for("admin_entra"))

            current["tenant_id"] = tenant_id
            current["client_id"] = client_id
            current["enabled"] = enabled
            current["registration_token"] = registration_token

        return render_template("admin_entra.html", config=current)

    @app.route("/admin/users/<username>/password", methods=["GET", "POST"])
    def admin_change_user_password(username: str):
        if g.user is None:
            return redirect(url_for("login"))
        if active_auth_backend() != "internal":
            flash("User management is only available for internal accounts.", "error")
            return redirect(url_for("calendar_view"))
        if not is_admin_user(g.user):
            flash("You must be an admin to manage users.", "error")
            return redirect(url_for("calendar_view"))

        db = get_db()
        user_row = db.execute(
            "SELECT username FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user_row is None:
            flash("User not found.", "error")
            return redirect(url_for("admin_users"))

        if request.method == "POST":
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not new_password:
                flash("New password is required.", "error")
            elif new_password != confirm_password:
                flash("New passwords do not match.", "error")
            else:
                db.execute(
                    "UPDATE users SET password_hash = ? WHERE username = ?",
                    (generate_password_hash(new_password), username),
                )
                db.commit()
                flash(f"Password for user {username} has been updated.", "success")
                return redirect(url_for("admin_users"))

        return render_template("admin_change_password.html", managed_username=username)

    @app.route("/admin/users/<username>/delete", methods=["GET", "POST"])
    def admin_delete_user(username: str):
        if g.user is None:
            return redirect(url_for("login"))
        if active_auth_backend() != "internal":
            flash("User management is only available for internal accounts.", "error")
            return redirect(url_for("calendar_view"))
        if not is_admin_user(g.user):
            flash("You must be an admin to manage users.", "error")
            return redirect(url_for("calendar_view"))

        db = get_db()
        user_row = db.execute(
            "SELECT username FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user_row is None:
            flash("User not found.", "error")
            return redirect(url_for("admin_users"))

        if request.method == "GET":
            return render_template(
                "admin_confirm_delete_user.html", managed_username=username
            )

        # POST: validate confirmation text and perform deletion.
        confirm_text = request.form.get("confirm_text", "").strip().lower()
        if confirm_text != "delete":
            flash('You must type "delete" to confirm removal.', "error")
            return render_template(
                "admin_confirm_delete_user.html", managed_username=username
            )

        if username == g.user:
            flash("You cannot delete your own account while logged in.", "error")
            return redirect(url_for("admin_users"))

        # Remove the user's bookings and then the user record.
        db.execute("DELETE FROM vacations WHERE username = ?", (username,))
        db.execute("DELETE FROM users WHERE username = ?", (username,))
        db.commit()
        flash(f"User {username} and their bookings have been removed.", "success")
        return redirect(url_for("admin_users"))

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))

    def parse_date(value: str):
        return datetime.strptime(value, "%Y-%m-%d").date()

    def month_bounds(year: int, month: int):
        first = date(year, month, 1)
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        last = next_month - timedelta(days=1)
        return first, last

    def booking_slots(start_date: date, end_date: date, slot: str | None):
        """Expand a booking into AM/PM half-day slots per calendar day.

        Full-day bookings occupy both AM and PM; half-day bookings occupy
        only the requested half on their day.
        """
        normalized = (slot or "").lower()
        slots = set()
        current = start_date
        while current <= end_date:
            if normalized in ("am", "pm"):
                slots.add((current, normalized))
            else:
                slots.add((current, "am"))
                slots.add((current, "pm"))
            current += timedelta(days=1)
        return slots

    def has_booking_conflict(
        username: str,
        start_date: date,
        end_date: date,
        slot: str | None,
        exclude_booking_id: int | None = None,
    ) -> bool:
        """Check for overlapping bookings for a given user, including half-days.

        Full-day bookings block both AM and PM. Half-day bookings block only
        their own half; booking the other half on the same day is allowed.
        """
        db = get_db()
        params: list[object] = [username]
        query = "SELECT id, start_date, end_date, slot FROM vacations WHERE username = ?"
        if exclude_booking_id is not None:
            query += " AND id != ?"
            params.append(exclude_booking_id)
        rows = db.execute(query, params).fetchall()

        new_slots = booking_slots(start_date, end_date, slot)
        for row in rows:
            existing_slots = booking_slots(
                row["start_date"], row["end_date"], row["slot"]
            )
            if new_slots & existing_slots:
                return True
        return False

    @app.route("/", methods=["GET"])
    def index():
        if g.user is None:
            return redirect(url_for("login"))
        return redirect(url_for("calendar_view"))

    @app.route("/calendar", methods=["GET", "POST"])
    def calendar_view():
        if g.user is None:
            return redirect(url_for("login"))

        today = date.today()
        year = int(request.values.get("year", today.year))
        month = int(request.values.get("month", today.month))

        first_day, last_day = month_bounds(year, month)

        # Use a date within the currently displayed month to initialize the browser date pickers.
        today = date.today()
        if today.year == year and today.month == month:
            picker_reference = today
        else:
            picker_reference = first_day
        picker_value = picker_reference.isoformat()

        is_admin = is_admin_user(g.user)

        # Defaults for re-populating the booking form on validation errors.
        form_start_date = None
        form_end_date = None
        form_comment = ""
        form_booking_username = ""
        form_slot_mode = "full"
        form_slot_half = ""

        if request.method == "POST":
            db = get_db()
            start_raw = request.form.get("start_date")
            end_raw = request.form.get("end_date")
            comment_raw = request.form.get("comment", "")
            mode_raw = request.form.get("slot_mode", "full")
            half_raw = request.form.get("slot_half", "").lower()
            mode = (mode_raw or "full").lower()
            form_start_date = start_raw or None
            form_end_date = end_raw or None
            form_comment = comment_raw
            form_slot_mode = mode
            form_slot_half = half_raw
            if is_admin:
                form_booking_username = request.form.get("booking_username", "").strip()

            validation_failed = False

            if mode == "half":
                if half_raw not in ("am", "pm"):
                    flash("Please choose AM or PM for half-day bookings.", "error")
                    validation_failed = True
                    slot = None
                else:
                    slot = half_raw
            else:
                slot = "full"

            if not start_raw or not end_raw:
                flash("Start and end dates are required.", "error")
                validation_failed = True
            else:
                try:
                    start_date = parse_date(start_raw)
                    end_date = parse_date(end_raw)
                    if end_date < start_date:
                        raise ValueError("End date before start date.")
                except ValueError:
                    flash("Invalid date range.", "error")
                    validation_failed = True
                else:
                    if slot is not None:
                        # Determine which username to use for the booking.
                        booking_username = g.user
                        if is_admin:
                            other_user = request.form.get("booking_username", "").strip()
                            if other_user:
                                booking_username = other_user

                        # Prevent overlapping bookings (including half-days) for the same user.
                        if has_booking_conflict(
                            booking_username, start_date, end_date, slot
                        ):
                            flash(
                                "You already have a vacation overlapping that date range.",
                                "error",
                            )
                            validation_failed = True
                        else:
                            db.execute(
                                """
                                INSERT INTO vacations (username, start_date, end_date, comment, slot)
                                VALUES (?, ?, ?, ?, ?)
                                """,
                                (
                                    booking_username,
                                    start_date,
                                    end_date,
                                    comment_raw.strip() or None,
                                    None if slot == "full" else slot,
                                ),
                            )
                            db.commit()
                            flash("Vacation booked.", "success")
                            return redirect(
                                url_for(
                                    "calendar_view",
                                    year=year,
                                    month=month,
                                )
                            )

        db = get_db()
        init_db()
        rows = db.execute(
            """
            SELECT id, username, start_date, end_date, comment, slot
            FROM vacations
            WHERE (start_date <= ? AND end_date >= ?)
            ORDER BY start_date, username
            """,
            (last_day, first_day),
        ).fetchall()

        # Assign a stable color per user, consistent across months, using HSL from a hash.
        usernames = {row["username"] for row in rows}

        def color_for_username(username: str) -> str:
            digest = hashlib.sha256(username.encode("utf-8")).digest()
            hue = (digest[0] / 255.0) * 360.0
            saturation = 55 + (digest[1] % 30)  # 55–84%
            lightness = 40 + (digest[2] % 20)   # 40–59%
            return f"hsl({hue:.0f}, {saturation}%, {lightness}%)"

        user_colors = {
            username: color_for_username(username)
            for username in usernames
        }

        # Build a mapping of day -> list of vacation entries (username + optional comment)
        days = {}
        cursor = first_day
        while cursor <= last_day:
            days[cursor] = []
            cursor += timedelta(days=1)

        for row in rows:
            slot = (row["slot"] or "").lower()
            start = row["start_date"]
            end = row["end_date"]
            current = max(start, first_day)
            last = min(end, last_day)
            while current <= last:
                days.setdefault(current, []).append(
                    {
                        "username": row["username"],
                        "comment": row["comment"],
                        "slot": slot if slot in ("am", "pm") else "full",
                    }
                )
                current += timedelta(days=1)

        user_bookings = [row for row in rows if row["username"] == g.user]
        all_bookings = rows if is_admin else []

        # Group days into weeks starting on Monday
        calendar_weeks = []
        week = [None] * 7
        start_weekday = first_day.weekday()  # Monday=0
        cursor = first_day
        i = start_weekday
        while cursor <= last_day:
            week[i] = {
                "date": cursor,
                "vacation_users": days.get(cursor, []),
            }
            if i == 6:
                calendar_weeks.append(week)
                week = [None] * 7
                i = 0
            else:
                i += 1
            cursor += timedelta(days=1)
        if any(day is not None for day in week):
            calendar_weeks.append(week)

        # Previous/next month navigation
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1

        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1

        # If the user submitted a form with errors, keep their entered start date
        # as the picker default.
        if form_start_date:
            picker_value = form_start_date

        return render_template(
            "calendar.html",
            year=year,
            month=month,
            calendar_weeks=calendar_weeks,
            first_day=first_day,
            last_day=last_day,
            prev_year=prev_year,
            prev_month=prev_month,
            next_year=next_year,
            next_month=next_month,
            user_bookings=user_bookings,
            all_bookings=all_bookings,
            user_colors=user_colors,
            is_admin=is_admin,
            picker_value=picker_value,
            form_start_date=form_start_date,
            form_end_date=form_end_date,
            form_comment=form_comment,
            form_booking_username=form_booking_username,
            slot_mode=form_slot_mode,
            slot_half=form_slot_half,
        )

    @app.route("/booking/<int:booking_id>/delete", methods=["POST"])
    def delete_booking(booking_id: int):
        if g.user is None:
            return redirect(url_for("login"))

        db = get_db()
        is_admin = is_admin_user(g.user)
        booking = db.execute(
            "SELECT id, username FROM vacations WHERE id = ?", (booking_id,)
        ).fetchone()

        if booking is None:
            flash("Booking not found.", "error")
        elif booking["username"] != g.user and not is_admin:
            flash("You can only delete your own bookings.", "error")
        else:
            db.execute("DELETE FROM vacations WHERE id = ?", (booking_id,))
            db.commit()
            flash("Booking removed.", "success")

        return redirect(
            url_for(
                "calendar_view",
                year=request.args.get("year"),
                month=request.args.get("month"),
            )
        )

    @app.route("/booking/<int:booking_id>/edit", methods=["GET", "POST"])
    def edit_booking(booking_id: int):
        if g.user is None:
            return redirect(url_for("login"))

        db = get_db()
        is_admin = is_admin_user(g.user)
        booking = db.execute(
            """
            SELECT id, username, start_date, end_date, comment, slot
            FROM vacations
            WHERE id = ?
            """,
            (booking_id,),
        ).fetchone()

        if booking is None:
            flash("Booking not found.", "error")
            return redirect(url_for("calendar_view"))

        if booking["username"] != g.user and not is_admin:
            flash("You can only edit your own bookings.", "error")
            return redirect(url_for("calendar_view"))

        if request.method == "POST":
            start_raw = request.form.get("start_date")
            end_raw = request.form.get("end_date")
            comment_raw = request.form.get("comment", "")
            mode_raw = request.form.get("slot_mode", "full")
            half_raw = request.form.get("slot_half", "").lower()
            mode = (mode_raw or "full").lower()
            if mode == "half":
                if half_raw not in ("am", "pm"):
                    flash("Please choose AM or PM for half-day bookings.", "error")
                    return redirect(url_for("calendar_view"))
                slot = half_raw
            else:
                slot = "full"
            if not start_raw or not end_raw:
                flash("Start and end dates are required.", "error")
            else:
                try:
                    start_date = parse_date(start_raw)
                    end_date = parse_date(end_raw)
                    if end_date < start_date:
                        raise ValueError("End date before start date.")
                except ValueError:
                    flash("Invalid date range.", "error")
                else:
                    # Prevent overlapping bookings for the same user, excluding this booking.
                    if has_booking_conflict(
                        booking["username"],
                        start_date,
                        end_date,
                        slot,
                        exclude_booking_id=booking_id,
                    ):
                        flash(
                            "This user already has a vacation overlapping that date range.",
                            "error",
                        )
                    else:
                        db.execute(
                            """
                            UPDATE vacations
                            SET start_date = ?, end_date = ?, comment = ?, slot = ?, edited_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                            """,
                            (
                                start_date,
                                end_date,
                                comment_raw.strip() or None,
                                None if slot == "full" else slot,
                                booking_id,
                            ),
                        )
                        db.commit()
                        flash("Booking updated.", "success")
                        return redirect(url_for("calendar_view"))

        return render_template("edit_booking.html", booking=booking)

    @app.route("/overview")
    def overview():
        if g.user is None:
            return redirect(url_for("login"))

        db = get_db()
        is_admin = is_admin_user(g.user)

        if is_admin:
            rows = db.execute(
                """
                SELECT id, username, start_date, end_date, created_at, edited_at, comment, slot
                FROM vacations
                ORDER BY start_date DESC, username
                """
            ).fetchall()
        else:
            rows = db.execute(
                """
                SELECT id, username, start_date, end_date, created_at, edited_at, comment, slot
                FROM vacations
                WHERE username = ?
                ORDER BY start_date DESC
                """,
                (g.user,),
            ).fetchall()

        return render_template("overview.html", bookings=rows, is_admin=is_admin)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
