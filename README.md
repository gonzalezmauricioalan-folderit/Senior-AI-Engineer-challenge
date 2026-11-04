# Relay: "is this week's activity normal for us?" (DASH-247)

## Run it

Prerequisites: Docker with compose v2, and free ports 5432 (db), 8000 (api) and 8080 (web).

```bash
docker compose up -d --build --wait    # db + api + web; the api migrates and seeds itself
```

- Dashboard: http://localhost:8080
- API: http://localhost:8000 (health check: http://localhost:8000/health, docs: http://localhost:8000/docs)

Reset to a clean database:

```bash
docker compose down -v && docker compose up -d --build --wait
```

The full write-up (stack, decisions, assumptions, tests) is coming in Task 13.
