# Build context is the REPO ROOT (compose: build.context "."), so data/seed.sql can be copied in.
# Exact patch tag (PLAN.md Task 5) so builds are reproducible.
FROM python:3.13.18-slim

# No .pyc files in the image; unbuffered stdout so `docker compose logs` shows output live.
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Mirror the repo layout (/srv/backend + /srv/data): app/seed.py resolves its default seed path as
# <repo root>/data/seed.sql, so no env var or code change is needed.
WORKDIR /srv/backend

# Requirements first so the dependency layer is cached across code changes.
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/alembic.ini ./
COPY backend/migrations ./migrations
COPY backend/app ./app
COPY backend/docker-entrypoint.sh ./
COPY data/seed.sql /srv/data/seed.sql

EXPOSE 8000
# Invoked via sh so the executable bit does not matter on the host checkout.
CMD ["sh", "docker-entrypoint.sh"]
