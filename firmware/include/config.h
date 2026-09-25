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

// Provisional ESP32 UART GPIO-matrix routing for AS608; verify exact board/module.
// Never rely on wire colors. GPIO16/17 may be occupied by PSRAM on some modules.
#define PIN_AS608_RX    16  // Connects to the sensor TX signal after voltage check
#define PIN_AS608_TX    17  // Connects to the sensor RX signal after compatibility check
#define AS608_BAUD_RATE 57600

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
