# Installed Development Tools Record

**Date:** 2026-09-24  
**Project:** Biometric School Attendance System (`biometric-attendance`)  

This document logs all development tools installed or configured during the bootstrap process, adhering strictly to the principle of minimal, necessary tool installation.

---

## 1. PlatformIO Core CLI

* **Tool Name:** PlatformIO Core (`pio`)
* **Version:** 6.2.0
* **Installation Method:** Python pip (`python -m pip install platformio`)
* **Location:** Python 3.13 site-packages and Scripts (`C:\Users\user\AppData\Local\Programs\Python\Python313\Scripts\pio.exe`)
* **Reason:** Essential build system and compiler toolchain manager for the ESP32 microcontroller (`espressif32` platform, Arduino framework). It enables headless compilation, automated package and library management, and reproducible builds without the GUI overhead of Arduino IDE.
* **Verification Command:**
  ```powershell
  pio --version
  # Output: PlatformIO Core, version 6.2.0
  ```

---

## 2. GitHub CLI

* **Tool Name:** GitHub CLI (`gh`)
* **Version:** 2.101.0
* **Installation Method:** Windows Package Manager (`winget install --id GitHub.cli --exact --silent --accept-package-agreements --accept-source-agreements`)
* **Location:** `C:\Program Files\GitHub CLI\gh.exe`
* **Reason:** Official CLI tool for interacting with GitHub repositories, issues, milestones, and pull requests directly from automated scripts and the command line.
* **Verification Command:**
  ```powershell
  gh --version
  # Output: gh version 2.101.0 (2026-09-15)
  ```
* **Authentication Status:** Pending user login (`gh auth login`). See `docs/github-setup.md`.

---

## 3. Pre-existing System Tools Retained

| Tool | Pre-installed Version | Path | Status |
| :--- | :--- | :--- | :--- |
| **Git** | 2.55.0.windows.3 | `C:\Program Files\Git\cmd\git.exe` | Verified, in PATH |
| **Python** | 3.13.15 | `C:\Users\user\AppData\Local\Programs\Python\Python313\python.exe` | Verified, in PATH |
| **Node.js** | 24.19.0 | `C:\Program Files\nodejs\node.exe` | Verified, in PATH |
| **npm** | 12.0.2 | `C:\Program Files\nodejs\npm.ps1` | Verified, in PATH |
| **VS Code** | Modern Release | `C:\Users\user\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd` | Verified, in PATH |
| **Obsidian** | Modern Release | `C:\Users\user\AppData\Local\Programs\Obsidian\Obsidian.exe` | Verified |

---

## 4. Tools Intentionally Not Installed

* **Arduino IDE / Arduino CLI:** PlatformIO covers all compiling and flashing needs with higher reproducibility.
* **Docker Desktop:** Unnecessary container layer for a local-first SQLite/FastAPI setup on a single laptop.
* **Cloud AI SDKs:** The core architecture requires local-first, zero-cloud operation. Cloud AI dependencies are avoided.
* **Large JS Frameworks (Angular/Next.js):** The web dashboard is engineered using vanilla web standards to guarantee high reliability, zero npm vulnerability creep, and zero build step failures during live science fair demonstrations.
