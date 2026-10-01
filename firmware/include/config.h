/**
 * @file config.h
 * @brief Firmware Pinout and System Parameter Configuration
 * @project Biometric School Attendance System
 */

#ifndef CONFIG_H
#define CONFIG_H

// Create local_config.h from local_config.example.h for local credentials.
// local_config.h is ignored by Git. Never put a real password in tracked files.
#if __has_include("local_config.h")
#include "local_config.h"
#endif

// Provisional ESP32 UART GPIO-matrix routing for the R307S optical fingerprint module.
// Observed harness wire order: 1: Red, 2: Black, 3: Yellow, 4: Green, 5: Blue, 6: White.
// DO NOT ASSUME WIRE COLORS PROVE THE PINOUT.
// Pin labels, supply voltage (5V vs 3.3V), and UART logic level are
// UNVERIFIED — HARDWARE VERIFICATION REQUIRED before connecting or powering the R307S.
// Refer to docs/r307s-integration-plan.md for the authoritative 10-phase integration sequence.
#define PIN_R307S_RX    32  // Connects to R307S TXD after level verification (<= 3.3V)
#define PIN_R307S_TX    33  // Connects to R307S RXD after logic verification
#define R307S_BAUD_RATE 57600  // Provisional default factory baud rate (confirm at handshake)

// Backward-compatibility aliases for existing code
#define PIN_R703_RX     PIN_R307S_RX
#define PIN_R703_TX     PIN_R307S_TX
#define R703_BAUD_RATE  R307S_BAUD_RATE

// I2C Bus - SSD1306 OLED & DS3231 RTC
#define PIN_I2C_SDA     21
#define PIN_I2C_SCL     22
#define OLED_I2C_ADDR   0x3C
#define RTC_I2C_ADDR    0x68
#define SCREEN_WIDTH    128
#define SCREEN_HEIGHT   64

// Actuators & Indicators
#define PIN_LED_GREEN   18  // Provisional success indicator
#define PIN_LED_RED     19  // Provisional error indicator
#define PIN_BUZZER      23  // Provisional active-buzzer module input

// Wi-Fi & Backend Server Settings (Configurable for Exhibition)
#ifndef DEFAULT_WIFI_SSID
#define DEFAULT_WIFI_SSID     ""
#endif
#ifndef DEFAULT_WIFI_PASSWORD
#define DEFAULT_WIFI_PASSWORD ""
#endif
#ifndef DEVICE_UUID
#define DEVICE_UUID ""
#endif
#ifndef DEVICE_TOKEN
#define DEVICE_TOKEN ""
#endif
#ifndef DEFAULT_SERVER_HOST
#define DEFAULT_SERVER_HOST   "192.168.137.1"
#endif
#ifndef DEFAULT_SERVER_PORT
#define DEFAULT_SERVER_PORT   8000
#endif
#define ATTENDANCE_ENDPOINT   "/api/v1/attendance"

#endif // CONFIG_H
