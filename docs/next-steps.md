---
type: project
area: workshop
status: active
tags:
  - next-steps
  - planning
  - unverified
---
# Firmware and hardware next steps

The software now contains a production runtime and isolated diagnostic images. Prioritize physical evidence; do not write more feature code until actual component results expose a concrete defect.

## First three actions at a safe bench

1. Record ESP32 DevKit and R307S PCB/model markings, connector orientation, and jumper/solder-link state. Do not infer the pinout from harness colors.
2. With suitable meter access, verify ground continuity, R307S VIN-to-GND rail during boot, and sensor TX idle level. Keep them **UNVERIFIED — REQUIRES MULTIMETER** until measured. Do not change current wiring based solely on zero UART bytes.
3. With the sensor disconnected from loopback pins, run `uart1_loopback`/`uart2_loopback` using GPIO25 TX→GPIO26 RX; then run the read-only `r307s` environment only if signal voltage is safe. Save complete serial output.

## Component and integration sequence

4. Run `i2c_scan` and `rtc` separately after confirming module rails and I2C pull-ups. Do not install a CR2032 until the exact RTC breakout's charge circuit is known. The SSD1306 OLED was removed from this project, so there is no OLED test path.
5. Run `buzzer`; record actual sound and verify no heating or unexpected reset. The green/red LEDs and their series resistors were removed from this project, so there is no LED test path.
6. Run `storage`; then initialize a disposable/new filesystem only if safe to erase it. Never run `uploadfs` on a device that may hold queued events.
7. Run `wifi_diag` and `backend_http` only on an isolated local synthetic-data network. Backend HTTP smoke-test performs GET `/health` only.
8. Use local synthetic device/student records to validate enrollment assignment/confirmation and event POST; verify queue ordering, restart recovery, duplicate UUID replay, and invalid HTTP/auth cases before any public demo.
9. Only after individual checks, test `production` firmware end-to-end. Capture UUIDs/outcomes in local test DB and verify offline events arrive exactly once after reconnect.
10. Update [hardware/test-plan.md](../hardware/test-plan.md), requirements traceability, [[TODO]], milestone/handoff, and Canvas with measured evidence. Keep browser dashboard work deferred until the backend exposes read/report routes.

## Current block

Owner-reported R307S diagnostics returned no valid UART bytes at tested assumptions. Sensor rail/logic and health remain unverified. RTC/buzzer/Wi-Fi/API and actual LittleFS reset behavior also have no current physical pass record. The SSD1306 OLED, the green/red LEDs, and their series resistors were removed from this project; see [final pin map](final-pin-map.md), [firmware audit](firmware-audit.md), [R307S research](r307s-hardware-research.md), and [power safety](power-and-safety.md).
