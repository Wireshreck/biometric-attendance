# Contributing to Biometric School Attendance System

Thank you for your interest in contributing to this open-source project!

## Development Setup

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/<your-username>/biometric-attendance.git
   cd biometric-attendance
   ```

2. **Set up the firmware environment:**
   ```powershell
   cd firmware
   pio run   # Compile the current toolchain-check sketch
   ```

3. **Set up the backend environment:**
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements-dev.txt
   python test_env.py   # Dependency and temporary SQLite/WAL smoke check only
   ```

## Branch Strategy

- `main` — shared baseline; keep it reviewable
- `feature/<name>` — focused work (firmware, backend, dashboard)
- `fix/<name>` — bug fixes

## Commit Conventions

Use conventional commits:
- `feat(firmware): add offline LittleFS queue replay`
- `fix(backend): prevent duplicate attendance scan within 60s`
- `docs: update wiring pin map for GPIO 23 buzzer`
- `chore: update platformio library versions`

## Important Rules

- **Never commit secrets:** Wi-Fi passwords, API tokens, or device keys must not appear in any committed file. Use `.env` files (excluded by `.gitignore`).
- **Never commit raw fingerprint data or images.**
- **Verify before a PR:** Firmware must compile (`pio run`). Run `pytest` once the product test suite exists; currently only the environment smoke check is present.
- **Hardware changes:** Update `docs/wiring.md` and `hardware/pinout.md` if GPIO assignments change.

## Pull Request Process

1. Open an issue first to discuss significant changes.
2. Create a feature branch from `develop`.
3. Fill in the PR template completely.
4. Ensure CI passes (PlatformIO build + backend environment smoke check).
5. Request review.

## Questions?

Open a GitHub Discussion or check the Obsidian knowledge base at `obsidian/Attendance System/`.
