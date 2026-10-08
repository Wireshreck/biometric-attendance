---
type: project
area: project
status: active
tags:
  - project
  - entry-point
---

# Biometric Attendance System v1.2.0

Local-first fingerprint attendance: ESP32 + R307S sensor + DS3231 RTC, a
FastAPI/SQLite backend, a web dashboard, an Expo mobile app, Windows tools,
and a Gemini assistant. No cloud required.

## 1. What this project is

A school attendance system. Students enroll a finger once; daily check-ins
take seconds: scan → match → timestamp → SQLite record → dashboard. It runs
on an isolated local network (optionally with internet only for Gemini
summaries).

## 2. Architecture

```
R307S + DS3231 + buzzer ──UART/I2C/GPIO── ESP32 (BLE GATT, JSON protocol)
        │                                       │ BLE (Web/Bluetooth apps)
        │ USB serial (flash/logs)               v
        │                              Windows-Python BLE clients
        v
Backend PC: FastAPI + SQLite (uvicorn 127.0.0.1:8000)
  ├── serves web dashboard (same origin)
  ├── REST for web / mobile / desktop
  └── optional Gemini summaries (server-side only)
```

## 3. Features

Dashboard, attendance explorer (search/filter/sort/paginate/export),
students (CRUD/deactivate/profiles), analytics, CSV+XLSX export, BLE device
management (17 commands), AI assistant, diagnostics, installer, test utility.

## 4. Hardware

ESP32-WROOM-32 DevKit, R307S module, DS3231 breakout, active buzzer module,
breadboard/jumpers/USB data cable. OLED and LEDs are removed.

## 5. Wiring

| Part | Wire | ESP32 |
|---|---|---|
| R307S TXD (yellow) | sensor out | GPIO32 (RX) |
| R307S RXD (green) | sensor in | GPIO33 (TX) |
| R307S VCC (red) | power | VIN / 5V |
| R307S GND (black) | ground | GND |
| R307S blue/white | — | disconnected |
| DS3231 SDA | data | GPIO25 |
| DS3231 SCL | clock | GPIO26 |
| DS3231 VCC/GND | power | 3V3 (if supported) / GND |
| Buzzer IN/GND | signal | GPIO27 / GND |

R307S 3.3V jumper: OPEN. Never use GPIO21/22 (old RTC pins) or GPIO23 (old
buzzer pin). ESP32 GPIO is 3.3V-only; verify R307S TX level ≤ 3.3V.

## 6. Requirements

Windows 10/11 + Python 3.11+, PlatformIO Core 6.2 (`pio` or
`%USERPROFILE%\.platformio\penv\Scripts\platformio.exe`), Node 18+
(web/mobile dev), Chrome/Edge (Web Bluetooth), Git + GitHub CLI (releases).

## 7. Repository structure

```
firmware/   ESP32 app (src/app|ble|hardware|network|storage, test_modes)
backend/    FastAPI + SQLite (app/, migrations/, tests/)
web/        Attendance Console (static; served by backend)
mobile/     Expo app (BLE + REST, self-hosted setup flow)
desktop/    Windows manager (tkinter + bleak + REST)
tools/      test_app (test.exe), installer (install.exe), enroll_guide
shared/     BLE protocol mirrors (py/js), tests/ protocol tests
scripts/    server.ps1 (backend manager), build_windows_apps.ps1
docs/       protocol/hardware/setup/web/mobile/windows/testing/...
hardware/   pinout/bring-up notes   diagrams/  firmware flows
```

## 8. Backend setup

