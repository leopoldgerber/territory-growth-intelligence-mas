$ErrorActionPreference = 'Stop'

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$backupDir = Join-Path $PSScriptRoot '..\backups'
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

$postgresDb = if ($env:POSTGRES_DB) { $env:POSTGRES_DB } else { 'tgi_db' }
$postgresUser = if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { 'tgi_user' }
$outputPath = Join-Path $backupDir "postgres_$timestamp.sql"

docker compose exec -T postgres pg_dump -U $postgresUser $postgresDb | Out-File -FilePath $outputPath -Encoding utf8

Write-Output "Backup created: $outputPath"
