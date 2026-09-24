# Anticipated Judge Questions (Evidence-Led Draft)

Use “planned” for design documents and “verified” only when test evidence exists. The project is currently in pre-development; answers below do not claim an operational system.

### What problem are you studying?

We are investigating whether a low-cost local biometric attendance demonstrator can keep matching at the edge, send only event metadata to a local service, and recover from a network outage. We have not quantified school time savings or compared commercial product prices.

### What is built today?

The repository contains plans, a configured PlatformIO toolchain-check sketch, environment setup and a static dashboard architecture decision. Product enrollment, matching loop, API, database schema migrations, dashboard, and offline sync are not implemented yet. Add only verified work here after testing.

### Why fingerprint rather than RFID or face recognition?

Fingerprint matching is a chosen experiment, not a claim that it is inherently safer or more accurate. RFID can be shared; face recognition would add camera data and different privacy/bias risks. All biometric options involve sensitive data and require consent and institutional review for real use.

### Where is biometric data stored?

The intended design keeps image capture/matching and template storage in the sensor, with only the matching slot ID leaving it. The exact sensor capabilities and template properties are not independently verified; the database would still hold sensitive identity-linked attendance and slot references. We do not claim templates are mathematically irreversible.

### What does the network outage behavior do?

The plan uses a durable LittleFS queue with a stable event UUID and replay after reconnection. That queue is not implemented or tested yet; we will demonstrate it only if outage/restart tests pass.

### How are duplicate scans handled?

The selected rule suppresses another accepted scan for the same student within 60 seconds. The same event UUID is idempotent across retries; a later same-day scan may be recorded, while daily presence counts the student once. This is planned; test boundary evidence will be reported separately.

### Is the system secure/ready for schools?

No. It is a pre-development science-fair prototype. Planned HTTP is not encrypted end-to-end, authorization is not implemented, sensor spoof resistance is unknown, and retention/compliance are unresolved. Demonstrations use synthetic records and consented adult testers only.

### What results have you measured?

Only report dated results with setup, sample count, and method from the test log. Recognition accuracy, FAR/FRR, latency and reliability are currently not measured. Requirements are targets, not outcomes.

### Why SQLite / vanilla web technology?

They keep a single-host demonstrator simple to run and inspect without a database server or JavaScript build chain. These are design choices; comparative performance has not been measured.

### Is AI required?

No. A possible local aggregate-only read-only explanation layer is deferred. It would not access SQLite directly, modify records, control the device, or send project data to cloud AI.
