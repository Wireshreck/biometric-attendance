---
type: project-navigation
status: PLANNED
updated: 2026-09-25
---

# 02 - Architecture

[[00 - Project Overview|⬅️ Hub]] | [[01 - Requirements|Requirements ⬅️]] | [[03 - Hardware|Hardware ➡️]]

**Status:** PLANNED — architecture is documented; service behavior remains unimplemented.

ESP32 + AS608 performs the planned match at the edge. A local FastAPI/SQLite service validates device events and serves a same-origin vanilla web dashboard. LittleFS queue/replay is planned. The optional local assistant is deferred and read-only. No product application code exists yet.

- [Canonical architecture and trust boundaries](../../docs/architecture.md)
- [Interactive Canvas](Architecture.canvas)
- [Architecture diagram](../../diagrams/architecture.mmd)
