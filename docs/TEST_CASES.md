# Ten sample test cases (manual + automated)

| # | Scenario | Steps | Expected |
|---|----------|-------|----------|
| 1 | Health check | `GET /health` | `200`, `{"status":"ok"}` |
| 2 | Seeker registration | `POST /api/v1/auth/register` with role `seeker` | `200`, user object |
| 3 | Login JWT | `POST /api/v1/auth/login` | `200`, `access_token` present |
| 4 | Search filters | `GET /api/v1/search/properties?city=Karachi&min_bedrooms=2` | `items` array, `total` count |
| 5 | Owner listing cap | Owner without plan creates 4th pending+approved listing | `403` when over limit |
| 6 | Admin approve | `POST /admin/properties/{id}/moderate` body `{"status":"approved"}` | Owner gets notification |
| 7 | Mock subscription | Owner `POST /subscriptions/subscribe` with `use_mock_payment: true` | Transaction `completed` |
| 8 | Chat thread | Seeker `POST /messages` to owner for a property | Message stored; WS `join` receives pushes |
| 9 | File upload | `POST /upload` multipart with Bearer token | JSON with `url` |
| 10 | Analytics | Admin `GET /analytics/summary` | Counts and `revenue_completed_total` |

Automated counterparts live in `backend/tests/test_api.py` (subset runs without Mongo via `REALSTAT_SKIP_DB_INIT`).
