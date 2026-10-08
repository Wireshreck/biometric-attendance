# Hardware verification record — v1.3.0 bench (2026-10-08, COM4)

Board: ESP32-WROOM-32 DevKit (CH340). Firmware: production 1.3.0, flashed
and verified over the air in the same session. Wiring unchanged:
DS3231 SDA→GPIO25/SCL→GPIO26, R307S yellow→GPIO32/green→GPIO33 (jumper
OPEN), buzzer→GPIO27. OLED/LEDs removed.

## Boot

`sensor=READY RTC=VALID storage=READY BLE=ADVERTISING`, I2C on
sda=25/scl=26, inventory capacity=1000. RTC battery holds time across
power cycles (VALID immediately after reflash without SETTIME).

## Component suites (PlatformIO envs, read-only unless noted)

- `i2c_scan`: PASS — 0x68 (DS3231) + 0x57 (EEPROM) on GPIO25/26.
- `r307s`: PASS — checksum-valid 0x00 ACKs at 57600, normal routing.
- `buzzer`: GPIO27 sequence executed (PASS code path). Audible confirmation
  requires a human ear; previously confirmed audible on this bench.
- `rtc`/`production`: build SUCCESS (all envs).

## BLE over-the-air (bleak, Windows)

All 10 device commands verified with live responses: PING, DEVICE_INFO
(1.3.0), DEVICE_STATUS (all true, count 2/1000 — two user templates
present, untouched), RTC_GET/SET (incl. invalid-date rejection),
FINGERPRINT_STATUS/COUNT, ATTENDANCE_STATUS/READ (paginated, 30 records),
BUZZER_TEST, FULL_DIAGNOSTIC 10/10 PASS, unknown-command rejection.

## Fingerprint enroll/search

HUMAN INPUT REQUIRED (no finger available in this session). Previously
verified live on this bench: enroll_success (slot 1, two-capture real
finger), search match (slot 1, confidence 184), honest no_match on empty
DB. Sensor currently holds 2 user templates — left untouched.

## Known bench behavior

- R307S UART shows intermittent framing glitches; firmware tolerates
  (3-strike rule) and recovers via bounded re-probe. Reseat yellow/green
  Duponts if glitches become frequent.
- Windows caches the GATT table per firmware build: after flashing, remove
  the pairing and toggle Bluetooth before reconnecting.
- Only one BLE central at a time; quit the enroll guide before using
  another client.
