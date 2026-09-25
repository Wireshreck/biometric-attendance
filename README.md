# Biometric School Attendance System

> **Open-source, local-first biometric attendance demonstrator for schools.**
> Planned core: ESP32 + AS608 fingerprint sensor + FastAPI + SQLite.
> Science Fair Exhibition: **9 October 2026**

---

## Project Status: `IN PROGRESS`

| Milestone | Status |
| :--- | :---: |
| Python/backend environment smoke check | VERIFIED |
| Git history | VERIFIED (baseline `9bb5801` preserved; milestone `310559e` committed locally, one commit ahead of `origin/main`; not pushed) |
| GitHub CLI authentication | VERIFIED locally (`gh auth status`; CI result not checked) |
| Hardware selection and BOM | IMPLEMENTED (planning docs; procurement unconfirmed) |
| Purchase/delivery confirmation | BLOCKED (owner status unknown) |
| Firmware toolchain validation sketch | VERIFIED (compile only; flashing and hardware behavior NEEDS HARDWARE) |
| Backend application/API | PLANNED |
| Obsidian project workspace | VERIFIED (repo root is vault; guide/handoff/file-backed Canvas link to source files) |
| Architecture documentation | VERIFIED (implementation remains planned) |
| Hardware bench tests | NEEDS HARDWARE |
| Attendance firmware | PLANNED; NEEDS HARDWARE for sensor validation |
| Database schema v1 migration | VERIFIED (6 temporary-database migration/constraint tests passed) |
| Dashboard | PLANNED |
| End-to-end integration | PLANNED; NEEDS HARDWARE |
| Science-fair demo | PLANNED |

---

## 🗓️ Science Fair Countdown

Dates below are planning targets from the project timeline, not confirmed purchases, delivery commitments, or completed milestones.

| Date | Deadline |
| :--- | :--- |
| **Sep 25** | ⚠️ **Hardware order placed by 12:00 noon** |
| **Sep 28** | Hardware arrives — bench bring-up |
| **Oct 01** | Standalone biometric prototype |
| **Oct 04** | First working end-to-end demo |
| **Oct 06** | Testing & code freeze |
| **Oct 08** | Final backup & presentation rehearsal |
| **Oct 09** | 🏆 **Science Fair** |

---

## 🔩 System Architecture

```
┌─────────────────────────────────┐
│     Edge Terminal (ESP32)       │
│  AS608 ─ UART ─ ESP32 ─ OLED   │
│              │                  │
│           DS3231 RTC            │
│    Green/Red LED  Buzzer        │
│    LittleFS offline buffer      │
└──────────────┬──────────────────┘
               │ Wi-Fi (2.4 GHz)
               ▼
┌─────────────────────────────────┐
│  Local Laptop (Python server)   │
│  FastAPI ──► SQLite3 (WAL)      │
│  Vanilla JS Web Dashboard       │
└──────────────┬──────────────────┘
               │ Optional
               ▼
┌─────────────────────────────────┐
│  Local LLM Tool-Calling Layer   │
│  (Read-only, offline, Ollama)   │
└─────────────────────────────────┘
```

---

## 🔑 Key Design Principles

- **Local-first design:** Core service is planned to run locally without cloud services; not implemented yet.
- **Biometric minimization:** The planned boundary keeps image/template operations on the sensor and sends a match slot only; exact sensor behavior is unverified.
- **Offline resilience:** DS3231 timekeeping and a LittleFS event queue are planned; neither is implemented or validated yet.
- **Open source:** MIT License — free for any school to use and modify.
- **Affordable target:** Current planning envelope is ~₹2,399 before any unpriced conditional RTC cell; verify the actual cart.

---

## 📁 Repository Structure

```
biometric-attendance/
├── firmware/            ESP32 source code (PlatformIO / Arduino)
├── backend/             FastAPI + SQLite backend (Python 3.13)
├── frontend/            Vanilla JS/HTML5 web dashboard
├── hardware/            Pinout, bench test plans
├── docs/                Project documentation
├── diagrams/            Mermaid diagrams
├── scripts/             Automation and backup scripts
├── presentation/        Demo script, judge Q&A, outline
├── obsidian/            Project navigation notes and Canvas (open repository root as vault)
└── .github/             Issue templates, CI workflows
```

---

## 🚀 Planned Quick Start (After Implementation and Hardware Bring-Up)

The commands below describe the intended end-to-end workflow; they are **not runnable yet**. The backend currently has no `main.py` application and the firmware sketch only validates the toolchain. Follow the subsystem READMEs for current setup checks.

```powershell
# 1. Flash firmware to ESP32
cd firmware
pio run -t upload
pio device monitor -b 115200

# 2. Start backend server (future; app/main.py is not implemented yet)
cd ..\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000

# 3. Open dashboard at http://localhost:8000
```

---

## 📖 Documentation Index

Open the repository root as the Obsidian vault. Start with the [project overview](obsidian/Attendance%20System/00%20-%20Project%20Overview.md), [AI development guide](obsidian/Attendance%20System/AI%20Development%20Guide.md), and [AI handoff](obsidian/Attendance%20System/AI%20Project%20Handoff.md). The numbered vault notes are navigation/status pages; subsystem design details remain authoritative in the linked files below.

| Document | Description |
| :--- | :--- |
| [`docs/project-plan.md`](docs/project-plan.md) | Overall project scope and WBS |
| [`docs/requirements.md`](docs/requirements.md) | Functional & non-functional requirements |
| [`docs/requirements-traceability.md`](docs/requirements-traceability.md) | Requirement priorities, status, component and planned verification mapping |
| [`docs/architecture.md`](docs/architecture.md) | System architecture & topology |
| [`docs/hardware.md`](docs/hardware.md) | Component datasheets & specs |
| [`docs/bill-of-materials.md`](docs/bill-of-materials.md) | Full BOM with Indian pricing |
| [`docs/wiring.md`](docs/wiring.md) | GPIO pin map & electrical connections |
| [`docs/software-stack.md`](docs/software-stack.md) | Technology selection rationale |
| [`docs/database-plan.md`](docs/database-plan.md) | SQLite schema design |
| [`docs/api-plan.md`](docs/api-plan.md) | REST API endpoint specification |
| [`docs/privacy-security.md`](docs/privacy-security.md) | Biometric privacy architecture |
| [`docs/science-fair-timeline.md`](docs/science-fair-timeline.md) | 15-day development schedule |
| [`docs/purchase-checklist.md`](docs/purchase-checklist.md) | Hardware purchase checklist |
| [`docs/github-setup.md`](docs/github-setup.md) | GitHub authentication guide |

---

## ⚡ Hardware Bill of Materials Summary

| Component | Est. Price |
| :--- | :---: |
| ESP32-WROOM-32 DevKit V1 | ₹349 |
| AS608 Optical Fingerprint Sensor | ₹799 |
| SSD1306 0.96" I2C OLED | ₹163 (listing, ex GST) |
| DS3231 High Precision RTC | ₹189 |
| Active Buzzer, LEDs, Resistors | ₹105 |
| Breadboard + Jumper Wires + USB Cable | ₹344 |
| **Planning estimate incl. tax/shipping reserve** | **~₹2,399 (verify current cart; not a quote)** |

---

## 📄 License

MIT License — See [`LICENSE`](LICENSE)

## 🤝 Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md)

## 🔒 Security

See [`SECURITY.md`](SECURITY.md) and [`docs/privacy-security.md`](docs/privacy-security.md)
