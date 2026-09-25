---
type: project-navigation
status: IN PROGRESS
updated: 2026-09-25
---

# Biometric School Attendance System — Project Home

Welcome to the project workspace for the **local-first Biometric School Attendance demonstrator**. Open the repository root as the Obsidian vault so this workspace can navigate the actual source, plans, configuration, and tests.

> [!NOTE]
> **Current Status:** `IN PROGRESS` — database foundation verified; backend/API and device/product implementation remain
> **Exhibition Date:** 09 October 2026  
> **Target Platform:** ESP32-WROOM-32 + AS608 + FastAPI + SQLite  

---

## 📌 Project Navigation Index

- [[AI Development Guide|AI / contributor operating guide]] · [[AI Project Handoff|Current project handoff]] · [[Decision Log|Architecture decision log]] · [[Milestones|Milestone status]]

* 📋 **Specifications & Goals:**
  * [[01 - Requirements|System Requirements (Functional & Non-Functional)]]
  * [[02 - Architecture|System Architecture & Topology]]
  * [[11 - Privacy & Security|Biometric Privacy & Legal Disclaimers]]
  * [Requirements-to-test traceability](../../docs/requirements-traceability.md)

* ⚡ **Hardware & Procurement:**
  * [[03 - Hardware|Component Specifications & Datasheets]]
  * [[04 - Bill of Materials|Bill of Materials & Indian Pricing]]
  * [[16 - Purchase Checklist|Physical Hardware Purchase Checklist]]
  * Wiring schematics & pin mapping details are documented in the main docs.

* 💻 **Software & Engineering Plans:**
  * [[05 - Software Stack|Technology Stack Selection & Rationale]]
  * [[06 - Firmware Plan|ESP32 Firmware Plan]]
  * [[07 - Backend Plan|FastAPI Backend & Service Architecture]]
  * [[08 - Database Plan|SQLite3 Relational Schema & WAL Mode]]
  * [[09 - API Plan|REST API Endpoint Specifications]]
  * [[10 - AI Plan|Optional Read-Only Tool-Calling AI Adapter]]

* 🧪 **Testing, Timeline & Execution:**
  * [[12 - Testing Plan|Hardware & Software Test Matrix]]
  * [[13 - GitHub & Development|Git Milestones & Issue Management]]
  * [[14 - Science Fair|Exhibition Master Plan & Judge Strategy]]
  * [[15 - Timeline|15-Day Science Fair Critical Path Timeline]]
  * [[TODO|Master Project Task & Defect Tracker]]
  * [[17 - Future Ideas|Future Roadmap & Expansion Concepts]]

* 🗺️ **Visual Canvas:**
  * [[Architecture.canvas|Open Interactive Architecture Canvas]]

---

## System Status Dashboard

| Area | Status | Evidence / remaining work |
| --- | --- | --- |
| Repository-root Obsidian workspace and AI handoff | VERIFIED | Guide, handoff, decision log, task tracker and file-backed Canvas |
| Git baseline / GitHub remote / CLI auth | VERIFIED | `main`, baseline `9bb5801`, `origin/main`, local `gh auth status` |
| Python environment and SQLite smoke check | VERIFIED | `backend/test_env.py` passed in `backend/.venv` |
| SQLite schema v1 migration | VERIFIED | Six temporary-database migration/constraint tests passed |
| Firmware toolchain sketch | VERIFIED | `pio run -d firmware` passed; compile only, no board flash or hardware test |
| FastAPI, attendance firmware, dashboard | PLANNED | Product application layers not implemented |
| Procurement / physical hardware | BLOCKED / NEEDS HARDWARE | Purchase status and exact module revisions are unknown |
| Integrated science-fair demo | PLANNED | Requires application work and hardware evidence |

> Dates remain targets. Hardware order/arrival is unconfirmed. Product features are planned unless their implementation and evidence are explicitly recorded. Use [[TODO|the authoritative task tracker]], [[Milestones]], and the [canonical project plan](../../docs/project-plan.md).
