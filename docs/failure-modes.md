# Firmware failure behavior and recovery

| Failure | Detection | Device behavior | Recovery / operator action | Evidence status |
|---|---|---|---|---|
| OLED absent | SSD1306 init false | Serial diagnostics continue; display calls are no-ops | Run `i2c_scan`, check module/3.3 V-safe pull-ups and 21/22 | Physical behavior NEEDS TESTING |
| RTC absent or oscillator stopped | DS3231 not found, lost-power bit, or invalid year | No attendance timestamp is generated; display/serial reports RTC invalid | Inspect I2C/power and explicitly set trusted local time with `SETTIME`; test again | Physical behavior NEEDS TESTING |
| Fingerprint sensor absent/no response | bounded handshake fails | `SENSOR NOT FOUND`; reprobe every 5 seconds; no infinite wait | Run read-only `r307s` diagnostic; verify exact board and safely measure power/logic | Current UART silence reported; sensor health unknown |
| Finger image poor / no match | capture/search result | show `NOT FOUND`; error signal; require finger lift before next attempt | Dry/clean finger and sensor surface; use test fingers | NEEDS HARDWARE |
| Storage mount, checksum, or write failure | LittleFS mount/parser/write/flush failure | storage state unhealthy; new scans are not accepted; never auto-format | Preserve device; inspect serial; do not run `uploadfs` if queue might exist | Software compiles; power-cut behavior NEEDS HARDWARE |
| Queue full | 100 pending or 48 KiB journal bound reached | fail closed, no “saved” claim and no event overwrite | Restore network/API; determine why pending events do not clear; back up/recover before any format | Logic implemented; full-device run NEEDS TESTING |
| Wi-Fi unavailable | station not connected | fingerprint attendance still writes to local queue; reconnect every 10 sec | Verify local 2.4 GHz test network and ignored credentials | NEEDS HARDWARE |
| API unavailable/unauthorized/invalid slot | timeout or response does not match accepted event contract | retain event and same UUID; retry oldest queue record | Inspect local API/device provisioning; correct config/clock/slot; synthetic data only | NEEDS INTEGRATION TEST |
| Enrollment API complete fails after sensor store | response mismatch/timeout | retain checksummed NVS completion intent; retry after boot | Restore network/backend; do not allocate/reuse this template slot | Needs physical/API integration verification |
| NVS intent cannot be saved after template store | putBytes fails | explicit critical warning; enrollment not reported complete | Stop enrollment and manually reconcile sensor slot with pending backend student | NOT TESTED |
| Brownout/reset | boot log reports ESP32 reset reason | restart initialization; journal/ack protocol recovers complete records | Check USB supply/cable and rail with meter; firmware cannot measure voltage | Reset reason is logged; actual supply NEEDS MULTIMETER |

The production build is not evidence for any physical recovery path. Never format LittleFS, clear templates, or send destructive sensor commands as a generic troubleshooting step. See [power and safety](power-and-safety.md) and [production behavior](production-firmware.md).
