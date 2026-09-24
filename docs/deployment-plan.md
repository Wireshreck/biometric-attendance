# Local Demo Deployment Plan

**Status:** Future runbook; the backend app/dashboard/attendance firmware do not exist yet. Do not attempt to follow this as a working demo recipe until implementation gates pass. Development setup: [environment](environment.md).

## Target topology

An isolated 2.4GHz laptop hotspot or travel router connects the ESP32 and host laptop. The laptop runs FastAPI, local SQLite, and serves the dashboard. Internet access is unnecessary. Device transport is currently planned over HTTP; therefore use synthetic data only, a unique demo passphrase, no port forwarding, and host firewall rules scoped to the demo network.

## Intended run sequence after implementation

1. Verify backup restoration and confirm the database contains only synthetic demo records.
2. Start isolated WPA2 network; record current laptop LAN IP. Do not reuse the sample IP/SSID as assumptions.
3. Set local firmware configuration in ignored `firmware/include/local_config.h`; create backend `.env` from its example with unique demo credentials. Do not commit either file.
4. Start service with LAN binding only as required; confirm `GET /health` and check Windows Firewall scope.
5. Open dashboard from the host browser; verify service/SSE state and synthetic student list.
6. Power the ESP32 from a measured suitable 5V USB supply; confirm sensor/RTC status and valid time.
7. Enroll only a consenting adult synthetic test identity through local USB serial procedure; verify assigned sensor slot.
8. Scan once, verify one accepted event UUID in API/DB/dashboard. Repeat within 60s to see suppression, then after 60s if testing the boundary policy.
9. Disconnect network, scan, confirm “saved offline” only after LittleFS persistence; restore network and verify the same UUID is stored once.
10. Stop service, export/backup if required, shut down hardware, and clear test database and sensor template after the demonstration.

## Degraded demo fallbacks

- Hardware or sensor failure: show the architecture, code, and clearly labeled recorded video/mock trace; do not claim a live scan occurred.
- Wi-Fi/backend failure: use an isolated direct hotspot/router alternate if previously tested. Otherwise switch to the offline sequence and state that dashboard sync is unavailable.
- Laptop failure: use a separate machine only after restore test, environment installation, local config recreation, and network IP change. No source backup contains Wi-Fi credentials.
- Power failure: use a tested, regulated USB power bank/adapter. Do not hot-rewire a powered breadboard.
- No actual database/hardware behavior is guaranteed until measured and logged in the test plan.
