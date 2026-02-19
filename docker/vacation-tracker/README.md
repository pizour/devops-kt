# Vacation Tracker

Team vacation tracking website with shared calendar, comments, and multiple authentication options (local accounts, PAM, and Microsoft Entra SSO).

## Features

- Shared month calendar showing all users’ vacations (per-user colors, comments, weekends greyed out).
- Users can book vacation ranges (start–end date), edit and remove their own bookings.
- Support for full-day and half-day (AM/PM) bookings, clearly marked in the calendar and lists.
- Per-user collision prevention (no overlapping bookings for the same user, including at half-day slot level).
- Admin functions:
  - View “All bookings this month” and a cross-month “Overview” (with created/edited timestamps).
  - Manage users: reset passwords, grant/revoke admin rights, remove users (with confirmation).
  - Configure Microsoft Entra (Azure AD) SSO in the UI.
- Multiple authentication methods:
  - Local accounts stored in SQLite (with registration token).
  - PAM against local Linux users.
  - SSO via Microsoft Entra.
- Runs directly on a Linux host or in a container via Docker Compose.

## Project layout

- `backend/` – Flask application, templates, static assets.
- `Dockerfile` – Container image for the app.
- `docker-compose.yml` – Container orchestration with a volume for the SQLite database.

## Authentication modes

The app supports three logical auth flows:

- **Local accounts (default in Docker Compose)**
  - Users log in with a username/password stored in the `users` table.
  - Users can change their own password (unless they logged in via SSO).
  - New users must supply a **registration token** (see `REGISTRATION_TOKEN` below).

- **PAM (local Linux accounts)**
  - When `AUTH_BACKEND=pam`, login uses system PAM.
  - No passwords are stored by the app; they are only checked via PAM.
  - Typically used when running directly on a Linux host or in a container with proper PAM setup.

- **Microsoft Entra SSO**
  - Users click the “Sign in with Microsoft” button and log in using their Entra account.
  - Admins configure SSO (Tenant ID, Client ID, Client Secret, enabled flag) on the `SSO` admin page.
  - On first SSO login, a corresponding local user record is created automatically (with a placeholder password).

## Configuration (environment variables)

The main configuration is via environment variables. When using Docker Compose, these are set under `services.vacation-tracker.environment` in `docker-compose.yml`:

- `FLASK_SECRET_KEY` – **Required in production.** Long, random string used to sign sessions.
- `VACATION_DB_PATH` – Path to the SQLite DB (default in Docker image: `/data/vacations.db`).
- `AUTH_BACKEND` – Authentication backend:
  - `internal` – use local accounts stored in SQLite (default in `docker-compose.yml`).
  - `pam` – use PAM (system accounts).
- `ADMIN_USERS` – Comma-separated list of usernames that should be admins initially. Example:
  - `ADMIN_USERS=alice,bob`
  - These users are treated as admins in addition to any `is_admin` flags stored in the DB.
- `REGISTRATION_TOKEN` – Secret token required to create new local accounts:
  - When set to a non-empty value, the registration form asks for this token.
  - The token is entered in a password-style field and is never echoed back in the UI.
  - A user can only register if the provided token matches `REGISTRATION_TOKEN`.
  - If unset or empty, self-registration is disabled.

SSO (Entra) settings are stored in the database and managed through the SSO admin page; they are not configured via environment variables.

## Running directly on a Linux machine

From the `vacation-tracker` directory:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export FLASK_SECRET_KEY="some-long-random-string"
export VACATION_DB_PATH="$(pwd)/instance/vacations.db"
export AUTH_BACKEND=internal  # or pam, if you have PAM configured

flask --app app:create_app init-db
flask --app app:create_app run --host 0.0.0.0 --port 5000
```

Then open `http://localhost:5000` in a browser.

- For `AUTH_BACKEND=pam`, log in using a Linux account on that host.
- For `AUTH_BACKEND=internal`, create users either via:
  - The registration form (when `REGISTRATION_TOKEN` is set), or
  - Direct DB access/bootstrapping if you prefer.

For a **fresh deployment**, one common pattern is:

- Start the app with a temporary registration token:

  ```bash
  REGISTRATION_TOKEN="initial-admin-token" \
  FLASK_SECRET_KEY="long-random-secret" \
  docker compose up -d
  ```

- Register the first local account with username `admin` using that token.
- Log in as `admin`, go to `Users` in the header, and grant admin rights to any additional accounts.
- Optionally clear or change the registration token afterwards (e.g. via Login settings) to control further self-registration.

