---
type: test
area: testing
status: unverified
tags:
  - hardware
  - testing
  - evidence
---
# Hardware Verification Evidence Log

**Status:** Hardware results are reported only when physically executed and observed. Runnable test procedure is maintained in [docs/hardware-test-plan.md](../docs/hardware-test-plan.md); this file records evidence and owner confirmations.

| ID | Component/test | Status | Evidence and limits |
|---|---|---|---|
| HW-00 | ESP32 toolchain, upload, USB serial | VERIFIED (owner/history report) | Previously built/flashed on COM3 at 115200 baud. Not reflashed during the 2026-10-02 audit. |
| HW-01 | Current R307S assembly | CONNECTED / NO VALID UART RESPONSE (owner report) | Red/VIN, black/GND, yellow/GPIO32 RX, green/GPIO33 TX, blue/white disconnected. Prior baud/routing scans received zero bytes. Sensor is not proven dead. |
| HW-02 | R307S VIN rail / current | UNVERIFIED — REQUIRES MULTIMETER | No independent rail/current measurement. |
| HW-03 | R307S TX high voltage / jumper / exact module wiring | UNVERIFIED — REQUIRES MULTIMETER / board inspection | Software ADC/internal-pull probe reported driven-high behavior; this is not calibrated voltage and does not prove sensor is powered. |
| HW-04 | ESP32 UART1/UART2 physical loopback | NOT EXECUTED | Environment `uart1_loopback` / `uart2_loopback`; jumper GPIO25 TX to GPIO26 RX. |
| HW-05 | I2C/DS3231 | NOT EXECUTED | Use `i2c_scan`, `rtc`; OLED removed from this project; no clock-setting test is performed. |
| HW-06 | Buzzer | NOT EXECUTED | Use `buzzer`; physical sound confirmation required. (LEDs removed from this project.)
| HW-07 | Wi-Fi and project API | NOT EXECUTED | Use `wifi_diag` / `backend_http` on isolated demo WLAN. HTTP image sends GET `/health` only. |
| HW-08 | LittleFS diagnostic | NOT EXECUTED | `storage` mounts without formatting, tests and removes only its diagnostic file; production journal is implemented but reboot/power-loss behavior needs device testing. |
| HW-09 | Integrated hardware / power recovery | NOT EXECUTED | Use staged integration tests after individual peripherals pass. Rail voltage and load behavior require measurements. |

## Historical evidence

Repository history records a successful ESP32 baseline upload/serial check and the R307S read-only diagnostic. Detailed sensor result transcript and known diagnostic limits remain in [R307S next-session handoff](../docs/r307s-next-session.md) and [hardware research](../docs/r307s-hardware-research.md). This log does not reinterpret those results as a hardware failure diagnosis.

## Record a future result

For each run, capture date/time, exact board/sensor revision, environment, wiring, measured voltage/current where relevant, test output, physical observations, and result. A successful firmware build alone must be recorded as **BUILD PASS**, not hardware PASS.
