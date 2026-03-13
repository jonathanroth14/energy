# Frontier Radar MVP

This repository contains Frontier Radar, an MVP focused on surfacing Texas oil & gas distress signals with full source traceability.

## Backend (FastAPI) local setup

### Backend folder structure
```text
backend/
  app/
    api/
    core/
    db/
    ingestion/
      base.py
      rrc_production.py
      normalize.py
      service.py
    models/
    schemas/
    services/
      alerts.py
      assets.py
      signals.py
      watchlists.py
    main.py
  alembic/
    versions/
      0001_init.py
      0002_ingestion_traceability.py
  scripts/
    seed.py
    run_ingestion.py
    data/sample_rrc_production.csv
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

### 6) Run ingestion manually (official RRC source)
```bash
python -m scripts.run_ingestion --source-url "$RRC_PRODUCTION_SOURCE_URL"
```

Local demo CSV option:
```bash
python -m scripts.run_ingestion --source-url "file://$(pwd)/scripts/data/sample_rrc_production.csv"
```

### 7) Start API
```bash
uvicorn app.main:app --reload
```

## Ingestion notes
- The ingestion module is source-adapter based (`app/ingestion/*`) so additional providers can be added without changing normalization code.
- Normalization is idempotent by upserting operators/assets and updating/inserting production records by `(asset_id, period_date)`.
- Traceability fields are persisted (`source_url`, `source_record_id`, `source_metadata`) on normalized production records, with source metadata also stored on operators and assets.
- Logging includes successful fetches, parse failures, and partial normalization failures.

## Signals implemented
- **Production collapse**: latest full month output down `>= 40%` vs trailing 3-month average.
- **Inactivity / shut-in proxy**: no production reports for `2+` consecutive periods after prior production history.

## Backend API endpoints
- `GET /alerts`
- `GET /alerts/{id}`
- `GET /assets`
- `GET /assets/{id}`
- `GET /watchlists`
- `POST /watchlists`
- `POST /watchlists/{id}/items`
