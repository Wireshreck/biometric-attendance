---
type: reference
area: firmware
status: active
tags:
  - firmware
  - reference
---
# ESP32 Firmware

**Status:** Production software now includes R307S matching and two-capture enrollment, a DS3231 timestamp gate, buzzer feedback, explicit serial enrollment, authenticated attendance POST, and a bounded persistent offline journal/replay. It compiles; no full physical workflow was tested. The R307S currently has no reported UART response, so operational attendance is still blocked by sensor/electrical verification. The SSD1306 OLED, the green/red LEDs, and their series resistors were removed from this project; status is reported on the serial console only. See [production behavior](../docs/production-firmware.md), [test matrix](../docs/hardware-test-plan.md), and [final pin map](../docs/final-pin-map.md).

## Build and run

From the repository root:

```powershell
pio run -d firmware -e production
pio run -d firmware -e esp32_core
pio run -d firmware -e r307s
pio run -d firmware -e production -t upload --upload-port COM3
pio run -d firmware -t uploadfs --upload-port COM3
```

The complete environment names and purpose are listed in [component tests](../docs/component-tests.md) and [integration tests](../docs/integration-tests.md). Upload one selected image with:

```powershell
pio run -d firmware -e <environment> -t upload --upload-port COM3
pio device monitor -d firmware --port COM3 --baud 115200
```

The port can change after reconnect; check the available ports rather than assuming COM3. `esp32dev` remains as a compatibility name for the production environment. The default environment is `production`.

Every image uses a source filter that selects one entry point. Test source lives in `src/test_modes/` so PlatformIO can include each entry under its configured `src` directory. Diagnostics print `[PASS]`, `[FAIL]`, `[NOT EXECUTED]`, and a `RESULT`; a compile result is not a physical hardware result.

`uploadfs` initializes the LittleFS partition for first use and replaces its contents. Only use it on a new/known-empty device before any events are stored; it erases the offline queue. Routine firmware uploads do not need `uploadfs`. The production firmware mounts with formatting disabled so a mount failure cannot silently erase queued data.

## Current R307S state

The owner reports R307S UART2 wiring to GPIO32/33 and 0-byte diagnostic responses. The diagnostic is preserved and read-only. Current VIN and sensor TX voltages are **UNVERIFIED — REQUIRES MULTIMETER**. The firmware reports `SENSOR NOT FOUND` and retries; do not interpret that message as a confirmed dead module. GPIO16/17 is obsolete wiring guidance for this setup.

## Local configuration

Copy `include/local_config.example.h` to the ignored `include/local_config.h` only when testing a local isolated demo network. Leave credentials blank for offline tests. The HTTP test performs GET `/health` only. Never put Wi-Fi passwords or device tokens in tracked files or logs.

## Production behavior and limits

The serial console accepts `HELP`, `STATUS`, `SETTIME YYYY-MM-DD HH:MM:SS`, and `ENROLL <pending-student-uuid>`. `SETTIME` sets local wall time (+05:30) only when explicitly entered; compare with a trusted clock. `ENROLL` requires USB/local serial access, Wi-Fi, device credentials, a backend pending student, and a working sensor. Never enroll during ordinary scans.

`local_config.h` needs demo SSID/password, backend host/port, provisioned device UUID, and token. Backend provisioning must use a verified sensor capacity; current sensor health is unverified. HTTP bearer credentials are unencrypted on the isolated LAN, so use synthetic data on a private test network and never expose this service to the public internet. The client only acknowledges an event after API success (including server duplicate suppression); failed events remain in the LittleFS queue. The queue is bounded and fails closed when full/corrupt. It stores slot ID, UUID and timestamp only, not images/templates or student names.

The runtime is compile-verified, but these still need physical verification: R307S enrollment/matching, actual sensor capacity, RTC module and time, buzzer current, durable queue across actual resets, Wi-Fi, local API request/response, offline replay, and full end-to-end behavior. The OLED and indicator LEDs are no longer in this project. See [complete beginner assembly](../docs/COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md), [breadboard placement](../docs/complete-breadboard-layout.md), and [production firmware](../docs/production-firmware.md).
