# Hardware Test Plan

**Status:** TEST FIRMWARE IMPLEMENTED; physical test execution remains unverified unless an evidence row below says otherwise.
**Detailed procedures:** this index maps to the runnable isolated firmware builds. Hardware evidence/results belong in [hardware/test-plan.md](../hardware/test-plan.md); do not mark tests passed based on compilation alone.

## Execution rules

1. Start with a standalone test environment. Do not run the full integration image first.
2. Confirm the exact ESP32 board and only attach the component listed for that test.
3. Never connect an unmeasured >3.3 V signal to an ESP32 input, drive arbitrary pins, short pins, or format storage.
4. The R307S test is read-only. Do not enroll or erase templates until the sensor is identified and its protocol/power are verified.
5. Record date, board/module revision, wiring, supply source, meter readings, environment name, serial log, and result.
6. Use **PASS** only after executing and observing the required test. Builds are **BUILD PASS**, not hardware PASS. The firmware test reporter supports PASS, FAIL, NOT EXECUTED, and UNVERIFIED; use **BLOCKED** in the evidence log when a prerequisite prevents testing.

## Standalone sequence

| Order | Environment | Subsystem | Expected evidence | Physical dependency | Current result |
|---:|---|---|---|---|---|
| 1 | `esp32_core` | Boot, chip, CPU, heap, flash, reset reason | Serial report, no arbitrary GPIO drive | ESP32 and USB serial | Build verified; runtime prior owner-reported |
| 2 | `uart1_loopback`, `uart2_loopback` | UART transmit/receive/checksum | Jumper from GPIO25 TX to GPIO26 RX; byte-for-byte match | Jumper wire and ESP32 | Not executed in this audit |
| 3 | `r307s` | R307S read-only packet/baud/response test | Valid checksum ACK and read-only parameters, or honest no-response result | Existing reported connection; rail and levels need meter verification | No valid response reported by owner; rerun result not collected here |
| 4 | `i2c_scan` | SDA/SCL address scan | Detected address list; no assumed devices | OLED/RTC if present | Not executed |
| 5 | `oled` | SSD1306 text/graphics/repeated refresh | Expected text visible and initialization success | OLED and safe 3.3 V I2C pull-ups | Not executed |
| 6 | `rtc` | DS3231 address/time/oscillator/repeated read | Plausible advancing time, no power-loss flag | RTC and backup supply | Not executed; no clock write occurs |
| 7 | `green_led`, `red_led` | Individual GPIO output sequence | Off/on/three blink pulses observed | Series current-limiting resistor | Not executed |
| 8 | `buzzer` | Quiet/two-short-beep output sequence | Beeps heard and output returns off | Suitable module/driver | Not executed |
| 9 | `gpio_sanity` | Input-mode configuration | Logs only; no outputs driven | ESP32 | Not executed |
| 10 | `wifi_diag` | Scan, optional association/DHCP/RSSI | Scan succeeds; connection evidence only if local credentials exist | 2.4 GHz test network; ignored local config | Not executed |
| 11 | `backend_http` | Local Wi-Fi + HTTP GET `/health` + JSON parse | HTTP 200 and `{"status":"ok"}` | Local isolated backend and test Wi-Fi | Not executed; no attendance POST is sent |
| 12 | `json` | Attendance JSON serialization and parsing | Synthetic fields round-trip to expected schema | None | Not executed |
| 13 | `storage` | LittleFS write/read/checksum/corrupt-detect/cleanup | No format; diagnostic file removed after test | ESP32 flash filesystem | Not executed |
| 14 | `power_reset` | Reset reason, boot timing, heap/CPU telemetry | Values reported; brownout reason interpreted cautiously | ESP32/USB | Not executed; electrical rails unmeasured |

## Test result distinctions

- PlatformIO builds prove only that the selected image compiles and links.
- GPIO output code cannot sense an LED or buzzer. A sequence log alone does not prove light or sound.
- An RTC I2C ACK does not prove clock accuracy or battery-backed holdover.
- The power/reset sketch cannot measure voltage, current, ripple, or regulator behavior.
- Wi-Fi and backend tests do not transmit student data. HTTP testing uses GET `/health`; actual attendance POST requires separate local synthetic fixture setup and backend tests.

See [component tests](component-tests.md), [integration tests](integration-tests.md), [power and safety](power-and-safety.md), and the legacy evidence log at [hardware/test-plan.md](../hardware/test-plan.md).


## Software build evidence (2026-10-02)

All 25 component and integration PlatformIO test environments compiled and linked. Production and backwards-compatible sp32dev environments also compiled and linked. Backend suite: 10 passed. These results do not establish electrical, sensor, display, RTC, storage-on-device, Wi-Fi, or end-to-end behavior. No upload or physical test was performed.
