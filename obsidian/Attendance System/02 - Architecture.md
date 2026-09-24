# 02 - Architecture

[[00 - Project Overview|⬅️ Hub]] | [[01 - Requirements|Requirements ⬅️]] | [[03 - Hardware|Hardware ➡️]]

**Status:** Selected architecture; service behavior remains planned.

ESP32 + AS608 performs the planned match at the edge. A local FastAPI/SQLite service validates device events and serves a same-origin vanilla web dashboard. LittleFS queue/replay is planned. The optional local assistant is deferred and read-only. No product application code exists yet.

- [Canonical architecture and trust boundaries](../../docs/architecture.md)
- [Interactive Canvas](Architecture.canvas)
- [Architecture diagram](../../diagrams/architecture.mmd)
