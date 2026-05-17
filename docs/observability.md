# Observability

## Health endpoints

- `GET /api/health`
- `GET /api/health/live`
- `GET /api/health/ready`
- `GET /api/health/metrics`

## Logging

Backend logs are structured JSON logs with:

- `request_id`
- `job_id`
- `project_id`
- `user_id`
- `duration_ms`

## Metrics

Prometheus-style metrics are exposed through `/api/health/metrics`.

Current baseline:

- request count
- request latency histogram

## Error tracking

Set `SENTRY_DSN` to enable Sentry for FastAPI exceptions.
