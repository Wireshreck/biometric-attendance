---
type: project-navigation
status: IN PROGRESS
updated: 2026-09-25
---

# 07 - Backend Plan

[[00 - Project Overview|⬅️ Hub]] | [[06 - Firmware Plan|Firmware ⬅️]] | [[08 - Database Plan|Database ➡️]]

**Status:** IN PROGRESS — schema/migrations and a tested API vertical slice now exist: health, admin student management/slot reservation/deactivation, device enrollment assignment/completion, and attendance ingestion with idempotency and duplicate suppression. Remaining planned endpoints and physical/firmware integration are not implemented.

Planned service: `/api/v1`, environment-backed configuration, aiosqlite, SQLite migrations/WAL, device/admin auth, student enrollment state, idempotent attendance ingest, reports/CSV, authenticated SSE and static dashboard serving. Local HTTP limits the prototype to synthetic data on an isolated WLAN.

- [Backend layout and implementation order](../../backend/README.md)
- [API contract](../../docs/api-plan.md)
- [Database design](../../docs/database-plan.md)
