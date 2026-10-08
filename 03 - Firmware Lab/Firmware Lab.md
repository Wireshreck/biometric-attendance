---
type: firmware
area: firmware
status: active
tags:
  - firmware
  - platformio
  - esp32
  - state-machine
---

# 03 - Firmware Lab

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[02 - Hardware Lab]] [[04 - Backend Server Room]] [[05 - Testing Lab]] · **CANVAS** [[03 - Firmware Lab/03 - Firmware Lab.canvas]]

The terminal runtime. ~1,150 lines of C++ across five modules, plus 25 isolated diagnostic images.

**Status: BUILD PASS.** `production` compiles and links — RAM 13.3%, Flash 66.0%. **No physical component has ever been exercised by this firmware.**

> The R307S this firmware talks to is **UNVERIFIED — REQUIRES MULTIMETER**: assembled per owner report, 0 valid bytes received, supply rail and TX logic level never measured. A working build is not a working sensor.

---

## The module graph

```text
main.cpp
  └─▶ app/attendance_app.cpp      lifecycle · state machine · serial operator
        ├─▶ app/attendance_state.cpp     state names
        ├─▶ hardware/device_services.cpp  RTC · buzzer · R307S (OLED/LEDs removed)
        │       └─▶ Adafruit_Fingerprint on HardwareSerial(2)
        ├─▶ storage/attendance_store.cpp  LittleFS CRC32 journal · acks · compaction
        └─▶ network/network_service.cpp   Wi-Fi · HTTP · bearer auth · contract
                └─▶ POST /api/v1/attendance  →  FastAPI
```

`r307s_uart_diag.cpp` sits beside all of this as a **read-only bring-up diagnostic** — retained deliberately, used by the `r307s` and `int_r307s*` environments, and scheduled for removal once a verified driver supersedes it.

---

## The state machine

```text
BOOT ─▶ SELF_TEST ─▶ ┬─▶ READY
                     ├─▶ WAITING_FOR_FINGER ─▶ IDENTIFYING ─▶ ATTENDANCE_RECORDED ─▶ SYNCING
                     ├─▶ ERROR            (RTC invalid · storage error · sensor absent)
                     ├─▶ OFFLINE          (queued locally, retrying)
                     └─▶ RECOVERY         (bounded sensor handshake retry)
```

Source: `firmware/include/attendance_state.h`

The design rule that matters: **the firmware never fabricates a fact.** No valid RTC → no timestamp, so no event. No durable write → no "saved locally". No API acknowledgement → no "attendance OK". Sensor missing → explicit `SENSOR NOT FOUND` with a 5-second bounded retry, never an infinite wait.

---

## Hardware services

| Service | Hardware | Key behaviour |
|---|---|---|
| `DisplayService` | removed | OLED/SSD1306 removed from this project. Status is serial-console only. |
| `RtcService` | DS3231 I2C 0x68 | Refuses to produce a timestamp unless the year is 2024–2099 and the oscillator has not lost power. Wall time + `+05:30` |
| `IndicatorService` | GPIO27 (buzzer); GPIO 18/19 reserved (OLED/LEDs removed) | Short/success/error/two-beep patterns; BUZZER_TEST |
| `FingerprintService` | R307S UART2 | `verifyPassword` handshake, `getImage → image2Tz → fingerFastSearch`, two-capture `enroll` |

> [!NOTE] `firmware/include/fingerprint_sensor.h` is an **11-line DEPRECATED notice**, not an interface. It declares nothing and no production source includes it. Do not mistake it for a second driver.

---

## The offline journal

`firmware/src/storage/attendance_store.cpp` — the most safety-critical code in the repository.

```text
/attendance.jsonl     append-only, one JSON object per line
                      line = <json>\t<CRC32 of json>\n
                      {"kind":"event","uuid","slot","captured_at","sync_status"}
                      {"kind":"ack","uuid"}
```

| Guarantee | Mechanism |
|---|---|
| Never auto-format | `LittleFS.begin(false)`; a failed mount is `STORAGE ERROR`, not a wipe |
| Torn tail is not data | An unterminated final line is treated as a power-loss truncation, never as a record |
| Corrupt middle record is fatal | A complete-but-invalid line fails storage **closed** |
| Overflow is visible | 100 pending / 48 KiB hard bounds; no "saved" claim past them |
| Compaction is crash-safe | temp → backup-rename → swap → remove backup |
| Replay is idempotent | The **same** `event_uuid` is resent, so the backend suppresses the duplicate server-side |

Source: [[docs/production-firmware.md]] · [[docs/failure-modes.md]]

---

## Operator serial console

UART0 at 115200, on the USB port.

| Command | Effect |
|---|---|
| `HELP` | list commands |
| `STATUS` | `state=… sensor=… rtc=… storage=… wifi=… pending=…` |
| `SETTIME YYYY-MM-DD HH:MM:SS` | Set DS3231 **local** wall time (assumed +05:30). No NTP. Compare to a trusted clock first |
| `ENROLL <student-uuid>` | Explicit two-capture enrollment. Requires an available sensor **and** an online backend assignment |

Enrollment is deliberately *not* reachable from a scan. The backend must already hold a `PENDING_ENROLLMENT` student with a reserved slot. After the sensor stores the template, a checksummed NVS intent records the completion obligation and is retried on boot; the intent is cleared only once the backend returns the student as `ACTIVE`.

---

## Network client

`firmware/src/network/network_service.cpp` implements exactly three calls, and all three match `backend/app/main.py`:

| Call | Endpoint | Auth |
|---|---|---|
| `sendAttendance` | `POST /api/v1/attendance` | `Bearer <device token>` |
| `enrollmentAssignment` | `GET /api/v1/devices/{uuid}/enrollment/{student}` | `Bearer` |
| `enrollmentComplete` | `POST …/enrollment/{student}/complete` | `Bearer` |

Acceptance requires a `201 RECORDED` or `200 DUPLICATE_SUPPRESSED` **with a matching `event_uuid`**. Anything else leaves the event queued. One oldest pending event is retried every 10 s while connected.

Credentials live in ignored `firmware/include/local_config.h`; the tracked example is empty. HTTP is plaintext — synthetic data on an isolated LAN only.

---

## Build environments

27 total: `production` (default), `esp32dev` (compatibility alias), 15 component, 9 integration. See [[05 - Testing Lab]].

```bash
pio run -d firmware -e production              # build
pio run -d firmware -e production -t upload --upload-port COM4
```

> Cosmetic debt: `[env:production]` still filters `+<fingerprint/*.cpp>` and no `firmware/src/fingerprint/` directory exists. PlatformIO ignores the unmatched filter, so the build is unaffected.

---

## Documents

[[docs/production-firmware.md]] · [[docs/failure-modes.md]] · [[docs/final-pin-map.md]] · [[docs/component-tests.md]] · [[docs/integration-tests.md]] · `firmware/README.md`

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[02 - Hardware Lab]] [[04 - Backend Server Room]] [[05 - Testing Lab]] · **CANVAS** [[03 - Firmware Lab/03 - Firmware Lab.canvas]]
