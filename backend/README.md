# Backend Service Plan

**Status:** IN PROGRESS — schema/migrations plus a tested FastAPI vertical slice are implemented: health, admin student list/create/read/deactivate, device-scoped enrollment assignment/completion, and authenticated attendance ingestion with UUID idempotency and the 60-second duplicate rule. Reports, device management/heartbeat, cleanup/deletion, CSV, SSE, static dashboard, and firmware integration are not implemented.

## Selected runtime

Python 3.13 on Windows, FastAPI, Uvicorn, Pydantic, aiosqlite, SQLite WAL. Serving the planned vanilla frontend from FastAPI is not implemented. AI is optional and deferred. Dependency manifests: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`.

## Current and planned module layout

```text
backend/
  app/
    database.py             # implemented SQLite connections, pragmas, migrations
    main.py                 # implemented app factory, health and MVP routes
    config.py               # implemented environment settings and fail-fast validation
    auth.py                 # implemented admin and per-device auth dependencies
    dependencies.py         # implemented request-scoped DB/settings dependencies
    schemas.py              # implemented bounded Pydantic request/response models
    provision_device.py     # implemented one-time local device provisioning CLI
    migrations/             # implemented schema v1; add ordered follow-up SQL
  data/                     # runtime database (ignored by Git)
  tests/                    # migration/constraint tests and API vertical-slice tests
```

Keep business rules in services/transactions, parameterize SQL, validate inputs at the boundary, and avoid a second ORM/framework for the small local workload.

## Setup and current verification

```powershell
cd C:\Users\user\projects\fair\biometric-attendance\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python test_env.py
python -m pytest tests
```

`test_env.py` verifies environment dependencies and SQLite basics. Pytest covers migrations/constraints and the implemented API slice. Configuration template: `.env.example`; `app.config` reads `backend/.env`; `.env` is ignored. The app refuses to start unless the admin username/password are configured; use a unique password of at least 16 characters and synthetic data only.

With `.env` configured, launch with `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`; `/health` and `/docs` are available locally. After confirming capacity from the exact sensor, provision the device in PowerShell:

```powershell
$verifiedCapacity = Read-Host "Enter the capacity verified for this sensor"
python -m app.provision_device --name "Demo terminal" --location "Lab" --sensor-capacity $verifiedCapacity
```

Save the one-time printed bearer token only in ignored local firmware configuration. For an ESP32 on an isolated demo network, bind to the laptop's LAN interface only as needed, apply host firewall rules, and use synthetic data because the MVP HTTP transport is unencrypted.

## Implementation order

1. **Implemented:** settings, health, DB connection/migrations, admin/device authentication, one-time local device provisioning.
2. **Implemented:** student creation/list/read/deactivation, slot reservation and device enrollment completion.
3. **Implemented and API-tested:** atomic event ingest, UUID replay, active-slot resolution and 60-second duplicate suppression.
4. **Next:** report/date queries, CSV-safe export, authenticated SSE, device status/heartbeat, deletion/cleanup flows.
5. Static same-origin dashboard serving, explicit body limits, browser integration, and device/firmware contract.
6. Keep tests database-backed and synthetic; the existing API tests do not verify physical enrollment or firmware-to-API networking.

Initial device provisioning is a local-only CLI action: generate a high-entropy token, store only its hash and device metadata, print the raw token once for local firmware configuration, and never expose a route that returns it again. Student creation binds the slot to the sole active MVP device; multi-device enrollment remains deferred.

Contract: [API plan](../docs/api-plan.md). Data model: [database plan](../docs/database-plan.md). Privacy boundary: [privacy/security](../docs/privacy-security.md).
