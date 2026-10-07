---
type: hardware
area: hardware
status: unverified
tags:
  - hardware
  - pinout
---
# Hardware Pinout Reference

The single authoritative ESP32 assignment table is [docs/final-pin-map.md](../docs/final-pin-map.md). Firmware constants are in `firmware/include/config.h`.

## Current R307S owner-reported assembly

| Harness position/color | Reported connection | Software pin |
|---|---|---|
| 1 red | ESP32 VIN | power |
| 2 black | ESP32 GND | ground |
| 3 yellow | sensor TX to ESP32 RX | GPIO32 / UART2 RX |
| 4 green | ESP32 TX to sensor RX | GPIO33 / UART2 TX |
| 5 blue | disconnected | — |
| 6 white | disconnected | — |

The owner reports that this wiring was assembled and UART diagnostics attempted; no valid sensor bytes were received. This reports the physical setup, not measured voltage or proof that the sensor is dead. Sensor rail, connector-to-board mapping, TX signal level, and jumper state remain **UNVERIFIED — REQUIRES MULTIMETER / exact-board inspection**. Never rely on harness colors alone when reconnecting.

GPIO16/17 references in old integration/wiring notes are superseded by the current 32/33 assembly and firmware configuration. Do not follow the old map.

## ESP32 constraints

Avoid GPIO0/2/5/12/15 strapping pins for attached peripherals, GPIO6–11 flash pins, and GPIO34–39 for outputs. UART0 GPIO1/3 remain reserved for USB serial. GPIO25/26 are used by the DS3231 I2C bus and by the UART loopback test; the UART loopback test requires a jumper between its own TX and RX and must not be run with the DS3231 attached.

See [power and safety](../docs/power-and-safety.md) before wiring or measuring.
