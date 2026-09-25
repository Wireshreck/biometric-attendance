# Security Policy

## Project status and scope

Biometric Attendance is an early educational prototype. It contains a partial FastAPI/SQLite attendance API, but no terminal firmware workflow, dashboard, or integrated product; it has not had an independent security audit. Use synthetic data only. It is not approved for live school, workplace, or public-institution deployment.

## Sensitive data rules

- Never commit passwords, API tokens, private Wi-Fi credentials, student data, fingerprint images, or template bytes.
- Do not send fingerprint images/templates to the backend, cloud services, issue trackers, or AI systems.
- The checked-in Wi-Fi password is intentionally empty. Configure local credentials without committing them.
- Treat slot IDs, attendance, roll numbers, names, logs, CSV exports, and backups as sensitive when linked to an individual.
- The backup helper creates a ZIP and does **not** encrypt it. Do not use it for real personal data without encrypting and testing the archive separately.

See [privacy and security design](docs/privacy-security.md) for boundaries, limitations, retention, and the production gate.

## Reporting a vulnerability

Do not publish credentials, personal information, or exploit details in a public issue. Until a private security contact is established, contact the repository maintainer through the private channel associated with the configured repository host. Include affected files/components, impact, and safe reproduction steps. Do not include real biometric/student data.

No response-time or coordinated-disclosure guarantee is currently established; there is no confirmed security response team.

## Known limitations

- Prototype device bearer-token and admin HTTP Basic checks are implemented for a limited API subset. They have not been independently audited; plain HTTP exposes credentials on the network and is suitable only for synthetic data on an isolated demo network.
- Planned local HTTP is not encrypted end-to-end; demo use is limited to an isolated network and synthetic data.
- SQLite and ZIP backups are not application-encrypted; the host filesystem needs appropriate protection.
- Exact sensor template properties and spoof resistance have not been verified. No mathematical irreversibility or liveness guarantee is claimed.
- Retention, consent, deletion, jurisdictional compliance, flash protection, secure boot, and production provisioning are unresolved.
