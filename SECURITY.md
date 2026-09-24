# Security Policy

## Project status and scope

Biometric Attendance is a pre-development educational prototype. The repository does not yet contain the attendance application and has not had an independent security audit. The planned science-fair MVP must use synthetic data only. It is not approved for live school, workplace, or public-institution deployment.

## Sensitive data rules

- Never commit passwords, API tokens, private Wi-Fi credentials, student data, fingerprint images, or template bytes.
- Do not send fingerprint images/templates to the backend, cloud services, issue trackers, or AI systems.
- The checked-in Wi-Fi password is intentionally empty. Configure local credentials without committing them.
- Treat slot IDs, attendance, roll numbers, names, logs, CSV exports, and backups as sensitive when linked to an individual.
- The backup helper creates a ZIP and does **not** encrypt it. Do not use it for real personal data without encrypting and testing the archive separately.

See [privacy and security design](docs/privacy-security.md) for boundaries, limitations, retention, and the production gate.

## Reporting a vulnerability

Do not publish credentials, personal information, or exploit details in a public issue. Until a private security contact is established, contact the repository maintainer through the private channel associated with the configured repository host. Include affected files/components, impact, and safe reproduction steps. Do not include real biometric/student data.

No response-time or coordinated-disclosure guarantee is currently established; the project has no confirmed public repository or security response team.

## Known limitations

- Device/API authentication and administrator authorization are planned, not implemented.
- Planned local HTTP is not encrypted end-to-end; demo use is limited to an isolated network and synthetic data.
- SQLite and ZIP backups are not application-encrypted; the host filesystem needs appropriate protection.
- Exact sensor template properties and spoof resistance have not been verified. No mathematical irreversibility or liveness guarantee is claimed.
- Retention, consent, deletion, jurisdictional compliance, flash protection, secure boot, and production provisioning are unresolved.
