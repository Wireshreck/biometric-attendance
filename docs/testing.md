# Testing

## Software-only (run anywhere, no hardware)

```powershell
# shared protocol unit tests
python -m pytest tests/test_protocol.py -q
# backend suite (existing)
# from backend/: .venv/Scripts/python -m pytest tests -q
# web/mobile protocol tests (needs node)
node mobile/protocol.test.js
# firmware compile (needs PlatformIO + network for first lib install)
C:\Users\User\.platformio\penv\Scripts\platformio.exe run -d firmware -e production
```

`tests/test_protocol.py` validates the shared command table, envelope,
error codes, enrollment states, diagnostic result honesty
(disconnected hardware must not be PASS), timeouts, and the final pin
mapping. It also cross-checks `firmware/include/ble_protocol.h`,
`shared/ble_protocol.js`, and `docs/protocol.md` for command drift.

## Hardware-required (ESP32 + R307S + DS3231 + buzzer)

- `firmware -e i2c_scan` → DS3231 at 0x68 on GPIO25/26.
- `firmware -e rtc`, `-e buzzer` (GPIO27), `-e r307s`, `-e int_full`.
- Web/mobile/desktop/test.exe against the live device: PING, DEVICE_STATUS,
  RTC_GET/SET, FINGERPRINT_COUNT/ENROLL/SEARCH/DELETE, ATTENDANCE_READ/CLEAR,
  FULL_DIAGNOSTIC.
- Results are recorded with module revisions and measurements. Compilation
  alone is never a hardware PASS. If no hardware is attached during automated
  runs, the report states that explicitly (see release notes).
