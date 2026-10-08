# Web App (`web/`)

Static management UI using Web Bluetooth. No build step; serve over HTTP
(Web Bluetooth requires a secure context — `http://localhost` works):

```powershell
cd web
python -m http.server 8000
# open http://localhost:8000/index.html in Chrome/Edge
```

Uses the single shared protocol (`shared/ble_protocol.js`, loaded as a
classic script exposing `window.BLE_PROTOCOL`); no alternate commands.

## Features

- Dashboard: connect/disconnect, device name, firmware, uptime, RTC, R307S,
  fingerprint count, storage, attendance status.
- Fingerprint: status, count, enroll (slot 1–1000), search/test, delete,
  delete-all with confirmation. Enrollment progress shown; only
  `enroll_success` counts as success.
- RTC: display current time, set from laptop clock, lost-power warning.
- Attendance: status, record table (slot, timestamp, status), clear with
  confirmation.
- Diagnostics: FULL_DIAGNOSTIC table with PASS/FAIL/WARN/SKIPPED,
  BUZZER_TEST (GPIO27), PING/BLE test.
- Help: setup, pairing, hardware, enrollment, troubleshooting, demo flow.

Characteristic UUIDs are the 16-bit forms 0x1101–0x1108 (numeric) under the
custom service `89ea2240-04cc-4e36-9356-c71647be1c8d`, matching the firmware
GATT table. See `docs/protocol.md`.
