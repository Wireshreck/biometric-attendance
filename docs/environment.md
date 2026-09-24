# Development Environment Setup (Windows / PowerShell)

**Observed host:** Windows 10 Pro x64; Python 3.13.15; Git 2.55.0; PlatformIO Core 6.2.0; GitHub CLI 2.101.0; Node.js is installed but not needed. GitHub CLI is unauthenticated. See the dated [environment audit](environment-audit.md); verify versions locally because host state changes.

## Clean setup order

1. Install Python 3.13, Git for Windows and PlatformIO Core. Node/npm is unnecessary for the selected vanilla frontend. Obsidian is optional for editing the vault.
2. Open PowerShell at the repository root; confirm tools:
   ```powershell
   python --version
   git --version
   pio --version
   gh --version
   ```
3. Build current firmware validation sketch:
   ```powershell
   cd .\firmware
   pio run
   cd ..
   ```
4. Create the isolated backend environment and run the environment smoke check:
   ```powershell
   cd .\backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements-dev.txt
   python test_env.py
   deactivate
   cd ..
   ```
   This verifies dependencies and SQLite/WAL basics; no FastAPI application exists yet.
5. Run `pwsh .\scripts\validate-environment.ps1` for available local checks. Connect hardware only after using the [bring-up plan](../hardware/test-plan.md).

If PowerShell blocks virtualenv activation, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for that terminal only, or invoke `.venv\Scripts\python.exe` directly.

## Configuration and secrets

- Backend: copy `backend/.env.example` to `backend/.env`; keep local credentials blank until the app is implemented. `.env` is ignored.
- Firmware: copy `firmware/include/local_config.example.h` to `local_config.h` and configure a demo SSID/password. `local_config.h` is ignored. Never commit real values.
- Set `APP_TIMEZONE=Asia/Kolkata` for demo reporting; device timestamps must include an explicit offset.
- No Node runtime, Docker, cloud account, or GitHub login is needed for offline local firmware/environment work.

## Future application startup (not runnable yet)

There is no `backend/app/main.py`. Once implemented, use a local server first:

```powershell
cd .\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

For ESP32 access, bind to the laptop's reachable demo-network address (or `0.0.0.0` only when necessary), restrict Windows Firewall to the isolated demo network, and do not port-forward. The current HTTP design is only for synthetic demonstration data.
