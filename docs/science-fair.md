# Science Fair Project Plan

**Event target:** 2026-10-09. **Project state:** early implementation; SQLite schema v1 exists, but no attendance product or measured demo results are claimed. Update claims only from test evidence.

## Question and motivation

**Engineering question:** Can a low-cost ESP32 + optical fingerprint module record a synthetic attendance event locally and recover from a local network outage without sending fingerprint image/template data to the laptop service?

Motivation is to study a technical trade-off: biometric convenience versus privacy, reliability and cost. Claims about time saved by schools, commercial product pricing, or comparative accuracy need cited research and are intentionally omitted until researched.

## Proposed solution (not yet implemented)

An ESP32/R307S terminal firmware implements local matching/enrollment, metadata-only event submission to FastAPI/SQLite on a laptop, a LittleFS offline queue, RTC timestamps and local status display. These workflows compile, but the owner-reported R307S currently returns zero UART bytes and exact power/logic levels are unmeasured, so no complete physical demonstration is verified. A browser dashboard and reports remain planned. Use synthetic identities and adult-consented testers only. The optional local AI report explainer is deferred. See [transport and demo setup](SCIENCE-FAIR-SETUP.md).

## Scientific method and experiments

| Experiment | Measurement | Sample/controls to define before run |
| --- | --- | --- |
| Enrollment success | Successful two-impression enrollments / attempts | Consenting adult testers; record module firmware and failures |
| Recognition reliability | Genuine accepts, genuine rejects, impostor accepts/rejects | Predefine consent and safe protocol; do not claim population FAR/FRR from a small sample |
| Response latency | Finger contact to local feedback; backend commit to UI event | Timestamp method, hardware/network setup, >=30 trials for summary |
| Duplicate boundary | outcomes at 59, 60, 61 seconds; same UUID replay | fixed synthetic identities and event timestamps |
| Offline resilience | queued UUIDs versus stored UUIDs after outage/restart | test Wi-Fi/API loss separately; account for queue capacity |
| Power interruption | DB integrity and queue recovery after controlled interruption | synthetic data only; safe controlled power removal |
| Backup recovery | restore duration, integrity checks, row-count equality | separate temporary restore destination |

Report actual sample count, failures, setup, and uncertainty. Blank results remain “not measured”; do not estimate them in the presentation.

## Booth / demo plan

Laptop + isolated local Wi-Fi and one breadboard terminal, if hardware gates pass. Explain architecture, privacy boundary, limitations and measurements. Do not use a real student or store/share biometric artifacts. Fallback is a clearly labeled code/architecture walkthrough or prerecorded/mock trace, never described as a live system.

See [timeline](science-fair-timeline.md), [demo script](../presentation/demo-script.md), and [judge questions](../presentation/judge-questions.md).
