# Windows Apps (`desktop/`, `tools/`)

All Python 3 + tkinter + `bleak` (BLE) + `pyserial` (installer port
detection). Desktop also uses stdlib `urllib` for the backend REST API.
All import the single shared protocol `shared/ble_protocol.py`.
Build with PyInstaller; see `scripts/build_windows_apps.ps1`.

## Desktop manager v1.1.0 (`desktop/app.py`)

Tabs: Dashboard (overview + recent), Attendance (search/filters/CSV
export), Students (search/add/deactivate), Fingerprints (BLE
count/enroll/search/delete), Device (scan/connect/status/RTC),
Diagnostics (FULL_DIAGNOSTIC table, buzzer, ping), AI Assistant (chat),
Settings (API host + admin credentials in memory only).

BLE reads use the write → busy-poll → result pattern from
`docs/protocol.md`. Build: `pyinstaller --onefile --windowed --name
BiometricDesktop --paths shared desktop/app.py`.

## test.exe (`tools/test_app/test_app.py`)

Standalone diagnostics. Buttons: CONNECT DEVICE, RUN FULL SYSTEM TEST,
R307S TEST, RTC TEST, BUZZER TEST, BLE TEST, STORAGE TEST, ATTENDANCE
TEST, EXPORT LOG. PASS/FAIL/WARN/SKIPPED only; disconnected hardware is
never PASS. Same busy-poll reads. Build: `pyinstaller --onefile
--windowed --name test --paths shared tools/test_app/test_app.py`.

## install.exe (`tools/installer/install_app.py`)

Setup wizard: prerequisites → ESP32 auto-detect (CP210x/CH340 hints) with
manual picker (never hardcodes COM4) → firmware upload → configure →
BLE verify → diagnostics pointer → installs app + test.exe → launchers →
final verification. Build: `pyinstaller --onefile --windowed --name
install --paths shared tools/installer/install_app.py`.
