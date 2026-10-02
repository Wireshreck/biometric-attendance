---
type: test
area: testing
status: unverified
tags:
  - testing
  - verification
  - platformio
  - evidence
---

# 05 - Testing Lab

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[03 - Firmware Lab]] [[04 - Backend Server Room]] [[06 - Research Archive]] [[10 - Workshop]] · **CANVAS** [[05 - Testing Lab/05 - Testing Lab.canvas]]

The evidence room. **27 firmware environments build. 0 physical results are recorded. 10 backend tests pass.**

Those two sentences are the whole point of this room.

---

## The five kinds of "it works"

They are not the same claim, and this vault never lets them blur into each other.

| Kind | What it proves | What it does **not** prove |
|---|---|---|
| **BUILD PASS** | The image compiles and links | That any part exists |
| **SOFTWARE PASS** | A function returns the expected result on synthetic input | That the hardware path is sound |
| **UNVERIFIED** | The firmware *issued the command*; nobody observed the effect | That the LED lit, the RTC ticked, the sensor answered |
| **PASS** | A person ran it **and** saw the expected physical result | — |
| **BLOCKED** | A prerequisite prevents the test | Nothing at all |

> The shared reporter `firmware/include/test_result.h` enforces this in code: `finish()` cannot return `PASS` when checks were skipped or when a test called `unverified()`. Tests that cannot sense their own effect (OLED, LEDs, buzzer) *must* land in `UNVERIFIED`.

---

## Component environments — 15

| Environment | Exercises | Physical result |
|---|---|---|
| `esp32_core` | chip, CPU, heap, flash, reset reason. Drives no GPIO | not executed |
| `uart1_loopback` | UART1, GPIO25 TX → GPIO26 RX jumper, byte-exact + CRC16 | not executed |
| `uart2_loopback` | same on UART2 | not executed |
| `r307s` | read-only VerifyPassword / ReadSysPara / TemplateCount | **0 bytes — UNVERIFIED** |
| `i2c_scan` | sweeps addresses 1–126 on GPIO21/22 | not executed |
| `oled` | SSD1306 init, text, pixel, line, clear, refresh | not executed |
| `rtc` | DS3231 ACK, plausible advancing time, `lostPower`. **Never writes the clock** | not executed |
| `green_led` | GPIO18: off 1 s, on 1 s, three blinks | not executed |
| `red_led` | same on GPIO19 | not executed |
| `buzzer` | GPIO23: quiet 1 s, two 80 ms beeps | not executed |
| `gpio_sanity` | configures 25/26/27/32/33/34/35/36/39 as inputs. Drives nothing, shorts nothing | not executed |
| `wifi_diag` | radio scan without logging SSIDs; optional association | not executed |
| `backend_http` | optional local Wi-Fi + `GET /health` + JSON parse. **Sends no attendance record** | not executed |
| `json` | synthetic attendance payload round-trip | not executed |
| `storage` | LittleFS mount *without* formatting, write/read/CRC, corrupt-detect, cleanup | not executed |
| `power_reset` | reset reason, boot time, heap, CPU. **Measures no voltage** | not executed |

Each environment is an isolated `build_src_filter = -<*> +<one file>`, so exactly one `setup()/loop()` compiles.

---

## Integration environments — 9

One `integration_test.cpp`, selected by `-D INTEGRATION_CASE=1..9`.

| ID | Env | Combines |
|---|---|---|
| INT-01 | `int_oled` | ESP32 + OLED |
| INT-02 | `int_rtc` | ESP32 + RTC |
| INT-03 | `int_outputs` | ESP32 + LEDs + buzzer |
| INT-04 | `int_r307s` | ESP32 + R307S read-only probe |
| INT-05 | `int_r307s_oled` | R307S + OLED |
| INT-06 | `int_r307s_rtc` | R307S + RTC |
| INT-07 | `int_wifi` | ESP32 + Wi-Fi |
| INT-08 | `int_backend` | ESP32 + backend `/health` |
| INT-09 | `int_full` | everything except the production attendance workflow |
| INT-10 | `production` | **the real attendance flow** — enrollment, live POST, outage, reboot, replay |

**INT-10 is the only test that would prove the product.** It has never been run. The queue's crash/replay claims are unverified until it is.

---

## Backend — 10 tests, passing

```bash
cd backend && .venv/Scripts/python.exe -m pytest tests -q
# 10 passed, 1 warning in 0.79s
```

`backend/tests/test_api.py` (164 lines) and `backend/tests/test_database.py` (167 lines) run against temporary SQLite databases seeded with synthetic records. They cover the API contract, the migration path, constraints, idempotency and the 60-second boundary.

A green backend suite says nothing about the wire between the ESP32 and the laptop. That path is `NEEDS INTEGRATION TEST`.

---

## How to record a result

1. Standalone environment first. Never start with `int_full`.
2. Attach **only** the component under test.
3. Never apply an unmeasured >3.3 V signal to a GPIO. Do not format storage.
4. Record: date, board/module revision, wiring, supply source, meter readings, environment name, full serial log, observation.
5. Write **PASS** only if you watched it happen. A green build is `BUILD PASS`.

Evidence belongs in [[hardware/test-plan.md]]. Procedure belongs in [[docs/hardware-test-plan.md]]. The two are deliberately separate files and must stay that way.

---

## Documents

[[docs/component-tests.md]] · [[docs/integration-tests.md]] · [[docs/hardware-test-plan.md]] · [[hardware/test-plan.md]] · [[docs/testing-plan.md]] · [[docs/requirements-traceability.md]] · [[docs/r307s-test-matrix.md]] · [[docs/failure-modes.md]]

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[03 - Firmware Lab]] [[04 - Backend Server Room]] [[10 - Workshop]] · **CANVAS** [[05 - Testing Lab/05 - Testing Lab.canvas]]
