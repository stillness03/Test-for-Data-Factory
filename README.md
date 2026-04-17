## How to launch a project
```bash
git clone (https://github.com/stillness03/Test-for-Data-Factory)
cd Test-for-Data-Factory
```

Don't forget created .env (.env.example)

```bash
docker-compose up --build
```

## Project Structure
- app/ — the main application code.
- init_db.sql — database dump (schema + initial data).
- migrations/ — Alembic migration history.
- docker-compose.yml — container configuration.
- entrypoint.sh — startup automation script (waiting for the database and migrations).

