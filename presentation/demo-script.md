# Demonstration Script (Conditional Draft)

**Do not present planned steps as working features.** Use real hardware only after its bring-up gates and end-to-end tests pass. Otherwise use the labeled fallback in each stage.

## Preparation

- Synthetic demo database only; no real student information.
- Adult tester explicitly consents; use a temporary sensor enrollment and clear it afterward.
- Isolated 2.4GHz WPA2 demo network, unique local password; local service credentials, correct host IP, firewall restricted, no port forwarding.
- Verify power rails, RTC, fingerprint sensor, API health, DB, SSE/dashboard and backup restore. Save tested commit/build ID and measured evidence.
- Keep static architecture/walkthrough ready. Never promise live scan or offline recovery unless that exact setup passed.

## Live sequence (only when verified)

1. **Start:** power laptop/network/service/device; show health and demo date/time. If any health gate fails, switch to fallback.
2. **Enroll:** create a synthetic test record, use authorized USB serial enrollment for two impressions, confirm API marks it active only after sensor confirmation.
3. **Scan:** one consenting adult scan; show generic terminal prompt and the accepted event in dashboard/database by event UUID.
4. **Duplicate:** scan again within 60s; show `DUPLICATE_SUPPRESSED`, not a second accepted presence event. If boundary test was not run, describe the planned rule only.
5. **Report:** show authorized daily aggregate/CSV for the synthetic date range; describe measurement and privacy scope.
6. **Failure/recovery:** disconnect local network, scan, verify durable offline save, restore, verify same UUID reconciles once. Do not force an untested power-cut.
7. **Close:** show limitations and clear temporary records/template after the fair.

## Fallbacks

- Hardware/sensor failure: use a clearly labeled prerecorded clip or static flow diagram; say the device did not work live.
- Wi-Fi/API failure: present verified local-only sensor/firmware behavior if available, otherwise static walkthrough; no dashboard-sync claim.
- Laptop/power failure: switch to printed architecture and measurements. A second laptop is usable only after a successful restore/network test.
- No measured results: explain test plan and report “not yet measured.” Never invent recognition rate, latency, attendance savings, or reliability.
