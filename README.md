# RealStat — Multi-role rental platform

React + Redux Toolkit + Tailwind frontend, FastAPI + MongoDB backend, WebSocket chat, mock subscriptions (Stripe-ready), Docker compose for local runs.

## Quick start (local)

1. **MongoDB**  
   - Install locally or run: `docker compose up -d mongo` from this folder.

2. **Backend**  
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Seed sample data** (optional)  
   ```bash
   cd backend
   python scripts/seed_mongo.py
   ```  
   Demo logins: `owner@demo.com` / `password123`, `seeker@demo.com` / `password123`, `admin@demo.com` / `admin12345`.

4. **Frontend**  
   ```bash
   cd frontend
   copy .env.example .env
   npm install
   npm run dev
   ```  
   Open `http://127.0.0.1:5173` (or `localhost:5173`). API calls use the Vite proxy to `127.0.0.1:8000` so you avoid “Failed to fetch” from localhost vs 127.0.0.1 mismatches. Keep the **backend running** on port 8000.

## Docker (API + Mongo + SPA)

```bash
docker compose up --build
```

- API: `http://localhost:8000`  
- SPA (nginx): `http://localhost:5173` (proxies `/api/*` to the API)  
- WebSocket from the browser still uses `ws://localhost:8000` (see `VITE_WS_URL`).

After containers are up, run the seed script against the compose Mongo URI:

```bash
cd backend
set MONGODB_URI=mongodb://localhost:27017
python scripts/seed_mongo.py
```

## Tests and Postman

- Pytest: `cd backend && pytest` (uses `REALSTAT_SKIP_DB_INIT` from `tests/conftest.py` so Mongo is optional).  
- Full API integration: start Mongo, unset `REALSTAT_SKIP_DB_INIT`, run `pytest`.  
- Postman: `postman/RealStat.postman_collection.json`.

## Docs in this repo

- `docs/MONGODB_SCHEMA.md` — collections and sample documents  
- `docs/TEST_CASES.md` — ten manual test scenarios  
- `docs/MOCKUPS.md` — Figma/AI-friendly layout spec  
- `docs/MIGRATION_LOCAL_TO_PRODUCTION.md` — Atlas, S3, Stripe, TLS

## Production notes

- Set `JWT_SECRET_KEY`, `MONGODB_URI` (Atlas), `CORS_ORIGINS`, `STORAGE_MODE=s3`, Stripe keys.  
- Build frontend with `VITE_API_URL` pointing at the public API URL.  
- Serve HTTPS and use `wss://` for chat.
