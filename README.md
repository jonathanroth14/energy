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
      bankruptcy_base.py
      courtlistener_bankruptcy.py
      bankruptcy_normalize.py
      bankruptcy_service.py
    models/
    schemas/
    services/
      signals.py
      bankruptcy_signals.py
    main.py
  alembic/
    versions/
      0001_init.py
      0002_ingestion_traceability.py
      0003_bankruptcy_traceability.py
  scripts/
    seed.py
    run_ingestion.py
    run_bankruptcy_ingestion.py
    data/sample_rrc_production.csv
    data/sample_courtlistener_cases.json
    data/sample_courtlistener_dockets.json
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

### 6) Run production ingestion manually
```bash
python -m scripts.run_ingestion --source-url "$RRC_PRODUCTION_SOURCE_URL"
```

### 7) Run bankruptcy ingestion manually (CourtListener / RECAP-compatible)
```bash
python -m scripts.run_bankruptcy_ingestion \
  --cases-source "$COURTLISTENER_CASES_SOURCE_URL" \
  --dockets-source "$COURTLISTENER_DOCKETS_SOURCE_URL"
```

Local sample JSON option:
```bash
python -m scripts.run_bankruptcy_ingestion \
  --cases-source "file://$(pwd)/scripts/data/sample_courtlistener_cases.json" \
  --dockets-source "file://$(pwd)/scripts/data/sample_courtlistener_dockets.json"
```

### 8) Start API
```bash
uvicorn app.main:app --reload
```

## Ingestion notes
- Source adapters are modular under `app/ingestion/*` so PACER-compatible sources can be added later.
- Bankruptcy ingestion currently assumes CourtListener-style JSON payloads with `results` arrays and stable IDs.
- Ingestion jobs are re-runnable/idempotent through external-id upserts and update semantics.
- Traceability is stored for every case/docket via `source_url`, `source_provider`, and `source_metadata`.
- Logging covers successful fetches, parse failures, and partial normalization failures.

## Signals implemented
- **Production collapse**: latest full month output down `>= 40%` vs trailing 3-month average.
- **Inactivity / shut-in proxy**: no production reports for `2+` consecutive periods after prior production history.
- **New bankruptcy filing**: Chapter 11/7 case creation.
- **Asset sale motion keyword hit**: docket text contains 363/sale-motion/APA/stalking-horse/bid-procedure terms.
- **Watchlist bankruptcy match**: normalized debtor names match watched operator entities.

## Backend API endpoints
- `GET /alerts`
- `GET /alerts/{id}`
- `GET /assets`
- `GET /assets/{id}`
- `GET /watchlists`
- `POST /watchlists`
- `POST /watchlists/{id}/items`
