# ESP32 Firmware

**Status:** VERIFIED — `src/main.cpp` compiles for `esp32dev` with pinned dependencies (`pio run -d firmware`, 2026-09-25). This verifies compilation only; flashing/board behavior NEEDS HARDWARE. Attendance, enrollment, RTC, OLED, networking, LittleFS queue, authentication, retries, and watchdog behavior are PLANNED.

## Build target and dependencies

PlatformIO Core, `espressif32@6.5.0`, board `esp32dev`, Arduino framework, ESP32-WROOM-32-class DevKit. Libraries and exact versions are pinned in `platformio.ini`. `littlefs` is selected as the future offline storage filesystem; setting it does not implement a queue.

```powershell
cd C:\Users\user\projects\fair\biometric-attendance\firmware
pio run
```

Upload/serial commands require a physical board and are not verified here:

```powershell
pio run -t upload
pio device monitor -b 115200
```

## Local configuration and secrets

Copy `include/local_config.example.h` to `include/local_config.h`; the latter is ignored by Git. Set demo SSID/password and server host locally. The defaults are empty. Do not commit real credentials. Keep demonstration data synthetic; the planned local HTTP transport is not encrypted end-to-end.

## Intended task/state design

- Sensor/UI task: bounded UART operations, sensor timeout recovery, generic user messages, RTC validation, non-blocking feedback state machine.
- Network/storage worker: persistent event UUIDs, bounded LittleFS queue with integrity/framing, retry with backoff, chronological replay, remove an event only after server acknowledges its stored idempotent result.
- Never block sensor feedback while waiting for network. Queue full/write failure must show an error and never claim an event is safely queued.
- Use framework watchdog defaults and short bounded tasks; do not disable watchdogs or feed them from a stuck loop.
- Do not log fingerprint images/templates, names, passwords, tokens, or full attendance payloads.
- Enrollment/deactivation requires local USB serial access. Allocate slot via API, capture two impressions, confirm sensor write before marking student active. Verify template deletion before slot reuse.

## Implementation order

1. Bench-test power, AS608 UART voltage/handshake, I2C, and indicators separately.
2. Add PlatformIO test environments/sketches for sensor handshake, I2C, and indicators (none currently exist).
3. Implement sensor enrollment/search/delete and explicit error states; measure timings.
4. Add RTC timezone policy and generic screen prompts.
5. Add Wi-Fi device authentication and event API client.
6. Add crash-safe LittleFS queue, event UUID, overflow behavior, and reconnect replay.
7. Run hardware/failure gates in [hardware test plan](../hardware/test-plan.md) and [software test plan](../docs/testing-plan.md).

Pinout and electrical assumptions are provisional; follow [wiring safety plan](../docs/wiring.md).
