# Frontier Radar (Demo-Ready MVP)

Frontier Radar is a demo-friendly MVP for surfacing Texas oil & gas distress signals across production and bankruptcy data.

## Quick Start (local, ~5 minutes)

### 1) Start Postgres
Create a DB named `frontier_radar`.

### 2) Backend setup
```bash
cp backend/.env.example backend/.env
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload
```
Backend URL: `http://localhost:8000`

### 3) Frontend setup
```bash
cd ../frontend
cp .env.example .env.local
npm install
npm run dev
```
Frontend URL: `http://localhost:3000`

> The UI is intentionally marked **Demo Mode** and is pre-populated by realistic seeded data.

---

## Demo data scenarios included
Seeding creates believable walk-through scenarios for:
- Production collapse
- Inactivity / shut-in proxy
- New bankruptcy filing (including Chapter 11)
- Asset sale motion keyword hit (`363`, `sale motion`, `APA`, etc.)
- Watchlist-triggered debtor/operator name match

All seeded alerts include source links and can be opened from alert cards via **View alert**.

## Optional ingestion commands
### Production ingestion (RRC source)
```bash
cd backend
python -m scripts.run_ingestion --source-url "$RRC_PRODUCTION_SOURCE_URL"
```

### Bankruptcy ingestion (CourtListener-compatible)
```bash
cd backend
python -m scripts.run_bankruptcy_ingestion \
  --cases-source "$COURTLISTENER_CASES_SOURCE_URL" \
  --dockets-source "$COURTLISTENER_DOCKETS_SOURCE_URL"
```

### Local sample bankruptcy payloads
```bash
cd backend
python -m scripts.run_bankruptcy_ingestion \
  --cases-source "file://$(pwd)/scripts/data/sample_courtlistener_cases.json" \
  --dockets-source "file://$(pwd)/scripts/data/sample_courtlistener_dockets.json"
```

## API endpoints (MVP)
- `GET /alerts`
- `GET /alerts/{id}`
- `GET /assets`
- `GET /assets/{id}`
- `GET /watchlists`
- `POST /watchlists`
- `POST /watchlists/{id}/items`
