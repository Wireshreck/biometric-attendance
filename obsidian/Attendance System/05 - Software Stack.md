# 05 - Software Stack

[[00 - Project Overview|⬅️ Hub]] | [[04 - Bill of Materials|BOM ⬅️]] | [[06 - Firmware Plan|Firmware ➡️]]

**Status:** Toolchain/dependency selections exist; product layers are not implemented.

PlatformIO + Arduino for ESP32; Python 3.13 + FastAPI/Uvicorn/Pydantic/aiosqlite + SQLite; static HTML/CSS/ES modules, no Node build. Local HTTP is for synthetic demo data on an isolated network only. SSE is planned for live updates. AI is optional/deferred.

- [Stack decisions and implementation state](../../docs/software-stack.md)
- [Dependency inventory](../../docs/dependencies.md)
- [Environment setup](../../docs/environment.md)
