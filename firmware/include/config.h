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

// Owner-reported current bench routing: R307S TXD (yellow) -> ESP32 RX GPIO32;
// R307S RXD (green) <- ESP32 TX GPIO33; red -> VIN, black -> GND; blue/white open.
// Harness/pad mapping is reported by the owner but not independently measured here.
// Sensor rail and TX logic voltage remain UNVERIFIED — REQUIRES MULTIMETER.
#define PIN_R307S_RX    32  // Connects to R307S TXD after level verification (<= 3.3V)
#define PIN_R307S_TX    33  // Connects to R307S RXD after logic verification
#define R307S_BAUD_RATE 57600  // Provisional default factory baud rate (confirm at handshake)

// I2C Bus - DS3231 RTC (OLED removed from this project)
#define PIN_I2C_SDA     21
#define PIN_I2C_SCL     22
#define RTC_I2C_ADDR    0x68

// Actuators & Indicators
#define PIN_BUZZER      23  // Provisional active-buzzer module input

// Legacy GPIO assignments removed with OLED/LED hardware:
//   GPIO18 and GPIO19 were green/red indicator outputs.
//   They are currently unused/reserved. Do not add new hardware here without updating this file and the docs.

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
#define LOCAL_TIMEZONE_OFFSET "+05:30" // DS3231 stores wall clock; backend normalizes offset to UTC.
#define SENSOR_RETRY_MS 5000UL
#define NETWORK_RETRY_MS 10000UL
#define HTTP_TIMEOUT_MS 4000
#define QUEUE_PATH "/attendance.jsonl"
#define QUEUE_MAX_BYTES (48 * 1024)
#define QUEUE_MAX_PENDING 100
#define FINGER_SCAN_INTERVAL_MS 100UL
#define FINGER_DEBOUNCE_MS 1800UL
#define SERIAL_LINE_MAX 96

#endif // CONFIG_H
