# Science Fair Presentation Outline (Draft)

**Target:** 3-minute explanation + up to 2-minute demonstration. **Current project state:** planning/toolchain stage. Fill measurements only after tests; omit unimplemented features from the “built” section.

1. **Problem/question (30s):** Explain the engineering question: how to test a local attendance pipeline while minimizing biometric data transfer and surviving a LAN outage. Avoid unsupported claims about school time savings or vendor prices.
2. **Design (40s):** ESP32/AS608 edge match, event metadata only, local API/SQLite, vanilla dashboard, LittleFS offline queue (planned until implemented).
3. **Privacy (30s):** On-sensor matching is the design boundary, not a verified guarantee of irreversibility. Slot IDs linked to attendance are sensitive. Demo data is synthetic. HTTP/local prototype is not school-ready.
4. **Build/experiment (40s):** State exactly which component gates passed. Show wiring, event path, duplicate test and outage/recovery test only if measured.
5. **Results (30s):** Provide measured enrollment/recognition counts and p50/p95 timings with setup and sample size. If unavailable, say “not measured”; do not substitute targets for results.
6. **Limitations/next work (20s):** Sensor liveness, network encryption, authentication maturity, physical validation, queue recovery and retention remain limitations until verified.
7. **Optional demo (up to 2m):** Follow [demo script](demo-script.md); use only consenting adult synthetic test identities. Switch to static explanation if any hardware/service fails.

## Claims gate

Before speaking, compare each “implemented” claim with a test record in [testing plan](../docs/testing-plan.md), the current build/source, and [authoritative tracker](../obsidian/Attendance%20System/TODO.md). No accuracy, response time, cost comparison, zero-loss, compliance, or security guarantee without evidence.
