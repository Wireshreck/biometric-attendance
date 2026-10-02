# R307S Debugging Handoff

**Updated:** 2026-10-02
**Purpose:** Record the current diagnostic result and the safe next step without relying on the earlier conversation.

## Current reported setup

- ESP32-WROOM-class board; prior upload and USB serial worked (COM number may change after replug; enumerate ports each session).
- R307S six-wire harness reported in this order: red, black, yellow, green, blue, white.
- Current reported wiring: red to ESP32 VIN; black to GND; yellow (sensor TX) to GPIO32/RX; green (sensor RX) to GPIO33/TX; blue and white disconnected.
- Firmware uses UART2 at provisional 57600 8-N-1 on RX32/TX33.
- Owner reports the diagnostic runs but receives 0 bytes at tested baud rates/routings. No multimeter is currently available.

## What the diagnostic says

`firmware/src/r307s_uart_diag.cpp` performs a finite-timeout line probe and receive monitor, probes the family baud ladder with VerifyPassword, and only runs ReadSysPara/TemplateCount after a valid response. It does not enroll, search, delete templates, or alter parameters. Preserve it until a verified driver replaces its role.

The previous captured run reported zero received bytes at all 12 documented family rates and the two software-swapped routing probes. Its software ADC/internal-pull test classified the GPIO32 wire as held high. This is **not a calibrated voltage measurement**, does not identify the source, and does not prove sensor power or health. The diagnostic summary was “completely silent”; it does not prove the module is dead.

## Unknowns

- Actual voltage at the sensor supply pins and current draw.
- Sensor TX high voltage; ESP32 GPIO is not 5 V tolerant.
- Whether the reported harness wires contact the expected board pads and whether the sensor jumper/solder bridge is configured for that rail.
- Integrity of the ESP32-TX-to-sensor-RX conductor.
- Whether the module boots, its address/password, and exact board/revision.

Current supply and logic levels must remain **UNVERIFIED — REQUIRES MULTIMETER**. The R307 family datasheet and R307S quick-start inform likely behavior but do not verify this exact board. Do not blindly swap wires, bridge jumpers, connect USB pads, or perform write/enrollment commands.

## Next session actions

1. Photograph/read the exact sensor markings, connector orientation and jumper state. Verify the manufacturer/board revision and pin mapping; do not rely on colors alone.
2. When a multimeter is available, record rail, ground continuity and sensor TX idle voltage before any new connection. Stop if voltage safety is unclear.
3. Re-run `pio run -d firmware -e r307s`, upload/monitor using today's enumerated serial port, and save the complete output. Then disconnect the sensor from GPIO32/33 and run `uart1_loopback` or `uart2_loopback` using a GPIO25-TX-to-GPIO26-RX jumper.
4. If physical electrical checks pass but silence persists, isolate the sensor with the documented USB/USB-UART path only after pad labels are positively identified and safe hardware is available.

Commands from repository root:

```powershell
pio device list
pio run -d firmware -e r307s
pio run -d firmware -e r307s -t upload --upload-port COM3
pio device monitor -d firmware --port COM3 --baud 115200
pio run -d firmware -e uart2_loopback -t upload --upload-port COM3
```

Replace COM3 with the current port. Never run loopback while anything else is attached to its test pins.

See [R307S hardware research](r307s-hardware-research.md), [power and safety](power-and-safety.md), [pin map](esp32-pin-map.md), and [component tests](component-tests.md).