```powershell
cd backend
copy .env.example .env   # then edit (see 10)
python -m pip install fastapi "uvicorn[standard]" pydantic aiosqlite tzdata python-dotenv openpyxl
.\scripts\server.ps1 start  # or: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Expect `{"status":"ok","schema_version":2}` at `/health`. Console at `/`.

## 9. SQLite setup

File `backend/data/attendance.db` (WAL). Created + migrated automatically
on first start (`migrations/001_*`, `002_*`). Verify:
`python -m pytest tests -q` from `backend/`.

## 10. Environment variables

| File | Variable | Format | Example |
|---|---|---|---|
| `backend/.env` | `DATABASE_PATH` | path | `data/attendance.db` |
| | `APP_TIMEZONE` | IANA zone | `Asia/Kolkata` |
| | `ADMIN_USERNAME` / `ADMIN_PASSWORD` | user / ≥16 chars | `admin` / `change-me-…` |
| | `MAX_CLOCK_SKEW_SECONDS` | int | `300` |
| | `GEMINI_API_KEY` | key, no quotes | (empty = local-only AI) |
| | `ALLOWED_ORIGINS` | comma URLs | `http://192.168.1.50:8000` |

Restart the server after any `.env` change (`scripts\server.ps1 restart`).
`.env` is gitignored — never commit it.

## 11. Gemini configuration

Set `GEMINI_API_KEY=` in `backend/.env`, restart. Without it `/api/v1/ai/chat`
answers from local data with `ai_available:false`. Key never leaves server.

## 12. ESP32 setup

Connect USB, discover (never assume COM4): `pio device list` (expect
CP210x/CH340, here COM4). Keep R307S wiring untouched.

## 13. Firmware build

`platformio.exe run -d firmware -e production` → SUCCESS expected.
Component envs: `i2c_scan rtc buzzer r307s gpio_sanity ...` (see
`docs/component-tests.md`).

## 14. Firmware flashing

`platformio.exe run -d firmware -e production -t upload --upload-port COMx`
(or `install.exe`). Fresh LittleFS once: same with `-t uploadfs`. 115200 baud
monitor shows `sensor=READY RTC=VALID storage=READY BLE=ADVERTISING`.

## 15. BLE setup

Service `89ea2240-04cc-4e36-9356-c71647be1c8d`, chars 0x1101–0x1108, JSON
write-then-read with busy-polling (`docs/protocol.md`). Name:
`biometric-attendance-esp32`. One central at a time; after flashes, clear
Windows pairing cache (remove + toggle Bluetooth).

## 16. Android setup

`cd mobile && npm install`; `npx expo start` (dev) or
`npx expo run:android` (on-device build, needs Android SDK — no APK is
bundled with releases for this reason).

## 17. Android self-hosted server configuration

No rebuilds, no hardcoded URLs: first launch shows setup → enter server URL
(`http://YOUR-PC-LAN-IP:8000`) → Test Connection (`/health`, shows schema)
→ Continue → admin credentials in Settings. Change servers anytime via
Settings. LAN: same Wi-Fi, Windows Firewall allows port 8000, start backend
bound to the LAN IP. See `docs/self-hosting.md`.

## 18. Web setup

Served by the backend at `/` (same origin, no CORS needed). Sign in with
admin creds (dialog, tab-session only). Views: Dashboard/Attendance/
Students/Device/AI/Help. `Ctrl+K` palette, dark-mode toggle.

## 19. Windows setup

`pip install bleak pyserial`, then `python desktop/app.py` (or
`dist/BiometricDesktop.exe`). Tabs mirror the web console; API host in
Settings (default `http://127.0.0.1:8000`).

## 20. Installer

`dist/install.exe` (or `python tools/installer/install_app.py`): checks
prereqs → detects ESP32 (pick the port, never assumes) → flashes firmware
→ verifies BLE → installs apps → launchers → final checks.

## 21. Test utility

`dist/test.exe`: CONNECT DEVICE → RUN FULL SYSTEM TEST (10 checks) plus
individual R307S/RTC/BUZZER/BLE/STORAGE/ATTENDANCE tests and EXPORT LOG.
Honest PASS/FAIL/WARN/SKIPPED; disconnected hardware is never PASS.

## 22. Device provisioning

In `backend/`: `python -m app.provision_device --name NAME --location LOC
--sensor-capacity 1000` (capacity = verified sensor count). Prints
`DEVICE_UUID` + one-time `DEVICE_TOKEN` — store the token in ignored local
config; it cannot be shown again. No restart needed.

