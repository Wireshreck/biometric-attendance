# Hardware Subsystem Documentation

This directory contains wiring diagrams, pinout mappings, component datasheets, and physical bring-up testing plans for the Biometric School Attendance System terminal.

---

## Directory Contents

* **`pinout.md`**: Provisional ESP32-WROOM-32 DevKit pin assignments and electrical constraints; includes observed R307S 6-wire harness order.
* **`test-plan.md`**: Step-by-step physical bench testing procedure, organized into 10 structured phase gates for R307S integration.

---

## Hardware Architecture Quick Reference

* **Main Controller:** ESP32-WROOM-32 DevKit V1 (3.3V Logic) — **Status: PASSED bench upload test on COM3 (115200 baud)**
* **Fingerprint Sensor:** R307S Optical Fingerprint Sensor Module (physically acquired; 6-wire harness observed: Red, Black, Yellow, Green, Blue, White)
  - **Status: NOT YET CONNECTED OR POWERED**
  - **Electrical & Pinout: UNVERIFIED — HARDWARE VERIFICATION REQUIRED**
  - Connection: Dedicated ESP32 Hardware UART (GPIO 16/17 provisional; verify exact module and board)
* **Real-Time Clock:** DS3231 via Hardware I2C (GPIO 21/22, Address `0x68`)
* **Display:** SSD1306 0.96" 128×64 OLED via Hardware I2C (GPIO 21/22, Address `0x3C`)
* **Audio Indicator:** 5V Active Buzzer with onboard transistor driver (GPIO 23)
* **Visual Status:** 5mm Diffused Green LED (GPIO 18) and Red LED (GPIO 19) through 330Ω resistors
* **Power Source:** 5V USB (via Micro-USB port)

---

## Critical Safety Notice

The ESP32 microcontroller is strictly a **3.3V logic device**. Its GPIO pins are **NOT 5V tolerant**.
The R307S optical fingerprint module's supply voltage (5V vs 3.3V) and UART TX logic level (3.3V vs 5V) must be confirmed via physical inspection or multimeter measurement before making any electrical connection to the ESP32.
Refer to [`docs/r307s-integration-plan.md`](../docs/r307s-integration-plan.md) for the authoritative integration sequence.
