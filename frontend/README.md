# Web Dashboard Plan

**Status:** PLANNED — UI not implemented. The `frontend/` directory currently contains this design note only. The backend owns the static-file mount once `backend/app/main.py` exists.

## Selected approach

Vanilla semantic HTML, CSS, and ES modules; no Node runtime, package manager, or build step. FastAPI serves the static assets from the same origin as the API. No browser connection to SQLite and no storage of device/API credentials in JavaScript or local storage.

## MVP views

1. **Today:** date/timezone, present distinct count, active count, absent count, percentage, recent accepted scan feed, live-connection state.
2. **Students:** paginated/searchable directory; add synthetic attendee; show `PENDING_ENROLLMENT` and assigned slot; activation occurs only after device confirms enrollment; deactivate with template-cleanup warning.
3. **History/export:** date range and optional class filters; authorized CSV download; explicit empty/error states.
4. **Devices/system:** online/last heartbeat, service/database health, queued/offline indication where known; no secret values.

Enrollment itself is initiated from the physical USB serial console in the MVP. The dashboard does not remotely issue sensor commands.

## API interaction

- Use same-origin `fetch()` for `/api/v1/students`, `/api/v1/attendance`, `/api/v1/reports/daily`, and `/api/v1/reports/export.csv`.
- Use authenticated Server-Sent Events at `/api/v1/events` for newly committed attendance outcomes. Reconnect using `Last-Event-ID`; de-duplicate in UI using event UUID. Refresh aggregate report after an event or date change.
- Use browser-managed Basic Auth for the planned demo admin endpoints; do not place credentials in source, query strings, local storage, or logs. Prototype is synthetic-data only because local HTTP does not encrypt credentials.
- Display model-generated content (if optional assistant is later added) separately from database values and identify it as a generated explanation.

## User states and acceptance

Provide initial loading, no students, no events, invalid input, permission denied, API unreachable, SSE reconnecting, offline device, export failure, and success states. Never show “recorded” until API confirms a stored result. Respect keyboard access, visible focus, labels, contrast, narrow mobile view, and text zoom. See [API contract](../docs/api-plan.md) and [UI test plan](../docs/testing-plan.md).
