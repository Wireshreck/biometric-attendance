---
type: test
area: testing
status: active
tags:
  - testing
  - component-tests
---
# Component Test Builds

**Status:** Implemented as independent PlatformIO source-filter environments. A build pass does not mean the physical component passed. Source entry points are under `firmware/src/test_modes/` because PlatformIO compiles selected files below its configured `src_dir`; each environment excludes all other entry points.

From the repository root, build an image:

```powershell
pio run -d firmware -e esp32_core
```

Upload it to the connected ESP32:

```powershell
pio run -d firmware -e esp32_core -t upload
pio device monitor -d firmware -b 115200
```

Replace `esp32_core` with the environment in the table. To upload through a specific port, add `--upload-port COM3`; monitor with `--port COM3`.

| Test | Environments | Purpose and notes |
|---|---|---|
| ESP32 core | `esp32_core` | CPU, heap, flash, chip revision, reset cause; no GPIO is driven. |
| UART loopback | `uart1_loopback`, `uart2_loopback` | Defaults to GPIO25 TX and GPIO26 RX; install one jumper. Never use the R307S as loopback. Supports two UART peripherals at 57600 8-N-1. |
| R307S | `r307s` | Reuses `r307s_uart_diag.cpp`; bounded read-only commands only. |
| I2C | `i2c_scan` | Scans and reports all ACKing addresses. With the SSD1306 OLED removed, the expected device on GPIO25/26 is only the DS3231 (0x68) when present. |
| RTC | `rtc` | Reads DS3231 repeatedly and checks plausible advancing time/oscillator state. Never writes time. |
| Buzzer | `buzzer` | Two 80 ms pulses, no continuous tone; result remains UNVERIFIED until heard. |
| GPIO sanity | `gpio_sanity` | Configures selected input-capable pins as inputs; does not drive or short pins and cannot measure wiring. |
| Wi-Fi | `wifi_diag` | Scans without logging network names. Optional station association uses ignored `firmware/include/local_config.h`. |
| Backend | `backend_http` | Optional local Wi-Fi plus HTTP GET `/health` and JSON parse. No attendance record is sent. |
| JSON | `json` | Builds and parses a synthetic attendance-shaped object locally. |
| Storage | `storage` | Mounts LittleFS without formatting; writes/read/checks a temporary diagnostic record, detects a changed buffer checksum, and removes the test file. It is not the production event queue. |
| Reset/power telemetry | `power_reset` | Reports boot time, reset cause, heap, and CPU frequency. Does not measure electrical power. |

Credentials remain in ignored `firmware/include/local_config.h`, copied from `local_config.example.h`. Do not commit real SSIDs, passwords, device tokens, or UUIDs. Keep the test network local and isolated. The backend endpoint setting is used only for local `/health` GET in this test.

Removed environments: `oled`, `green_led`, and `red_led` no longer exist because the SSD1306 OLED and the green/red LEDs (and their series resistors) were removed from this project. GPIO18 and GPIO19 are unused/reserved.
