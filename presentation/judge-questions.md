---
type: science-fair
area: science-fair
status: planned
tags:
  - science-fair
  - judges
---
# Anticipated Judge Questions (Evidence-Led Draft)

Use canonical status terms and say “verified” only for evidence that exists. The project is in early implementation; these answers do not claim an operational attendance system.

### What problem are you studying?

We are investigating whether a low-cost local biometric attendance demonstrator can keep matching at the edge, send only event metadata to a local service, and recover from a network outage. We have not quantified school time savings or compared commercial product prices.

### What is built today?

The repository contains modular PlatformIO firmware source for enrollment/matching, RTC-qualified events, an offline journal and authenticated API sync, plus SQLite schema v1 and a tested FastAPI API slice. Backend tests pass against synthetic temporary databases. The browser dashboard and reports/SSE remain unimplemented. Firmware compiles, but the R307S currently has no valid reported UART response and the complete physical workflow is not verified. Describe only observed results in a demonstration.

### Why fingerprint rather than RFID or face recognition?

Fingerprint matching is a chosen experiment, not a claim that it is inherently safer or more accurate. RFID can be shared; face recognition would add camera data and different privacy/bias risks. All biometric options involve sensitive data and require consent and institutional review for real use.

### Where is biometric data stored?

The intended design keeps image capture/matching and template storage in the sensor, with only the matching slot ID leaving it. The exact sensor capabilities and template properties are not independently verified; the database would still hold sensitive identity-linked attendance and slot references. We do not claim templates are mathematically irreversible.

### What does the network outage behavior do?

Firmware source uses a bounded LittleFS journal with stable event UUIDs and replay after reconnection. It has not yet been physically exercised across outage/restart; demonstrate that behavior only after the corresponding hardware test passes.

### How are duplicate scans handled?

The backend code suppresses another accepted scan for the same student within 60 seconds; its tests cover the boundary. The same event UUID is idempotent across retries; a later same-day scan may be recorded, while daily presence counts the student once. Device replay integration is not yet physically tested.

### Is the system secure/ready for schools?

No. It is an early-stage science-fair prototype. HTTP bearer traffic is not encrypted end-to-end, sensor spoof resistance is unknown, and retention/compliance are unresolved. Backend admin/device authentication exists in the implemented API slice, but that does not make this prototype suitable for live use. Demonstrations use synthetic records and consented adult testers only.

### What results have you measured?

Only report dated results with setup, sample count, and method from the test log. Recognition accuracy, FAR/FRR, latency and reliability are currently not measured. Requirements are targets, not outcomes.

### Why SQLite / vanilla web technology?

They keep a single-host demonstrator simple to run and inspect without a database server or JavaScript build chain. These are design choices; comparative performance has not been measured.

### Is AI required?

No. A possible local aggregate-only read-only explanation layer is deferred. It would not access SQLite directly, modify records, control the device, or send project data to cloud AI.
