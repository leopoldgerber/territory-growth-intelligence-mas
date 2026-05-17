# Database Migrations

## Local commands

```bash
make migrate
make migrate-current
make migrate-history
```

## Safety rules

- Run migrations before exposing new backend code.
- Take a backup before destructive schema changes.
- Prefer backward-compatible migrations.
- Validate `docker compose config --quiet` before deploy.
