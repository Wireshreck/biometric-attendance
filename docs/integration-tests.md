---
type: test
area: testing
status: planned
tags:
  - testing
  - integration
---
# Firmware Integration Tests

**Status:** Integration diagnostic entry points and PlatformIO environments are implemented; physical execution is **NOT EXECUTED** here. The separate `production` image contains the attendance workflow, but a build is not evidence that attached devices work.

From the repository root, build/upload each environment with:

```powershell
pio run -d firmware -e int_rtc
pio run -d firmware -e int_rtc -t upload
pio device monitor -d firmware -b 115200 --port COM3
```

| ID | Environment | Prerequisites | Expected result / limits |
|---|---|---|---|
| INT-01 | `int_rtc` | ESP32 + DS3231 | I2C responds, time plausible, oscillator not stopped. No time write. |
| INT-02 | `int_r307s` | Existing R307S connection; only after power/logic safety gate | Runs existing read-only diagnostic; no enrollment/deletion. No response is not proof of dead sensor. |
| INT-03 | `int_r307s_rtc` | R307S + DS3231 | RTC does not supply a timestamp to sensor test; read-only sensor probe remains independent. |
| INT-04 | `int_wifi` | Isolated 2.4 GHz network; optional ignored config | Scans; optional DHCP/RSSI check when credentials are configured. Does not print SSIDs. |
| INT-05 | `int_backend` | Test Wi-Fi and locally running project backend | GET `/health`, verify HTTP 200 and response JSON. Does not post attendance. |
| INT-06 | `int_full` | Every connected component except OLED/LEDs, safe measured rails, isolated test LAN/backend | Combines RTC, R307S, Wi-Fi and backend diagnostics with the read-only sensor probe. It is not the production attendance workflow and does not POST events. |
| INT-07 | `production` | Individually verified sensor/RTC/storage; synthetic provisioned device and pending student; isolated local backend | Exercise serial enrollment, live event POST, API ack, disconnect/reboot/reconnect and stable-UUID queue replay. Verify DB outcomes and no raw template/image; physical test not run here. The OLED and indicator LEDs were removed from this project, so there is no display/LED verification path; status is reported on the serial console. Never target a production service. |

Removed integration environments: `int_oled`, `int_outputs`, and `int_r307s_oled` no longer exist because the SSD1306 OLED and the green/red LEDs (and their series resistors) were removed from this project. GPIO18 and GPIO19 are unused/reserved.

`backend_http` and `int_backend` are read-only. INT-10 uses the production firmware and must use a temporary synthetic database/device/student; there is no compile-time test lock on API destination, so inspect `local_config.h` carefully before connecting. Never use a real deployment. The queue's crash/replay claims remain unverified until INT-10 is executed and recorded.
