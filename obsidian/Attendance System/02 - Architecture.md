---
type: project-navigation
status: PLANNED
updated: 2026-09-25
---

# 02 - Architecture

[[00 - Project Overview|⬅️ Hub]] | [[01 - Requirements|Requirements ⬅️]] | [[03 - Hardware|Hardware ➡️]]

**Status:** IN PROGRESS — architecture is documented; the backend implements a tested health/student/enrollment/attendance API slice. Firmware, frontend, reports/SSE, and integrated service behavior remain incomplete.

ESP32 + AS608 is planned to perform matching at the edge. The local FastAPI/SQLite service currently supports authenticated student slot reservation/enrollment completion and synthetic attendance ingestion with idempotency and the 60-second duplicate policy. A same-origin vanilla dashboard and LittleFS queue/replay are planned. The optional local assistant is deferred and read-only. No terminal or full product workflow is verified.

- [Canonical architecture and trust boundaries](../../docs/architecture.md)
- [Interactive Canvas](Architecture.canvas)
- [Architecture diagram](../../diagrams/architecture.mmd)
