# Frontier Radar MVP

This repository contains Frontier Radar, an MVP focused on surfacing Texas oil & gas distress signals with full source traceability.

## Backend (FastAPI) local setup

### Backend folder structure
```text
backend/
  app/
    api/
      alerts.py
      assets.py
      watchlists.py
    core/
      config.py
    db/
      base.py
      session.py
    models/
      entities.py
    schemas/
      common.py
    services/
      alerts.py
      assets.py
      signals.py
      watchlists.py
    main.py
  alembic/
    versions/
      0001_init.py
    env.py
  scripts/
    seed.py
  alembic.ini
  requirements.txt
```

### 1) Prerequisites
- Python 3.10+
- Postgres 14+
- Database named `frontier_radar`

### 2) Configure environment
```bash
cp backend/.env.example backend/.env
```

### 3) Install dependencies
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4) Run migrations
```bash
alembic upgrade head
```

### 5) Load seed/demo data
```bash
python -m scripts.seed
```

### 6) Start API
```bash
uvicorn app.main:app --reload
```

### 7) Verify
- Health: `GET http://localhost:8000/health`
- Alerts: `GET http://localhost:8000/alerts`

## Backend API endpoints
- `GET /alerts`
- `GET /alerts/{id}`
- `GET /assets`
- `GET /assets/{id}`
- `GET /watchlists`
- `POST /watchlists`
- `POST /watchlists/{id}/items`

## Alert filtering support
`GET /alerts` supports:
- `county`
- `operator`
- `alert_type`
- `severity`
- `start_date` (YYYY-MM-DD)
- `end_date` (YYYY-MM-DD)

## Notes
- Seed script loads demo records for all core models so the backend is usable with no external ingestion.
- Each court case, docket entry, and alert record stores a `source_url` for traceability.
- APScheduler runs signal-generation service hooks on startup intervals.
