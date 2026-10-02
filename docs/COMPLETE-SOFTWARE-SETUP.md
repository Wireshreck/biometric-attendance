# Complete software setup (Windows)

**Status:** Commands are documented from the current repo configuration. Firmware compilation and backend tests pass; physical device upload and full-system operation still need testing.

## 1. Install the tools

Install Git for Windows, Python 3.11 or newer, Visual Studio Code, and the PlatformIO IDE extension (or PlatformIO Core CLI). Connect the ESP32 with a USB data cable. If Windows does not show a COM port, install the USB-UART driver matching the chip on the ESP32 board (commonly CP210x or CH340; read the USB bridge marking rather than guessing). The project currently builds with PlatformIO's pinned ESP32 platform and Arduino framework.

## 2. Get and open the project

In PowerShell:

```powershell
git clone https://github.com/Wireshreck/biometric-attendance.git
cd biometric-attendance
code .
```

In VS Code, install/enable PlatformIO, allow it to install the project toolchain, and open the PlatformIO terminal. Alternatively install PlatformIO Core and run the commands below from the repository root.

## 3. Configure the backend for local synthetic use

In one terminal:

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Edit `backend/.env` with a long random admin password (at least 16 characters), a non-default admin username, and local settings. Keep `.env` private; it is ignored by Git. Start the API bound to the local network interface only when needed:

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For an isolated offline laptop-only demonstration, bind to `127.0.0.1`; for ESP32-to-laptop access, find the laptop's private LAN IPv4 address and use that address from the device. Do not create a router port-forward or expose the service publicly. Check `http://127.0.0.1:8000/health` in a browser. Run backend tests with `python -m pytest tests -q` from `backend/`.

Provisioning is a one-time command that prints a bearer token once. Run it only after the sensor's capacity is actually known:

```powershell
python -m app.provision_device --name "Demo ESP32" --location "Local lab" --sensor-capacity 100
```

Do not copy the example number unless that is the measured/reported capacity of the exact sensor. Store the printed UUID/token only in the ignored firmware config.

## 4. Configure firmware credentials

In another terminal at repository root:

```powershell
Copy-Item firmware\include\local_config.example.h firmware\include\local_config.h
```

Edit `firmware/include/local_config.h` with private 2.4 GHz Wi-Fi values, the laptop's private IPv4 address, port `8000`, and provisioned device UUID/token. This file is ignored. Never paste credentials into tracked files, screenshots, notes or serial logs. API traffic uses plain HTTP and bearer tokens on the local network; this is demonstration-only with synthetic data on a private network.

## 5. Build and test firmware

List available serial ports in PlatformIO Devices or Windows Device Manager. Replace `COMx` below with the actual port. From repository root:

```powershell
pio run -d firmware -e production
pio run -d firmware -e esp32_core
pio run -d firmware -e i2c_scan
pio run -d firmware -e oled
pio run -d firmware -e rtc
pio run -d firmware -e green_led
pio run -d firmware -e red_led
pio run -d firmware -e buzzer
pio run -d firmware -e uart2_loopback
pio run -d firmware -e r307s
pio run -d firmware -e wifi_diag
pio run -d firmware -e backend_http
pio run -d firmware -e storage
pio run -d firmware -e int_full
```

Build is not physical verification. Upload only after the matching test prerequisites are satisfied:

```powershell
pio run -d firmware -e esp32_core -t upload --upload-port COMx
pio device monitor -d firmware --port COMx --baud 115200
```

For each hardware test, replace its environment (`i2c_scan`, `oled`, `rtc`, `green_led`, `red_led`, `buzzer`, `uart2_loopback`, `r307s`, `wifi_diag`, `backend_http`, `storage`, `int_full`) and upload/run the image. Read [component tests](component-tests.md) for prerequisites, expected output, and what a PASS actually proves.

### First-use filesystem

The production app mounts LittleFS without formatting, protecting queued attendance data. A new blank board may need one initial filesystem image:

```powershell
pio run -d firmware -t uploadfs --upload-port COMx
```

This erases/replaces the on-device filesystem. Do this only before any attendance events are stored or after consciously exporting/reconciling all pending events. Never use it as routine repair.

### Production image

```powershell
pio run -d firmware -e production
pio run -d firmware -e production -t upload --upload-port COMx
pio device monitor -d firmware --port COMx --baud 115200
```

Enter `HELP`; use `STATUS`. `SETTIME YYYY-MM-DD HH:MM:SS` writes explicitly entered India local time (+05:30) into the RTC; compare with a trusted clock. Enrollment requires an already-created pending synthetic student and the command `ENROLL <student-uuid>`. Attendance POST requires sensor functionality, valid RTC, mounted storage, Wi-Fi, device UUID/token, and backend-assigned slot. Current R307S response state blocks physical operation.

## 6. Interpreting results

- `[PASS]` means only the printed check passed in that run. A compile PASS says nothing about external hardware.
- `NOT EXECUTED` means no test was run.
- `UNVERIFIED` means available evidence does not establish that claim.
- `BLOCKED` means a prerequisite (for example a safe rail measurement) is missing.
- Never treat `SENSOR NOT FOUND` as proof a module is dead. The current rail/TX voltage are unmeasured.

See [troubleshooting](troubleshooting.md), [power safety](power-and-safety.md), [production firmware](production-firmware.md), and [science fair setup](SCIENCE-FAIR-SETUP.md).
