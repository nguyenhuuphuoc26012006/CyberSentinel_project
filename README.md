# CyberSentinel

Independent SIEM learning project: Flask + React/TypeScript + PostgreSQL + Redis.

## Requirements
- Windows 10/11
- Docker Desktop with Linux containers
- Git (optional)

## Run on Windows
1. Copy `.env.example` to `.env`.
2. Open PowerShell in this directory.
3. Run `docker compose up --build`.
4. Open:
   - Frontend: http://localhost:5173
   - Backend health: http://localhost:5000/api/health
   - Events API: http://localhost:5000/api/events
5. Stop with `Ctrl+C`, then `docker compose down`.

To reset local database data: `docker compose down -v` (deletes PostgreSQL and Redis volumes).

## Demo: create a failed-login event
PowerShell:
```powershell
$body = @{
  source = "lab-simulator"
  event_type = "login_failure"
  source_ip = "192.0.2.10"
  username = "admin"
  severity = "low"
  message = "Simulated failed login"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:5000/api/events" -ContentType "application/json" -Body $body
```
Send 5 events from the same IP within 5 minutes to trigger the starter Brute Force rule.
Use documentation-only TEST-NET IPs such as 192.0.2.10; do not target real systems.

## Current scope
This is the runnable foundation and first detection rule, not a production SIEM. Authentication, ingestion agents, durable queue workers, RBAC, migrations, retention policies, and hardened deployment are later phases.
