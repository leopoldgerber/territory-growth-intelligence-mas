# Runbook

## Service unhealthy

1. Check `make health-live`.
2. Check `make health-ready`.
3. Review backend, worker, and postgres logs.
4. Confirm migrations are applied.

## Database restore

1. Stop the stack.
2. Restore PostgreSQL dump.
3. Restore uploaded files.
4. Start stack and run health checks.

## Worker backlog

1. Check Redis and worker logs.
2. Inspect queue size.
3. Restart worker if heartbeat is stale.

## Upload failures

1. Check file registration in upload history.
2. Review quality checks.
3. Review ingestion logs for report type and row counts.
