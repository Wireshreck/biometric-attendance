# Testing (v1.1.0)

## Software-only (no hardware)

```powershell
python -m pytest tests/test_protocol.py -q   # shared BLE protocol + mirrors
cd backend; python -m pytest tests -q        # 17 tests: API, dashboard, migrations, AI
node mobile/protocol.test.js                 # web/mobile protocol module
C:\Users\User\.platformio\penv\Scripts\platformio.exe run -d firmware -e production
```

Hardware-required tests report honestly: no hardware → tools refuse
PASS (FAIL/SKIPPED with reasons).

## Hardware (ESP32 + R307S + DS3231 + buzzer on COMx)

```powershell
# component builds, one upload+run each:
pio run -d firmware -e i2c_scan -t upload --upload-port COMx     # expect 0x68 (+0x57 EEPROM)
pio run -d firmware -e rtc -t upload --upload-port COMx          # ticking, no writes
pio run -d firmware -e buzzer -t upload --upload-port COMx        # GPIO27 sequence (listen!)
pio run -d firmware -e r307s -t upload --upload-port COMx         # valid R307S ACK
pio run -d firmware -e production -t upload --upload-port COMx   # full system
python C:\Users\User\AppData\Local\Temp\ble_full.py              # over-air BLE suite
```

Enrollment/search need a finger on the sensor with the documented
place → remove → place-again choreography; the device logs
`[ENROLL]` stages on serial. Use an empty slot (check
FINGERPRINT_COUNT first), link it to a `TEST-` student in the backend,
verify the attendance row and dashboard, then delete the slot, the test
student rows, and device records.

## AI

Without `GEMINI_API_KEY`: `/api/v1/ai/chat` answers from local data
with `ai_available: false` (tested). With a key: backend-only call,
never logged, invalid keys degrade to the same local answer. The key is
never committed, never sent to browsers, never baked into binaries.
