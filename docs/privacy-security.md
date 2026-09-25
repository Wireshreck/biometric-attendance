# Privacy and Security Design

**Status:** PLANNED — intended controls only; no production security controls have been implemented or independently audited. The MVP is for a synthetic-data science fair demonstration, not live school attendance.

## Data boundaries

- Fingerprint capture, matching, and template storage are intended to remain inside the AS608 module. Firmware should send only a matched integer slot ID and event metadata. The host API/database must never request, accept, log, export, or back up raw images or template bytes.
- This is an application design constraint, not a verified guarantee about every sensor revision or its proprietary template format. Do not claim templates are mathematically irreversible or impossible to reconstruct. Confirm the exact module documentation and firmware behavior; physical access to the sensor may expose or erase on-module templates.
- A slot ID is pseudonymous, not anonymous: linked to a student's identity and attendance, it is sensitive personal data. Attendance records, roll numbers, names, device tokens, and backups require protection.
- Collect only the identity fields needed for the demo. Use synthetic attendees. No real student or biometric data in tests, screenshots, issue trackers, logs, or presentation materials.

## MVP controls (planned)

- Device token: random high-entropy per-device bearer token; store only its hash server-side. Revoke device tokens by changing device state. Never embed production credentials in source. The checked-in Wi-Fi password setting is empty; configure a private value locally.
- Admin access: local environment-backed credentials for the prototype. Static-file UI/API on plain HTTP does not protect credentials from other clients on the network. Use only an isolated WPA2 demo network and synthetic data. Do not treat Wi-Fi encryption as end-to-end transport security.
- Bind service only as broadly as needed for the isolated demo network; firewall the host, do not port-forward, and stop the service after use. `0.0.0.0` exposes it to every reachable interface.
- Validate all payloads, limit request/body sizes and date ranges, use parameterized SQL, restrict CORS to the served origin, and never expose database files or stack traces.
- Do not store secrets in browser local storage. Do not put identity details, tokens, full request bodies, fingerprint data, or exported CSV contents in logs.
- Admin audit log is useful operational evidence but is not tamper-proof against a host administrator. Do not describe it as immutable.
- Use SQLite online backup API; the current ZIP backup script does not encrypt archives. Keep sensitive backups off by default; encrypt any backup that contains real personal data and verify restoration.

## Retention, deactivation, deletion

The 365-day period in earlier planning was not institutionally approved and must not be treated as a valid live-school retention rule. For the demo, use synthetic data and delete database/backups after the project. A real deployment requires a documented lawful purpose, retention schedule, consent/notice, authorized deletion procedure, and institution/privacy/legal approval. Deactivation stops future attendance; it is not deletion. Sensor slot cleanup must be confirmed physically before slot reuse.

## Known prototype limitations

- AS608 liveness/spoof resistance is unknown for the exact unit; assume spoofing may be possible. Measure only with safe, consented test artifacts and do not infer production FAR/FRR from a small demo.
- HTTP over a shared/local LAN is not encrypted end-to-end; bearer tokens can be replayed by an observer. The planned MVP is not suitable for real student data.
- One shared administrator credential does not provide robust identity, role-based access, recovery, or non-repudiation.
- Laptop filesystem and SQLite database are not encrypted by the application. Physical host access exposes data.
- Firmware secrets can be extracted from an unprotected device; flash encryption/secure boot provisioning is not implemented.
- Local audit records can be edited by a host administrator; no centralized monitoring or alerting is implemented.
- No jurisdictional compliance has been established. Educational demonstration is not authorization to deploy biometrics in a school.

## Production gate (out of scope)

Before any institutional use, require a privacy impact assessment and jurisdiction-specific review, informed consent/notice, TLS and secure device provisioning, strong admin identity and least privilege, key rotation, encrypted storage/backups, tested deletion/retention, tamper-evident audit, threat modeling, independent security assessment, documented incident response, and verified sensor capabilities. Do not rely on this prototype plan as legal advice or as evidence of compliance.