## 23. Device credentials

Bearer token, SHA-256 hashed in SQLite (`devices.token_hash`). Rotate: set
device `REVOKED`, provision a replacement. Revoke: update status to
`REVOKED` (invalid immediately). Never commit tokens/UUIDs (see 34).

## 24. Student setup

Students → Add (roll/name/class/section) → PENDING_ENROLLMENT + slot →
enroll finger into that slot (Device tab or `tools/enroll_guide/`) →
Open → Mark enrolled → ACTIVE.

## 25. Fingerprint enrollment

Guided: `python tools/enroll_guide/enroll_guide.py` (countdown cues, live
verdict). Up to 3 attempts per capture; matching stays strict. Never
overwrite occupied slots (check count first).

## 26. Attendance workflow

Scan → slot → student lookup → RTC timestamp → SQLite `RECORDED` (60 s
debounce suppresses duplicates) → dashboard/statistics/SSE update.

## 27. Analytics

Overview (today), 7–60-day trends, per-class comparison, busy hours,
absentees — all aggregate SQL in `backend/app/stats.py`, shared with AI.

## 28. Exports

Attendance view → CSV/XLSX, honoring active filters (server-generated).

## 29. Diagnostics

`FULL_DIAGNOSTIC` (10 subsystems), `test.exe`, Device tab with animated
per-test results. See `docs/testing.md` for the hardware matrix.

## 30. Troubleshooting

See `docs/troubleshooting.md` (ESP32/BLE/R307S/RTC/buzzer/SQLite/backend/
Android/CORS/installer/Gemini/exports). BLE cache clearing and the
large-response pagination limit are documented there and in `docs/protocol.md`.

## 31. Development

Backend: `pytest tests -q` (backend/). Protocol: `pytest
tests/test_protocol.py`, `node mobile/protocol.test.js`. Firmware:
per-env `pio run`. Mobile JSX: babel parse via installed preset.

## 32. Testing

`docs/testing.md` + `backend/tests/test_dashboard.py` (dashboard, filters,
migration upgrade, exports, AI no-key, CORS). Hardware matrix in §29 of
that doc. Never fake hardware results.

## 33. Building releases

Firmware: `pio run -d firmware -e production` → `.pio/build/production/firmware.bin`.
Windows: `scripts/build_windows_apps.ps1` → `dist/*.exe`. Mobile APK:
`npx expo run:android` (needs SDK; not bundled). Tag `vX.Y.Z`, `gh release
create` with notes + assets (see `docs/self-hosting.md` update notes? no —
release checklist in §37).

## 34. Security

Server-side Gemini key; no secrets in tracked files/APK/EXE/firmware;
Basic admin + hashed device tokens; validated inputs; parameterized SQL;
CORS allowlist (empty default). Audit: search for tokens/keys before release.

## 35. Backup/recovery

Copy `backend/data/attendance.db*` (WAL trio) while the server is stopped.
Restore by copying back. LittleFS journal survives ESP32 power loss; RTC
battery holds time.

## 36. Updating

Backend: pull → `pytest` → restart (migrations auto-apply; back up first).
Firmware: pull → `pio run -t upload`. Apps: replace EXE / `npm install`.
Database migrates forward automatically; verify `/health` schema version.

## 37. Upgrade/migration procedure

1. Back up SQLite. 2. Record `/health` schema + firmware version. 3. Update
code. 4. Restart backend (watch migration logs). 5. Re-run backend tests.
6. Flash firmware if changed; run diagnostics. 7. Roll back = restore code +
DB backup (downgrades are not automatic; never go backward without backup).

## 38. Known limitations

Mobile APK not bundled (needs Android SDK); PDF export not included
(CSV+XLSX); R307S UART shows intermittent framing glitches on this bench
(firmware tolerates + recovers — reseat Duponts if frequent); ESP32→backend
Wi-Fi uplink unconfigured here (offline queue + BLE/USB transport used);
BLE single-central + Windows cache clearing sometimes needed.
