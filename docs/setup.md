# Setup Guide (v1.1.0)

## Hardware

- ESP32-WROOM-32 DevKit, USB data cable.
- R307S: red→VIN, black→GND, yellow→GPIO32 (ESP32 RX), green→GPIO33 (ESP32 TX), blue/white disconnected. Jumper OPEN.
- DS3231: VCC→3V3 (only if the breakout supports it), GND→GND, SDA→GPIO25, SCL→GPIO26. Address 0x68 (plus 0x57 EEPROM on most modules).
- Buzzer module input→GPIO27, GND→GND.
- OLED and LEDs are removed.

## Backend + dashboard

```powershell
cd backend
copy .env.example .env   # then fill ADMIN_USERNAME / ADMIN_PASSWORD (min 16 chars), optional GEMINI_API_KEY
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# open http://127.0.0.1:8000/ and sign in
```

SQLite lives at `backend/data/attendance.db` (WAL mode, migrations
`backend/migrations/`). Schema v2 added employee-team columns, device firmware
tracking, and search/filter indexes; v3 adds offline-sync metadata
(`client_seq`, `clock_uncertain`) and `company_settings`. Never delete a real
database to "fix" it — migrations preserve data; see `docs/testing.md`.

## Firmware

```powershell
C:\Users\User\.platformio\penv\Scripts\platformio.exe run -d firmware -e production -t upload --upload-port COMx
```

Discover the port first (`pio device list`); never assume COM4. After
flashing, if LittleFS is fresh, run `... -t uploadfs` once to format it,
then set the clock (`SETTIME YYYY-MM-DD HH:MM:SS` on serial, RTC_SET over
BLE, or RTC tab in any client).

## Verify

1. Serial 115200: `sensor=READY RTC=VALID storage=READY BLE=ADVERTISING`.
2. `test.exe`: CONNECT DEVICE → RUN FULL SYSTEM TEST (expect 10× PASS).
3. Web Device tab or BLE script: PING → DEVICE_STATUS → FINGERPRINT_COUNT.
4. Dashboard: enroll a test slot, search it, confirm the record, then
   clean up test data.

## Science-fair demo

Dashboard → enroll → search → live attendance row → FULL_DIAGNOSTIC →
CSV export → AI summary ("Summarize today's attendance").
