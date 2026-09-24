# Software Stack

**Status:** Selected tooling; application implementation is pending. Exact dependency sources are [PlatformIO config](../firmware/platformio.ini), [Python pyproject](../backend/pyproject.toml), and [requirements files](../backend/requirements.txt). See [dependency inventory](dependencies.md).

| Layer | Selected technology | Current state |
| --- | --- | --- |
| Firmware | PlatformIO, `espressif32@6.5.0`, Arduino on ESP32-WROOM-32-class board | Toolchain-check sketch only; libraries pinned in config |
| Sensor/display/RTC | Adafruit fingerprint, SSD1306/GFX, RTClib | Dependency declarations only; no product firmware |
| Offline storage | ESP32 LittleFS | Build setting only; queue unimplemented |
| Device transport | Local HTTP JSON, per-device bearer credential | Planned; no TLS; synthetic demo data only |
| Backend | Python 3.13, FastAPI, Uvicorn, Pydantic, aiosqlite | Venv/metadata/environment smoke script; no app |
| Database | Standard SQLite in Python, WAL | Schema is planned only |
| UI | Static semantic HTML/CSS/ES modules | No UI files or Node tooling |
| Live updates | Authenticated Server-Sent Events + REST `fetch()` | API/UI plan only; meets stated update target if verified |
| Optional reporting assistant | Local LLM via allowlisted read-only API tools | Deferred; core does not depend on it |

## Design rationale and limits

- Keep the science-fair system local and dependency-light; no cloud service or frontend build pipeline is required.
- SQLite is suitable for this single-host/small-write prototype; WAL allows readers during writes but does not turn SQLite into a multi-writer server database.
- Do not assume separate ESP32 cores/tasks until firmware code and timing tests establish the need. The current sketch has no concurrent tasks.
- HTTP over a LAN is not end-to-end encrypted. Limit the MVP to synthetic data and an isolated demo network; production needs a reviewed TLS/key-provisioning and admin-identity design.
- Optional AI must be off by default, read-only, local, bounded to approved reports, and clearly label model-generated explanation separately from database facts.

No React/Vue, Node runtime, Docker, cloud AI SDK, ORM, migration package, or chart library is currently required. Revisit only when a concrete need appears.
