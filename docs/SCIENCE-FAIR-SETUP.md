---
type: setup
area: science-fair
status: planned
tags:
  - setup
  - science-fair
  - logistics
---
# Science fair setup and transport

**Status:** Planning checklist for a local demonstration. The device's complete physical workflow is not verified; keep the demonstration honest and use synthetic records only.

## Pack

- ESP32 DevKit and USB data cable
- R307S sensor and its connector/harness, with blue/white ends insulated as currently reported
- OLED and DS3231 modules, LEDs with series resistors, buzzer module, breadboard, jumper wires
- Laptop, charger, spare known-good USB data cable, and labeled storage device containing the repository backup
- Printed [pin map](final-pin-map.md), [assembly guide](COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md), and [hardware test plan](hardware-test-plan.md)
- Multimeter if available for safe voltage/continuity verification; do not perform uncertain probing
- Local backend `.env`, firmware `local_config.h`, and database backup stored securely and separately from source control
- Synthetic test roster only; never bring real student biometric or attendance data

## Before leaving

1. Run backend tests and firmware builds on the laptop; retain the output as software evidence.
2. Back up the local backend database and confirm it can be copied/restored using the project backup procedure.
3. Check `.env`, `local_config.h`, and any database backup are private; do not include them in a public repository/USB shared with others.
4. Do not flash a filesystem image if pending attendance is present; `uploadfs` erases the device queue.
5. Mark the current R307S connection and zero-byte response in `hardware/test-plan.md`; do not call it a working sensor.

## Venue startup

1. Place the breadboard on a nonconductive, stable table and inspect wiring with USB disconnected.
2. Verify module labels, common ground, I2C 3.3 V pull-ups, LED resistors, and the exact RTC coin-cell charging design. Leave an uncertain CR2032 out.
3. Do not change the current R307S harness or power it from the coin cell. If its voltage has not been measured, stop before a test requiring safe UART connection.
4. Connect ESP32 USB only; keep other power supplies disconnected.
5. Run `esp32_core`, then `i2c_scan`, OLED, RTC, outputs, UART loopback with the sensor disconnected, and only then R307S if its electrical safety gate is satisfied.
6. Start backend on private LAN, check `/health`, then run the read-only `backend_http` test.
7. Run production only after synthetic device provisioning and all required hardware tests. Open serial monitor and run `STATUS`.

## Demonstration order

1. Introduce the local-first design: fingerprint template remains on the sensor; backend receives only sensor slot, event UUID, timestamp and synchronization state.
2. Show boot/device status and RTC time; explain any component that has not passed its physical test.
3. If sensor is verified and a synthetic pending user enrolled, demonstrate a match, local durable queue write, server acknowledgement, and dashboard/API record. The current firmware task does not create a browser dashboard; API inspection is the current software view.
4. Demonstrate offline mode only using an isolated synthetic device and a deliberate network interruption. Confirm local queue then restore Wi-Fi and observe the same UUID replay.
5. Show test/build evidence separately from hardware evidence. Never stage fabricated successful scans.

## Recovery

- **R307S no response:** stop. Do not guess or declare dead. Preserve wiring, note the exact module/pad marking, check UART loopback separately, then get safe multimeter readings for sensor VIN and TX idle level. Leave sensor disconnected from GPIO if its output may exceed the ESP32 input limit.
- **No network:** use the local durable queue if production is otherwise verified; if attendance event delivery cannot be demonstrated safely, explain it and show synthetic backend tests instead. Do not pretend synchronization occurred.
- **Backend unavailable:** check laptop IP/network profile, process startup and `/health`; do not expose the local API publicly. Restart only after ensuring the local database path is correct.
- **RTC invalid:** do not accept timestamps until explicitly set and checked against a trusted clock.
- **Queue/storage error:** do not run `uploadfs` when pending data may exist. Preserve the board and log the error for recovery.
- **Power instability:** disconnect USB if heat, smell, repeated resets or unexpected behavior occurs; inspect only while unpowered.

## Science fair documentation

See [science fair overview](science-fair.md), [timeline](science-fair-timeline.md), [complete software setup](COMPLETE-SOFTWARE-SETUP.md), and [failure modes](failure-modes.md). The full R307S + RTC + offline recovery demonstration remains NEEDS HARDWARE until physically tested.
