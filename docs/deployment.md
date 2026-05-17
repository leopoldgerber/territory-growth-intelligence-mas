# Deployment

## Production baseline

Production compose is defined in `docker-compose.prod.yml`.

Services:

- `postgres`
- `redis`
- `backend`
- `worker`
- `beat`
- `frontend`
- `nginx`

## Startup

```bash
make prod-up-build
```

## Shutdown

```bash
make prod-down
```

## Post-deploy checks

```bash
make health-live
make health-ready
make health-metrics
```
