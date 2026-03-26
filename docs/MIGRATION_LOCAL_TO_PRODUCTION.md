# Migration: local → production

1. **Database**: Export local Mongo (`mongodump`) or re-seed Atlas; set `MONGODB_URI` to Atlas SRV string; run API once to create indexes (startup `ensure_indexes`).
2. **Secrets**: Generate strong `JWT_SECRET_KEY`; never commit `.env`.
3. **Media**: Set `STORAGE_MODE=s3`, provide `AWS_*` bucket in same region; set `PUBLIC_MEDIA_BASE_URL` to CloudFront or bucket website URL.
4. **CORS**: Set `CORS_ORIGINS` to your SPA origin(s) only.
5. **HTTPS**: Terminate TLS at load balancer or reverse proxy (Caddy/NGINX); WebSockets require `wss://`.
6. **Stripe**: Set `STRIPE_SECRET_KEY` live key; implement client Payment Element; set `use_mock_payment: false`; configure webhook for subscription lifecycle.
7. **Frontend**: Build with `VITE_API_URL=https://api.yourdomain.com/api/v1`; deploy static assets to S3+CloudFront or Vercel.
8. **Jobs**: Schedule `POST /api/v1/subscriptions/system/auto-renew-run` behind an internal API key or VPC-only cron.
9. **Monitoring**: Add structured logging, health checks, and optional Sentry/OpenTelemetry.
