---
type: firmware
area: firmware
status: active
tags:
  - firmware
  - architecture
---
# Production firmware behavior

**Status:** Runtime workflows are IMPLEMENTED and production image is BUILD-VERIFIED. Physical component, network, crash-recovery, enrollment, and attendance integration are NEEDS HARDWARE / NEEDS TESTING. A compile is not proof of working hardware.

## Architecture

- `firmware/src/app/attendance_app.cpp`: lifecycle, state transitions, serial operator commands, event creation, dispatch and retry scheduling.
- `firmware/src/hardware/device_services.cpp`: OLED, RTC, indicators/buzzer, and Adafruit sensor wrapper.
- `firmware/src/network/network_service.cpp`: station Wi-Fi, local HTTP API authentication, contract payload, response validation, enrollment assignment/completion.
- `firmware/src/storage/attendance_store.cpp`: LittleFS append journal with CRC32, acknowledgements, bounded size/count and compaction; damaged middle records fail closed, incomplete last write is ignored.
- `firmware/src/r307s_uart_diag.cpp`: retained read-only diagnostic; no enrollment/delete commands in this diagnostic.
- `firmware/include/config.h`: pin/time/retry/queue settings and optional ignored `local_config.h`.

The backend contract is authoritative. Attendance sends `{event_uuid,fingerprint_slot_id,captured_at,sync_status}` with `Authorization: Bearer <device token>` to `POST /api/v1/attendance`. A 201 `RECORDED` or 200 `DUPLICATE_SUPPRESSED` response with matching event UUID acknowledges/removes the queue entry. Other responses leave it pending. Retries retain the same event UUID, preserving backend idempotency. Old queued events use `REPLAYED_OFFLINE`; fresh immediate requests use `LIVE`.

## Startup and attendance lifecycle

Boot initializes indicators, OLED/I2C, RTC, LittleFS, Wi-Fi, and fingerprint UART. LittleFS mount uses formatting disabled. If the RTC is stopped/invalid, storage is unavailable, or the sensor does not answer, the firmware reports the fault and avoids making up a timestamp or claiming a scan was recorded. Sensor handshake retries every five seconds. Wi-Fi reconnect attempts are spaced ten seconds apart.

For a valid match, the firmware reads a local DS3231 timestamp, formats it with the configured `+05:30` offset, creates a UUIDv4, and appends the event to LittleFS before network submission. A durable write is required before the OLED can say “Saved locally.” API acknowledgement is required before “Attendance OK.” The finger must be lifted before a new scan is accepted. The backend applies its existing 60-second duplicate policy. The OLED and serial output do not display student names; serial logs include the event UUID and slot, so keep the local serial console access-controlled.

The RTC stores wall time. The operator can set it explicitly through local USB serial: `SETTIME YYYY-MM-DD HH:MM:SS`. This sets local time assumed to be India Standard Time (`+05:30`); compare to a trusted clock before using it. There is no NTP time correction or DST logic. Invalid dates are rejected. No timestamp is generated from compile time or uptime.

## Explicit enrollment

Enrollment requires local serial command `ENROLL <student-uuid>`. The backend must already have a pending student and reserved slot. The device requests the exact assignment, prompts for two captures, rejects an impression already found in another template slot where the sensor reports it, creates/stores the template, then posts the existing enrollment completion schema. Ordinary attendance scans never enroll.

After sensor storage succeeds, a checksummed NVS intent stores the student UUID and slot before backend completion. If the completion call fails or power is lost, boot retries it. The intent is removed only after the backend returns the matching student as ACTIVE. If NVS write fails after the sensor stored the template, firmware warns not to reuse that slot; local repair is required. There is no remote enroll/delete operation and no raw image/template crosses the API.

## Offline queue and recovery

Each queue line contains compact JSON plus a CRC32. Complete lines are parsed in order; an acknowledgement line follows a successful API response. A torn final line is ignored as an incomplete append; a malformed complete record fails storage closed. The append-only file is compacted to unacknowledged events after acknowledgements dominate, using a temporary and backup rename recovery sequence. The maximum is 100 pending records and 48 KiB. At capacity or if LittleFS cannot mount/read, new attendance is not claimed as saved. The journal stores slot number, UUID and timestamp/status only; it holds no fingerprint image/template or student profile.

The accepted event is sent immediately. If no acceptable acknowledgement arrives, it remains queued. One oldest pending event is retried every ten seconds when Wi-Fi is connected. Server conflicts/validation failures remain queued for operator investigation; they are not silently discarded. Backend duplicate suppression is idempotent at server receipt. LittleFS does not encrypt the event journal; physical access to the device can expose slot/time metadata. The bearer token is plaintext in firmware config and HTTP on the LAN. Use only synthetic data and an isolated private network; this MVP is not suitable for real student records or public networks.

## Local setup

1. Verify the actual sensor pin/voltage constraints before leaving R307S attached; the current sensor returns zero valid bytes and rail/TX voltage are unmeasured.
2. Set up backend locally and provision one device with `python -m app.provision_device --name "Demo ESP32" --location "Local lab" --sensor-capacity N`. `N` must be an actually verified sensor capacity; do not provision while sensor capacity is unknown.
3. Copy `firmware/include/local_config.example.h` to ignored `local_config.h`, then enter local test Wi-Fi credentials, backend host/port, UUID and token. Keep the token private.
4. On a new ESP32 filesystem only, run `pio run -d firmware -t uploadfs --upload-port COMx` before attendance data exists. This erases/formats LittleFS. Do not use it after events may have queued.
5. Build/upload production: `pio run -d firmware -e production`; `pio run -d firmware -e production -t upload --upload-port COMx`. Monitor: `pio device monitor -d firmware --port COMx --baud 115200`.
6. Verify RTC time with `STATUS`; if stopped, set using explicit `SETTIME` and compare to trusted source. Test on synthetic student/device records in an isolated backend before demonstration.

## Verification status

Production build passes PlatformIO on the current toolchain. Backend tests pass using its virtual environment. No firmware upload or component physical test has occurred in the current work. In particular, no claim is made that sensor matching/enrollment, RTC accuracy, LittleFS reboot behavior, Wi-Fi reconnect, HTTP sync, queue replay or complete assembly passes on the actual board. Follow [component tests](component-tests.md), [integration tests](integration-tests.md), [hardware plan](hardware-test-plan.md), and [failure modes](failure-modes.md).
