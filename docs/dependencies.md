# Dependency Inventory

Manifest sources of truth: `firmware/platformio.ini`, `backend/pyproject.toml`, `backend/requirements.txt`, and `backend/requirements-dev.txt`. Product code is not implemented; current imports/build references are environment/toolchain checks.

| Name | Pinned version/range | Used for | Required? | Install/verification | License note |
| --- | --- | --- | --- | --- | --- |
| PlatformIO Core | Host tool; audit recorded 6.2.0 | Resolve/build/upload firmware | Required for firmware dev | `python -m pip install platformio`; `pio --version`, `pio run` | PlatformIO Core license applies; inspect upstream terms before redistribution |
| `espressif32` platform | 6.5.0 | ESP32 board/framework/toolchain | Required firmware | PlatformIO `pio run` | Platform/package component terms; review upstream metadata |
| Arduino framework | Selected by PlatformIO platform | Firmware API | Required firmware | Bundled/resolved by PlatformIO | Upstream framework license |
| Adafruit Fingerprint Sensor Library | 2.1.3 | AS608 UART/enrollment/match commands | Planned required firmware | `pio run`, then physical sensor test | Adafruit library license; preserve notices if redistributing |
| Adafruit SSD1306 | 2.5.9 | OLED driver | Planned required firmware | `pio run` and display bench test | Adafruit library license |
| Adafruit GFX | 1.11.9 | OLED graphics dependency | Planned required firmware | Resolved as direct dependency; `pio run` | Adafruit library license |
| RTClib | 2.1.3 | DS3231 access | Planned required firmware | `pio run` and RTC bench test | Adafruit library license |
| ArduinoJson | 7.0.4 | JSON event encode/decode | Planned required firmware | `pio run` and payload tests | Benoit Blanchon library license; review upstream terms |
| Python | 3.13.15 in audited host; project requires >=3.11 | Backend/runtime scripts | Required backend | `python --version` | Python PSF license |
| FastAPI | 0.115.0 | HTTP API/static serving | Planned required backend | `pip install -r requirements.txt` | Upstream MIT metadata |
| Uvicorn | 0.31.0 `[standard]` | ASGI server | Planned required backend | Same; `uvicorn --version` | Upstream BSD metadata |
| Pydantic | 2.9.2 | Request/response validation | Planned required backend | Same; import check | Upstream MIT metadata |
| aiosqlite | 0.20.0 | Async SQLite access | Planned required backend | Same; import check | Upstream MIT metadata |
| tzdata | 2026.4 | IANA timezone database fallback; needed for portable `ZoneInfo` on Windows | Planned required backend | Pinned in manifests; test `ZoneInfo("Asia/Kolkata")` | Upstream Apache-2.0 metadata |
| HTTPX | 0.27.2 | API test client | Development only | `pip install -r requirements-dev.txt` | Upstream BSD metadata |
| pytest | 8.3.3 | Backend test runner | Development only | `pytest` after tests exist | Upstream MIT metadata |
| pytest-asyncio | 0.24.0 | Async pytest support | Development only | Same | Upstream Apache-2.0 metadata |

The versions above match checked-in manifests. Verify upstream package metadata/license notices during dependency updates; this inventory is not a legal determination. No multipart upload is planned, so `python-multipart` was removed. No Node/React/Vite, Docker, ORM, chart library, cloud AI SDK, or PDF package is required for MVP.

## Clean install

```powershell
# Firmware (from a shell where Python/pip is available)
python -m pip install platformio
cd C:\Users\user\projects\fair\biometric-attendance\firmware
pio run

# Backend
cd ..\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python test_env.py
```

The last command validates dependencies and basic SQLite behavior only; it does not test the unimplemented backend.
