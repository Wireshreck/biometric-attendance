# Hardware Subsystem Documentation

This directory contains wiring diagrams, pinout mappings, component datasheets, and physical bring-up testing plans for the Biometric School Attendance System terminal.

---

## Directory Contents

* **`pinout.md`**: Provisional ESP32-WROOM-32 DevKit pin assignments and electrical constraints; not bench-verified.
* **`test-plan.md`**: Step-by-step physical bench testing procedure; the Sep 28, 2026 arrival date is a planning target, not confirmed delivery.

---

## Hardware Architecture Quick Reference

* **Main Controller:** ESP32-WROOM-32 DevKit V1 (3.3V Logic)
* **Optical Fingerprint Sensor:** AS608 via configurable ESP32 UART (GPIO 16/17 provisional; verify exact module and board)
* **Real-Time Clock:** DS3231 via Hardware I2C (GPIO 21/22, Address `0x68`)
* **Display:** SSD1306 0.96" 128×64 OLED via Hardware I2C (GPIO 21/22, Address `0x3C`)
* **Audio Indicator:** 5V Active Buzzer with onboard transistor driver (GPIO 23)
* **Visual Status:** 5mm Diffused Green LED (GPIO 18) and Red LED (GPIO 19) through 330Ω resistors
* **Power Source:** 5V USB (via Micro-USB port)
