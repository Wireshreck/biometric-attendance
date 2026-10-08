# Web App (`web/`)

Attendance Console: dashboard, attendance explorer, students, BLE device
manager, AI assistant, help. Static files, no build step — served by the
backend itself (same origin as the API):

```powershell
cd backend
# configure .env from .env.example first
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# open http://127.0.0.1:8000/ in Chrome/Edge, sign in with admin credentials
```

Standalone BLE-only use is still possible via any static server
(`python -m http.server` in `web/`); backend-backed views then point at
the API host.

Design: light, restrained, table-first; system fonts; one accent color;
no gradients/glow/particles. Canvas bar charts are hand-drawn (no
dependencies, works offline). Respects `prefers-reduced-motion`.
Responsive: tables collapse to two-column cards under 860 px.
Accessible: skip link, labeled controls, focus states, live regions.

## Views

- Dashboard: present/absent counts, percentage, 7-day trend, per-class
  table, busiest hours, recent check-ins. Auto-refreshes on new records
  (polls recent endpoint; full SSE stream is exposed for header-capable
  clients at `/api/v1/events`).
- Attendance: search (debounced), date/range/time filters, class/section/
  fingerprint/status filters, sorting, pagination, CSV + XLSX export —
  all server-side queries.
- Students: search, class/status filters, add/edit/deactivate, 30-day
  profile with percentage and first/last attendance.
- Device: BLE connect, DEVICE_INFO/STATUS refresh, FULL_DIAGNOSTIC table,
  fingerprint enroll/search/delete, RTC read/set. Uses the single shared
  protocol (`web/vendor/ble_protocol.js`, generated from
  `shared/ble_protocol.js` by stripping `export` for classic-script
  loading — enforced by test).
- AI Assistant: chat with suggested questions, structured mini-tables,
  honest missing-key notice.
- Help: setup, demo flow, AI key setup.

Bluetooth uses numeric 16-bit characteristic UUIDs 0x1101–0x1108 under
service `89ea2240-04cc-4e36-9356-c71647be1c8d`. See `docs/protocol.md`.
