# Setup Guide

## Hardware

- ESP32-WROOM-32 DevKit, USB data cable.
- R307S: red→VIN, black→GND, yellow→GPIO32 (ESP32 RX), green→GPIO33 (ESP32 TX), blue/white disconnected. Jumper OPEN (normal onboard-regulator). Never assume wire colors; verify with the module silkscreen.
- DS3231: VCC→3V3 (only if the breakout supports it), GND→GND, SDA→GPIO25, SCL→GPIO26. Address 0x68.
- Buzzer module input→GPIO27, GND→GND (use a driver if the module exceeds GPIO current).
- OLED and LEDs are removed. Do not connect displays/LEDs without updating `firmware/include/config.h` and `docs/final-pin-map.md`.

## Firmware build and flash

Prerequisite: PlatformIO Core 6.2.0 (`pio` on PATH or
`$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe`).

```powershell
C:\Users\User\.platformio\penv\Scripts\platformio.exe run -d firmware -e production
```

Flash with `install.exe` (recommended: it detects the ESP32 port instead of
assuming one) or manually:

```powershell
.../platformio.exe run -d firmware -e production -t upload --upload-port COMx
```

Never hardcode COM4. If several ports exist, identify the USB-serial
(CP210x/CH340) device in Device Manager first.

## Configure and verify

1. `install.exe` steps 5–6, or open the serial monitor at 115200.
2. Confirm `BLE=ADVERTISING`, `RTC=VALID/INVALID`, `sensor=READY/UNAVAILABLE`.
3. Web app (`web/index.html` over `http://localhost`, Chrome/Edge): Connect BLE
   → Refresh dashboard → RTC_GET → FINGERPRINT_COUNT.
4. `test.exe`: CONNECT DEVICE → RUN FULL SYSTEM TEST. Disconnected hardware
   reports FAIL/SKIPPED, never PASS.

## Science-fair demo flow (protocol terms)

PING → DEVICE_INFO → DEVICE_STATUS → RTC_GET → FINGERPRINT_COUNT →
FINGERPRINT_ENROLL → FINGERPRINT_SEARCH → ATTENDANCE_READ → FULL_DIAGNOSTIC.

See also: `docs/web.md`, `docs/mobile.md`, `docs/windows.md`,
`docs/troubleshooting.md`, `docs/testing.md`.
