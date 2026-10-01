# Hardware Bring-Up and Verification Plan

**Current Status:** Phase 0 PASSED (ESP32 serial test confirmed on COM3 at 115200 baud).  
**Target Sensor:** R307S Optical Fingerprint Sensor (Acquired; NOT YET CONNECTED OR POWERED).  
**Reference Document:** [`docs/r307s-integration-plan.md`](../docs/r307s-integration-plan.md)  

---

## 1. Hardware Verification Gates

| ID | Gate | Method | Status | Pass Criterion / Recorded Evidence |
| :--- | :--- | :--- | :---: | :--- |
| **HW-00** | **ESP32 Serial & Toolchain Test (Phase 0)** | PlatformIO compile, upload to COM3, monitor at 115200 baud | **VERIFIED (PASSED)** | Boot banner received, chip model identified, heap reported cleanly on COM3. |
| **HW-01** | **R307S Physical & Electrical Identification (Phase 1)** | Visual inspection of connector, silkscreen labels, multimeter ground trace | **IN PROGRESS (BLOCKED ON BENCH)** | Confirm pin 1–6 signal definitions; confirm supply rating (5V vs 3.3V); record observed harness order (Red, Black, Yellow, Green, Blue, White). |
| **HW-02** | **Power Rails & No-Load Sanity (Phase 2 & 3)** | Multimeter measurement of ESP32 5V and 3V3 rails; test sensor alone | **PLANNED** | 5V rail within 4.75V–5.25V; 3V3 rail within 3.25V–3.35V; R307S TX pin voltage $\le 3.3\text{V}$; no heating. |
| **HW-03** | **RTC Battery & Circuit Safety** | Inspect DS3231 breakout charging circuit before inserting coin cell | **PLANNED** | Verify no trickle charging onto primary non-rechargeable CR2032 cell. |
| **HW-04** | **I2C Bus Scan (OLED + RTC)** | Flash I2C diagnostic scanner at 100 kHz on GPIO 21/22 | **PLANNED** | OLED responds at `0x3C` (or `0x3D`); RTC responds at `0x68`. Bus voltage never exceeds 3.3V. |
| **HW-05** | **LED & Buzzer Indicator Check** | Toggle GPIO 18, 19, 23 with current-limiting resistors / transistor | **PLANNED** | Green/Red LEDs illuminate safely ($\le 12\text{mA}$); active buzzer emits clean acoustic tone without reset. |
| **HW-06** | **R307S UART Communication (Phase 4 & 5)** | Configure UART2 on GPIO 16/17 (57600 baud default); send password verify packet | **PLANNED** | Sensor returns acknowledge packet with confirmation code `0x00`. No framing errors. |
| **HW-07** | **R307S Status & Capacity Query (Phase 6)** | Send `readSysPara` command packet | **PLANNED** | Sensor reports system parameters (baud, packet size, security level, capacity = 1000). |
| **HW-08** | **R307S Biometric Enrollment & Matching (Phase 7 & 8)** | 2-pass finger impression capture, model generation, slot 1 store; 1:N search | **PLANNED** | Enrolled finger matches slot 1 with high confidence; un-enrolled finger returns not found. |
| **HW-09** | **Combined Load & RTC Persistence (Phase 9)** | Run full terminal with Wi-Fi burst, OLED active, and optical illumination | **PLANNED** | No brownouts, resets, or thermal throttling. RTC retains time through 10-minute USB power disconnect. |

---

## 2. R307S Bring-Up Sequence Rules

1. **Gate HW-01 is a HARD STOP:** Do not apply power to the R307S until its physical pin labels, ground pin, and supply voltage requirements are confirmed from the physical unit.
2. **Never rely on wire colors:** The observed harness order (1: Red, 2: Black, 3: Yellow, 4: Green, 5: Blue, 6: White) must be validated against the module PCB.
3. **Check TX voltage before connecting to ESP32:** Power the sensor from 5V/3.3V and measure the open-circuit voltage on the TX line. It must not exceed 3.3V.
4. **Initial UART test must be isolated:** Connect only GND, VCC, TX, and RX. Leave touch/wakeup lines disconnected.
5. **Start at 57600 baud:** If no response, test 9600, 19200, 38400, and 115200 baud before altering hardware connections.
