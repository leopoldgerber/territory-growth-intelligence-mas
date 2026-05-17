# Backup Restore

## Backup

```bash
make backup-db
```

Backups are written to `backups/`.

## Restore outline

1. Stop application traffic.
2. Restore PostgreSQL dump into target database.
3. Restore uploaded files from storage backup.
4. Run migrations if schema is behind.
5. Run health checks.
6. Validate login, upload, reports, and workflow endpoints.