> Note: For PAM mode, the process must have permission to query PAM for your local users (standard on most distributions).

## Running with Docker Compose

From the `vacation-tracker` directory:

```bash
docker compose build
docker compose up -d
```

The app will be available at `http://localhost:8000`.

Initialize the database the first time:

```bash
docker compose exec vacation-tracker flask --app app:create_app init-db
```

The SQLite database is stored in the `vacation-tracker-data` named volume.

To enable registration for local accounts, you should set a registration token (and keep it secret) when starting the stack, e.g.:

```bash
REGISTRATION_TOKEN="<your-secret-token>" \
FLASK_SECRET_KEY="long-random-secret" \
docker compose up -d
```

## First run

In order to set up access and privileges on the first run (`AUTH_BACKEND=internal`), a common pattern is:

1. Start the app (optionally with a temporary registration token):

   ```bash
   REGISTRATION_TOKEN="initial-admin-token" \
   FLASK_SECRET_KEY="long-random-secret" \
   docker compose up -d
   ```

2. Register the first local account with username `admin` and a strong password.  
   - The `admin` username is allowed to register even when no registration token is configured (bootstrap flow).
3. Log in as `admin`, open **Login settings** in the header, and configure Microsoft Entra (SSO): Tenant ID, Client ID, Client Secret, and enable SSO. Then log out.
4. Log in via SSO with your Entra account so your real user is created, then log out again.
5. Log back in as `admin`, open **Users**, and grant admin privileges to your SSO account.

> Note: Keep the local `admin` account configured and use it as a break-glass account in case Entra authentication stops working.

## Admin UI

Once logged in as an admin (from `ADMIN_USERS` or DB `is_admin` flag), the header shows:

- `Overview` – cross-month list of bookings with Created/Edited timestamps.
- `Users` – user management:
  - Reset user passwords (for internal accounts).
  - Grant / revoke admin privileges.
  - Remove users (with confirmation by typing `delete`), also removing their bookings.
- `SSO` – SSO (Microsoft Entra) configuration:
  - Set Tenant ID, Client ID, Client Secret.
  - Enable/disable SSO.
  - Shows the redirect URI to configure in Entra.
  - Configure the registration token used for local account self-registration.

## Booking behaviour

- The booking form defaults both start and end date to the currently displayed month.
- When you change the **start date** to a value later than the current **end date**, the end date is automatically moved to match the start date to avoid accidental inverted ranges.
- Half-day bookings:
  - First choose **Full day** or **Half day**; if you select half-day, additional options appear to choose **AM** or **PM**.
  - You can book half days over a multi-day range; for each day in the range, the calendar will show only the selected half (AM or PM).
  - You can also book both AM and PM on the same day as two separate entries; the calendar will show “AM” / “PM” badges.
  - Overlap detection works at the half-day level (you cannot double-book the same day/slot combo).

## Security notes

- Always set `FLASK_SECRET_KEY` to a strong, random value in production.
- Keep `REGISTRATION_TOKEN` secret; treat it like a one-time registration “invite” code.
- For PAM mode, ensure the host/container environment is trusted and properly configured.
- For SSO, configure a dedicated app registration in Microsoft Entra, restrict access appropriately, and consider enabling Conditional Access policies.
- Consider putting this service behind a reverse proxy (nginx, Traefik, etc.) and enabling HTTPS.

## Backup and restore

All persistent application state (users, bookings, SSO settings, registration token) is stored in the SQLite database referenced by `VACATION_DB_PATH`.

- **Docker Compose**
  - The database lives in the `vacation-tracker-data` named volume (mounted at `/data` in the container and typically containing `vacations.db`).
  - To back up:
    - Stop the container.
    - Back up the contents of that volume (e.g. via filesystem-level backup or host-level snapshots).
  - To restore:
    - Recreate the volume from your backup.
    - Start the container again with that volume attached.

- **AWS EC2 (EBS-backed deployments)**
  - Ensure both the application code and the SQLite DB reside on EBS volumes.
  - For backup:
    - Stop the container (or the instance) to quiesce writes.
    - Take EBS snapshots of the relevant volumes on a schedule with a retention policy.
  - For restore:
    - Create new volumes from the latest snapshots.
    - Attach them to a new or existing EC2 instance.
    - Start the container with the restored volume(s).

In all cases, periodically test restoring from backup to ensure that the process and data are valid.
