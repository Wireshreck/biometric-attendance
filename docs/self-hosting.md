# Self-hosting guide

Run the whole system on your own hardware. No developer laptop needed.

## Architecture

```
Android app ─┐
Web browser ─┼──► Your backend PC ──► SQLite (attendance.db)
Windows app ─┘        │  (FastAPI :8000)       ▲ auto-migrated, WAL
                      └──► ESP32 via BLE (each client pairs directly)
```

Clients talk to the backend over HTTP(S); to the ESP32 over BLE. The
backend never calls the ESP32 — no inbound firewall holes to the device.

## Backend on your machine

1. Install Python 3.11+, clone the repo.
2. `cd backend`, copy `.env.example` → `.env`, fill `ADMIN_USERNAME`,
   `ADMIN_PASSWORD` (≥16 chars), `APP_TIMEZONE`, optional `GEMINI_API_KEY`.
3. `pip install fastapi "uvicorn[standard]" pydantic aiosqlite tzdata python-dotenv openpyxl`
4. `python -m app.provision_device --name NAME --location LOC --sensor-capacity 1000`
5. `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
   (or `scripts\server.ps1 start` on Windows).
6. Check `/health` → `{"status":"ok","schema_version":2}`.

## LAN access (phone/other PCs)

1. Bind to your LAN IP: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
   (or set the host in your launcher). Prefer binding the specific LAN IP.
2. Windows Firewall → allow inbound TCP 8000 (Private profile only).
3. Server URL for clients: `http://YOUR-LAN-IP:8000` (example format only —
   use your actual IP from `ipconfig`).
4. If a phone *browser* (not the app) opens the console from LAN, set
   `ALLOWED_ORIGINS=http://YOUR-LAN-IP:8000` in `.env` and restart.
   Native mobile/desktop apps do not need CORS.

## HTTPS

For production, terminate TLS in front of uvicorn (reverse proxy such as
Caddy/Nginx) and use `https://attendance.example.com`. Keep the Gemini key
and admin password out of logs and out of git either way.

## Android

Install the app build, enter the server URL on first launch, Test
Connection (`/health`, shows schema), Continue, then admin credentials in
Settings. Change servers anytime via Settings → Change server.

## Backups and updates

Stop the server, copy `backend/data/attendance.db*`, restart. Update =
pull code → run backend tests → restart (migrations apply automatically)
→ reflash ESP32 if firmware changed → run FULL_DIAGNOSTIC. Roll back with
code + DB backup together.

## Troubleshooting

- Phone can't reach server: same Wi-Fi? IP correct? firewall rule? server
  bound to 0.0.0.0/LAN IP (not 127.0.0.1)?
- Browser CORS errors from LAN: set `ALLOWED_ORIGINS` to the exact origin.
- 401s: wrong admin creds, or editing `.env` without restarting.
- BLE invisible: press EN/RST, rescan; clear Windows pairing cache.
