# Development Environment Audit

**Audit Date:** 2026-09-24  
**Project:** Biometric School Attendance System (`biometric-attendance`)  
**Auditor:** Automated Project Initialization Agent  

> Historical machine snapshot. Current Git/GitHub state is in [GitHub setup](github-setup.md); the repository root is now the Obsidian vault, while `obsidian/Attendance System/` is its project workspace. The pinned `esp32dev` validation sketch compiled with `pio run -d firmware` on 2026-09-25; this is compile evidence only, not a flash or hardware test.

---

## 1. System Specifications

| Parameter | Detected Value | Status / Notes |
| :--- | :--- | :--- |
| **Operating System** | Windows 10 Pro (Build 2009 / 19045+) | Verified 64-bit |
| **Architecture** | AMD64 / x86_64 | 64-bit OS and CPU |
| **CPU** | 11th Gen Intel(R) Core(TM) i5-11400F @ 2.60GHz (6 Cores, 12 Threads) | High performance for compiling & hosting |
| **RAM** | 16.0 GB (17,038,991,360 bytes physical) | Sufficient for firmware compilation and local servers |
| **Disk Space (C:)** | 193.66 GB Free (out of ~476 GB) | Ample storage for PlatformIO packages, Python venv, caches |

---

## 2. Tool & Runtime Categorization

### INSTALLED (Ready for Use)

| Tool / Runtime | Version | Detected Executable Path | Purpose |
| :--- | :--- | :--- | :--- |
| **Git** | 2.55.0.windows.3 | `C:\Program Files\Git\cmd\git.exe` | Version control & repository tracking |
| **Python** | 3.13.15 | `C:\Users\user\AppData\Local\Programs\Python\Python313\python.exe` | Backend execution, scripting, PlatformIO host |
| **pip** | 26.2.1 | `C:\Users\user\AppData\Local\Programs\Python\Python313\Scripts\pip.exe` | Python package management |
| **Node.js** | 24.19.0 | `C:\Program Files\nodejs\node.exe` | Frontend runtime (if optional static tooling needed) |
| **npm** | 12.0.2 | `C:\Program Files\nodejs\npm.ps1` | Node package manager |
| **VS Code** | Detected | `C:\Users\user\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd` | Primary developer IDE |
| **Obsidian** | Detected | `C:\Users\user\AppData\Local\Programs\Obsidian\Obsidian.exe` | Knowledge base & Canvas visualizer |
| **Windows Package Manager** | 1.9+ | `C:\Users\user\AppData\Local\Microsoft\WindowsApps\winget.exe` | Windows package installation |
| **PlatformIO Core** | 6.2.0 | Installed via pip (`python -m pip install platformio`) | ESP32 toolchain, board manager, compiler |
| **GitHub CLI (gh)** | 2.101.0 | Installed via winget (`GitHub.cli`) | GitHub issue & milestone management |

---

### MISSING AT SNAPSHOT DATE (2026-09-24; re-check current state)

| Component | Status | Required Action / Remedy |
| :--- | :--- | :--- |
| **GitHub Authentication** | `gh auth status` returned unauthenticated at snapshot time | Rechecked 2026-09-25; authenticated as `Wireshreck`. Current instructions in `docs/github-setup.md`. |
| **Git User Identity** | Global `user.name` and `user.email` not set at snapshot time | Rechecked 2026-09-25; configured identity and baseline commit are recorded in `docs/github-setup.md`. |
| **Physical ESP32 Board** | No USB-UART bridge detected on COM ports | Hardware pending procurement (Science Fair arrives ~Sept 28, 2026). Upload marked as **PENDING HARDWARE**. |

---

### OPTIONAL (Not Needed for MVP)

| Component | Status | Evaluation |
| :--- | :--- | :--- |
| **pnpm** | Not found | Optional; `npm` 12 is already installed if package builds are needed. |
| **Docker** | Not found | Optional; FastAPI and SQLite run natively in Python 3.13 without container overhead. |
| **Cloud AI SDKs** | Not installed | System strictly targets local-first operation without cloud dependencies. |

---

### NOT NEEDED (Omitted to Keep Environment Clean)

| Tool | Status | Reason for Omission |
| :--- | :--- | :--- |
| **Arduino IDE / Arduino CLI** | Omitted | Redundant. PlatformIO Core provides unified CLI compilation, automated library resolution, and CI support without Arduino IDE dependencies. |
| **Java / OpenJDK** | Not found | No Java dependencies in ESP32 firmware or Python backend stack. |
| **Heavy Frontend Frameworks** | Omitted | The attendance web dashboard is designed with modern vanilla HTML5, CSS3, and JavaScript, eliminating Vite/Webpack/React build bloat. |

---

## 3. Hardware Interfaces & Serial Ports

```powershell
Port Name: COM1
Device ID: ACPI\PNP0501\0
Description: Communications Port (Standard motherboard serial port)
```

* **ESP32 USB-to-UART Bridge:** Not connected (expected during bootstrap phase). Supported ICs: Silicon Labs CP2102/CP2104, WCH CH340G/C, FTDI FT232R.
* **Hardware Bring-up Status:** Pending hardware delivery scheduled for September 28, 2026.
* **Firmware Validation:** Performed via PlatformIO CLI dry-run compilation (`pio run` targeting `esp32dev`).

---

## 4. Obsidian Environment

* **Obsidian Executable:** `C:\Users\user\AppData\Local\Programs\Obsidian\Obsidian.exe`
* **Existing Vaults Registry:** Located in `C:\Users\user\AppData\Roaming\obsidian\obsidian.json`
* **Project Workspace:** Notes were originally created under `biometric-attendance/obsidian/Attendance System/`; current convention is to open the repository root as the vault, keeping the rest of the user's vaults separate.
