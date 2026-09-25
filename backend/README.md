# Backend Service Plan

**Status:** IMPLEMENTED / VERIFIED — SQLite schema v1 and transactional migration/connection setup in `app/database.py` and `migrations/`; six migration/constraint tests pass. There is no `app/main.py`, router, authentication, or API behavior. `test_env.py` is an environment smoke check.

## Selected runtime

Python 3.13 on Windows, FastAPI, Uvicorn, Pydantic, aiosqlite, SQLite WAL. Vanilla frontend is served by FastAPI. AI is optional and deferred. Dependency manifests: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`.

## Current and planned module layout

```text
backend/
  app/
    database.py             # implemented SQLite connections, pragmas, migrations
    main.py                 # planned lifespan, health, static mount
    config.py               # environment settings, fail-fast validation
    auth.py                 # admin and per-device auth dependencies
    schemas.py              # Pydantic request/response models
    routers/                # students, attendance, reports, devices, SSE
    services/               # enrollment state, idempotency/60s duplicate policy
    migrations/             # implemented schema v1; add ordered follow-up SQL
  data/                     # runtime database (ignored by Git)
  tests/                    # migration/constraint tests; API tests planned
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

`test_env.py` verifies environment dependencies only. The pytest suite currently verifies DB migrations/constraints; no routes exist yet. Configuration template: `.env.example`; `.env` is ignored. The future app should fail fast when credentials are empty outside explicit development mode.

After `app/main.py` and routes exist, intended launch is `uvicorn app.main:app --host 127.0.0.1 --port 8000`. For an ESP32 on an isolated demo network, bind to the laptop's LAN interface or `0.0.0.0` only as needed, apply host firewall rules, and use synthetic data because the MVP HTTP transport is unencrypted.

## Implementation order

1. Settings, health endpoint, database connection/pragmas and versioned schema.
2. Device/admin authentication and synthetic device provisioning.
3. Student creation/enrollment state, then transactional attendance ingest with event UUID and 60-second behavior.
4. Reports, CSV-safe export, admin audit actions, authenticated SSE with resume cursor.
5. Static mount and CORS disabled/same-origin; explicit request limits and errors.
6. Unit/API/migration/security tests using temporary databases; add actual tests before CI claims a test suite.

Initial device provisioning is a local-only CLI action: generate a high-entropy token, store only its hash and device metadata, print the raw token once for local firmware configuration, and never expose a route that returns it again. Student creation binds the slot to the sole active MVP device; multi-device enrollment remains deferred.

Contract: [API plan](../docs/api-plan.md). Data model: [database plan](../docs/database-plan.md). Privacy boundary: [privacy/security](../docs/privacy-security.md).
