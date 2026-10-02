---
type: project-navigation
status: IN PROGRESS
updated: 2026-09-29
---

# 02 - Architecture

[[00 - Project Overview|⬅️ Hub]] | [[01 - Requirements|Requirements ⬅️]] | [[03 - Hardware|Hardware ➡️]]

**Status:** IN PROGRESS — backend vertical slice is tested; firmware attendance/enrollment/API/queue workflows are implemented and buildable, but physical integration remains unverified. Frontend, reports/CSV/SSE remain planned.

ESP32 + R307S matching is implemented at the firmware boundary; owner-reported R307S wiring returned zero response bytes and its rail/TX level is unverified, so physical use is not established. Firmware stores an event UUID/slot/time in LittleFS before posting the existing authenticated FastAPI/SQLite contract, and retries with stable UUIDs. Backend implements student slot reservation/enrollment completion and attendance idempotency/60-second suppression. Browser dashboard/reports are planned. The optional local assistant is deferred and read-only. No complete physical workflow is verified.

- [Canonical architecture and trust boundaries](../../docs/architecture.md)
- [Interactive Canvas](Architecture.canvas)
- [Architecture diagram](../../diagrams/architecture.mmd)
