# Frontier Radar MVP

Frontier Radar is a monorepo MVP that surfaces Texas oil & gas distress and deal activity alerts from production and court signals.

## Stack
- Backend: FastAPI + SQLAlchemy + Alembic + Postgres + APScheduler
- Frontend: Next.js App Router + TypeScript + Tailwind CSS
- Email hook: Resend

## Monorepo Layout
- `backend/` API, schema, migrations, seed script, services
- `frontend/` dashboard, asset detail, watchlist UI

## Backend Setup
1. Create a Postgres database named `frontier_radar`.
2. Copy `backend/.env.example` to `backend/.env` and set values.
3. Install deps:
   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run migration:
   ```bash
   alembic upgrade head
   ```
5. Seed demo data:
   ```bash
   python -m scripts.seed
   ```
6. Start API:
   ```bash
   uvicorn app.main:app --reload
   ```

## Frontend Setup
1. Copy `frontend/.env.example` to `frontend/.env.local`.
2. Install and run:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. Open http://localhost:3000

## API Endpoints
- `GET /alerts`
- `GET /alerts/{id}`
- `GET /assets`
- `GET /assets/{id}`
- `GET /watchlists`
- `POST /watchlists`
- `POST /watchlists/{id}/items`

## Demo Data Included
- 10 operators
- 25 assets
- 50 production records
- 5 court cases
- 20 docket entries
- 30 alerts
- 2 watchlists

## Notes
- Each alert stores a source URL for traceability.
- Scheduled signal evaluation hook is wired through APScheduler and ready for live-ingestion extensions.
- App is fully usable with seed data when external feeds are unavailable.
