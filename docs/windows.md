# Windows Apps (`desktop/`, `tools/`)

All Python 3 + tkinter (standard library UI) + `bleak` (BLE) + `pyserial`
(used by the installer for port detection). All import the single shared
protocol `shared/ble_protocol.py`. Build with PyInstaller into real `.exe`
files; see `scripts/build_windows_apps.ps1`.

## Desktop manager (`desktop/app.py`)

BLE discovery, connect/disconnect, dashboard, fingerprint management
(status/count/enroll/search/delete/delete-all with confirmation), RTC
display/set, attendance table/clear, FULL_DIAGNOSTIC table, BUZZER_TEST,
PING, help. Same JSON protocol as every other client.

```powershell
pip install bleak pyserial
python desktop/app.py
```

Build: `pyinstaller --onefile --windowed --name BiometricDesktop desktop/app.py`
→ `dist/BiometricDesktop.exe`.

## test.exe (`tools/test_app/test_app.py`)

Standalone diagnostics. Buttons: CONNECT DEVICE, RUN FULL SYSTEM TEST,
R307S TEST, RTC TEST, BUZZER TEST, BLE TEST, STORAGE TEST, ATTENDANCE
TEST, EXPORT LOG. Results are PASS/FAIL/WARN/SKIPPED only: disconnected
hardware is never PASS, unsupported is SKIPPED, failures carry reasons,
and EXPORT LOG writes a timestamped diagnostic file.

Build: `pyinstaller --onefile --windowed --name test tools/test_app/test_app.py`
→ `dist/test.exe`.

## install.exe (`tools/installer/install_app.py`)

Setup wizard: prerequisites → ESP32 auto-detect (CP210x/CH340 hints) with
manual port picker (never hardcodes COM4) → firmware upload via PlatformIO
→ device configure → BLE verify → hardware diagnostics pointer → installs
the Windows app + test.exe → shortcuts/launchers → final verification.

Build: `pyinstaller --onefile --windowed --name install tools/installer/install_app.py`
→ `dist/install.exe`.
