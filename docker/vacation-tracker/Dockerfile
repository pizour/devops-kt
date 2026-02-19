FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libpam0g-dev \
      libpam-modules \
      libpam-modules-bin \
      libpam-runtime \
      python3-pam && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY pam-vacation-tracker /etc/pam.d/vacation-tracker
WORKDIR /app/backend

ENV FLASK_SECRET_KEY=change-me
ENV VACATION_DB_PATH=/data/vacations.db

VOLUME ["/data"]

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:create_app()"]
