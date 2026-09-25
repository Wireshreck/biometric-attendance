---
type: project-navigation
status: PLANNED
updated: 2026-09-25
---

# 05 - Software Stack

[[00 - Project Overview|⬅️ Hub]] | [[04 - Bill of Materials|BOM ⬅️]] | [[06 - Firmware Plan|Firmware ➡️]]

**Status:** PLANNED — toolchain/dependency selections exist; application layers are not implemented.

PlatformIO + Arduino for ESP32; Python 3.13 + FastAPI/Uvicorn/Pydantic/aiosqlite + SQLite; static HTML/CSS/ES modules, no Node build. Local HTTP is for synthetic demo data on an isolated network only. SSE is planned for live updates. AI is optional/deferred.

- [Stack decisions and implementation state](../../docs/software-stack.md)
- [Dependency inventory](../../docs/dependencies.md)
- [Environment setup](../../docs/environment.md)
