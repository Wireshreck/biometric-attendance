# 07 - Backend Plan

[[00 - Project Overview|⬅️ Hub]] | [[06 - Firmware Plan|Firmware ⬅️]] | [[08 - Database Plan|Database ➡️]]

**Status:** Python environment and dependencies are present; there is no FastAPI app entry point or product test suite.

Planned service: `/api/v1`, environment-backed configuration, aiosqlite, SQLite migrations/WAL, device/admin auth, student enrollment state, idempotent attendance ingest, reports/CSV, authenticated SSE and static dashboard serving. Local HTTP limits the prototype to synthetic data on an isolated WLAN.

- [Backend layout and implementation order](../../backend/README.md)
- [API contract](../../docs/api-plan.md)
- [Database design](../../docs/database-plan.md)
