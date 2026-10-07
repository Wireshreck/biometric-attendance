---
type: hardware
area: hardware
status: unverified
tags:
  - hardware
  - breadboard
  - power
  - wiring
---

# 02 - Hardware Lab

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[01 - Project HQ]] [[03 - Firmware Lab]] [[05 - Testing Lab]] [[06 - Research Archive]] · **CANVAS** [[02 - Hardware Lab/02 - Hardware Lab.canvas|02 - Hardware Lab.canvas]] · **ASSEMBLY** [[02 - Hardware Lab/02 - Hardware Assembly.canvas|02 - Hardware Assembly.canvas]]

The bench. One ESP32, one fingerprint sensor, one display, one clock, two lights, one buzzer, and a lot of unmeasured voltages.

> [!DANGER] The bench is not electrically characterised.
> Every rail in this room is **UNVERIFIED — REQUIRES MULTIMETER**. ESP32 GPIO is 3.3 V and is **not** 5 V tolerant. Nothing here may be energised on the assumption that a datasheet describes *this* board.

---

## What is on the bench

| Part | Interface | ESP32 pins | State |
|---|---|---|---|
| **ESP32-WROOM-32 DevKit** | — | — | Upload + USB serial work (owner/history report). Port is now **COM4**, was COM3 |
| **R307S fingerprint sensor** | UART2 · 57600 8-N-1 | RX **32**, TX **33** | Assembled per owner report · **0 valid bytes** · rail/logic **UNVERIFIED** |
| **SSD1306 OLED** — REMOVED | not connected | — | not in this project |
| **DS3231 RTC** | I2C `0x68` | SDA **21**, SCL **22** | Mapped · **NOT EXECUTED** |
| **Green LED** | GPIO out via resistor | **18** | Mapped · **NOT EXECUTED** |
| **Red LED** | GPIO out via resistor | **19** | Mapped · **NOT EXECUTED** |
| **Active buzzer** | GPIO in / driver | **23** | Mapped · **NOT EXECUTED** · module identity unknown |
| **Breadboard + jumpers** | — | — | Layout is a *recommendation*, not a record — no photo exists |
| **USB 5 V** | power in | — | Rails never measured |
| **CR2032** | — | — | **RTC backup only. Never the sensor supply.** |

Canonical pin table: [[docs/final-pin-map.md]] · `firmware/include/config.h`

---

## The three buses

```text
ESP32 ──UART2──▶  R307S        GPIO32 RX / GPIO33 TX @ 57600 8-N-1
ESP32 ──I2C────┬─▶ DS3231 only   GPIO21 SDA / GPIO22 SCL @ 100 kHz (OLED removed)
              └─▶ RTC  0x68   shared bus, shared 3.3 V pull-up domain
ESP32 ──GPIO───┬─▶ Green LED   GPIO18 through a series resistor
               ├─▶ Red LED     GPIO19 through a series resistor
               └─▶ Buzzer      GPIO23, or a transistor driver
```

The RTC is the only I2C device on this bus. An I2C ACK proves a device is listening — it does not prove pull-up voltage. OLED was removed from this project.

---

## The R307S, as actually wired

Observed six-wire harness order: **red, black, yellow, green, blue, white**.

| Position | Colour | Reported connection | State |
|---|---|---|---|
| 1 | red | ESP32 `VIN` | Assembled per owner report · **voltage not measured** |
| 2 | black | ESP32 `GND` | Assembled per owner report |
| 3 | yellow | ESP32 **GPIO32** (sensor TX → MCU RX) | Connected · **no valid response** |
| 4 | green | ESP32 **GPIO33** (MCU TX → sensor RX) | Connected · **no valid response** |
| 5 | blue | open, insulated | Leave disconnected |
| 6 | white | open, insulated | Leave disconnected |

Wire colour is an *observation*, not proof of the PCB pad function. Do not infer pinout from colour.

Diagnostic evidence: [[docs/r307s-test-matrix.md]] · [[docs/r307s-hardware-research.md]] · [[docs/r307s-next-session.md]]

---

## What is verified and what is not

**VERIFIED (owner/history report)**
- ESP32 compiles, flashes, and talks over USB serial.
- The diagnostic runs to completion and prints a result.
- GPIO32's line reads as actively *driven high* under both internal pull-down and pull-up. This is a **software ADC estimate, not a calibrated voltage.**

**UNVERIFIED — REQUIRES MULTIMETER**
- R307S rail voltage, current draw, TX high level.
- Exact PCB pin mapping, connector orientation, 3.3 V solder-jumper state.
- Whether the reported harness wires contact the pads the owner believes they do.
- RTC supply compatibility and I2C pull-up rail (OLED removed).
- buzzer module voltage and current (LEDs/OLED removed).
- Every common-ground path.

**NOT EXECUTED**
- Every one of `i2c_scan`, `oled`, `rtc`, `green_led`, `red_led`, `buzzer`, `uart1_loopback`, `uart2_loopback`.

**BLOCKED**
- Anything requiring a measurement instrument. There is no multimeter available today.

---

## Safety rules

1. ESP32 GPIO is **3.3 V, not 5 V tolerant.** Measure a sensor TX high level before it ever touches a GPIO.
2. Do not fit a primary CR2032 to a charging RTC breakout.
3. Do not short jumpers, bridge unknown solder links, or probe unknown USB pads.
4. Unplug USB before rewiring. Never combine USB power with an injected rail.
5. Never drive an unknown or high-current load — including a buzzer — straight from a GPIO.
6. Read [[docs/power-and-safety.md]] before connecting anything. It is the gate, not advice.

---

## Documents

| Purpose | Canonical file |
|---|---|
| Pin map, per component, with status column | [[docs/final-pin-map.md]] |
| Electrical safety and measurement gate | [[docs/power-and-safety.md]] |
| Physical assembly, step by step | [[docs/COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md]] |
| Breadboard placement method | [[docs/complete-breadboard-layout.md]] |
| Bench evidence log | [[hardware/test-plan.md]] |
| Component selection and limits | [[docs/hardware.md]] |
| Bill of materials and pricing | [[docs/bill-of-materials.md]] |
| Purchase checklist | [[docs/purchase-checklist.md]] |
| Sensor integration sequence | [[docs/r307s-integration-plan.md]] |
| Hardware diagram | [[diagrams/hardware.mmd]] |

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[03 - Firmware Lab]] [[05 - Testing Lab]] [[06 - Research Archive]] · **CANVAS** [[02 - Hardware Lab/02 - Hardware Lab.canvas|02 - Hardware Lab.canvas]] · **ASSEMBLY** [[02 - Hardware Lab/02 - Hardware Assembly.canvas|02 - Hardware Assembly.canvas]]
