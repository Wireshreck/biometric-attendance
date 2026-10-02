# Firmware Integration Tests

**Status:** Integration diagnostic entry points and PlatformIO environments are implemented; physical execution is **NOT EXECUTED** here. The separate `production` image contains the attendance workflow, but a build is not evidence that attached devices work.

From the repository root, build/upload each environment with:

```powershell
pio run -d firmware -e int_oled
pio run -d firmware -e int_oled -t upload
pio device monitor -d firmware -b 115200 --port COM3
```

| ID | Environment | Prerequisites | Expected result / limits |
|---|---|---|---|
| INT-01 | `int_oled` | ESP32 + SSD1306 on mapped I2C | OLED initializes and displays integration label. |
| INT-02 | `int_rtc` | ESP32 + DS3231 | I2C responds, time plausible, oscillator not stopped. No time write. |
| INT-03 | `int_outputs` | LEDs with resistors and suitable buzzer driver | Executes green/red/buzzer sequence; human must confirm physical light/sound. |
| INT-04 | `int_r307s` | Existing R307S connection; only after power/logic safety gate | Runs existing read-only diagnostic; no enrollment/deletion. No response is not proof of dead sensor. |
| INT-05 | `int_r307s_oled` | R307S + OLED | OLED comes up then read-only sensor probe runs; validates their independent interfaces in one image. |
| INT-06 | `int_r307s_rtc` | R307S + DS3231 | RTC does not supply a timestamp to sensor test; read-only sensor probe remains independent. |
| INT-07 | `int_wifi` | Isolated 2.4 GHz network; optional ignored config | Scans; optional DHCP/RSSI check when credentials are configured. Does not print SSIDs. |
| INT-08 | `int_backend` | Test Wi-Fi and locally running project backend | GET `/health`, verify HTTP 200 and response JSON. Does not post attendance. |
| INT-09 | `int_full` | Every connected component, safe measured rails, isolated test LAN/backend | Combines diagnostics and read-only sensor probe. It is not the production attendance workflow and does not POST events. |
| INT-10 | `production` | Individually verified sensor/RTC/OLED/outputs/storage; synthetic provisioned device and pending student; isolated local backend | Exercise serial enrollment, live event POST, API ack, disconnect/reboot/reconnect and stable-UUID queue replay. Verify DB outcomes and no raw template/image; physical test not run here. Never target a production service. |

`backend_http` and `int_backend` are read-only. INT-10 uses the production firmware and must use a temporary synthetic database/device/student; there is no compile-time test lock on API destination, so inspect `local_config.h` carefully before connecting. Never use a real deployment. The queue's crash/replay claims remain unverified until INT-10 is executed and recorded.
