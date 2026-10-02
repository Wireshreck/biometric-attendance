---
type: project-navigation
status: IN PROGRESS
updated: 2026-10-02
---

# 06 - Firmware Plan

[[00 - Project Overview|⬅️ Hub]] | [[05 - Software Stack|Stack ⬅️]] | [[07 - Backend Plan|Backend ➡️]]

**Current state:** read-only R307S diagnostic and independent component/integration test environments are preserved. The production runtime now implements matching, explicit enrollment, RTC-gated attendance events, LittleFS journal/replay, Wi-Fi/API requests, and recovery reporting. Production source builds; physical component and end-to-end evidence remain unverified. R307S currently returns no bytes in the owner report, with rail/TX level unmeasured.

- Current R307S report: owner says red/VIN, black/GND, yellow/GPIO32 RX, green/GPIO33 TX, blue/white disconnected; prior diagnostics got 0 response bytes. Rail, signal voltage and module health remain **UNVERIFIED — REQUIRES MULTIMETER**.
- Current UART map: GPIO32 RX / GPIO33 TX; GPIO16/17 in older documents is superseded. See `docs/esp32-pin-map.md`.
- Production modules: `firmware/src/app/`, `firmware/src/hardware/`, `firmware/src/network/`, and `firmware/src/storage/`.
- Enrollment is an explicit USB serial `ENROLL <student-uuid>` command. Local `SETTIME` sets the RTC; ordinary matching cannot enter enrollment mode.
- Successful code compilation does not establish physical matching, queue persistence, Wi-Fi, or API communication. See `docs/production-firmware.md` for semantics and limitations.

## Development sequence

1. Run the isolated component builds/tests in `docs/component-tests.md`; capture physical evidence in `hardware/test-plan.md`.
2. Run staged combinations from `docs/integration-tests.md` after their component prerequisites pass.
3. Complete safe sensor communication/enrollment/search tests with synthetic adult testers and controlled template slots.
4. Test LittleFS power-loss/corrupt/full/outage/replay behavior and the exact backend device-client contract on a synthetic local database.
5. Keep UI generic and show “Saved locally” only after durable write; show attendance success only after backend acceptance.

References: [firmware architecture](../../docs/production-firmware.md), [test plan](../../docs/hardware-test-plan.md), [hardware map](../../docs/esp32-pin-map.md), [wiring safety](../../docs/power-and-safety.md), [backend contract](../../docs/api-plan.md).
