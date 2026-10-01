/**
 * @file main.cpp
 * @brief Pre-Development Toolchain & Hardware Configuration Validation
 * @project Biometric School Attendance System
 * 
 * NOTE: This is NOT the attendance application implementation.
 * This sketch exists strictly to validate that the ESP32 toolchain,
 * Arduino framework, board configuration, and third-party libraries
 * compile cleanly and deterministically.
 */

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <RTClib.h>
#include <Adafruit_Fingerprint.h>
#include <ArduinoJson.h>

#include "config.h"
#include "r307s_uart_diag.h"

// NOTE: All GPIO assignments now come from firmware/include/config.h
// (single source of truth). The previously hard-coded PIN_R703_RX 16 /
// PIN_R703_TX 17 defines here were STALE and have been removed; the
// R307S UART uses PIN_R307S_RX (32) / PIN_R307S_TX (33) from config.h.

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("==================================================");
    Serial.println("  Biometric Attendance System - Toolchain Check   ");
    Serial.println("  Status: PRE-DEVELOPMENT TOOLCHAIN CHECK          ");
    Serial.println("==================================================");

    // Pin mode setup
    pinMode(PIN_LED_GREEN, OUTPUT);
    pinMode(PIN_LED_RED, OUTPUT);
    pinMode(PIN_BUZZER, OUTPUT);

    digitalWrite(PIN_LED_GREEN, LOW);
    digitalWrite(PIN_LED_RED, LOW);
    digitalWrite(PIN_BUZZER, LOW);

    Serial.printf("ESP32 Chip Model: %s (Rev %d)\n", ESP.getChipModel(), ESP.getChipRevision());
    Serial.printf("CPU Frequency: %d MHz\n", ESP.getCpuFreqMHz());
    Serial.printf("Free Heap: %d bytes\n", ESP.getFreeHeap());
    Serial.println("If this message is visible, the validation sketch is running.");

    // R307S Phase 4/5 UART bring-up diagnostic (docs/r307s-integration-plan.md).
    // Runs ONCE after a settle delay, then the sketch returns to idle. Delete
    // this call plus r307s_uart_diag.{h,cpp} once the real driver lands.
    delay(2000);  // Let the R307S finish its own power-on boot before probing.
    r307s_uart_diag_run();
}

void loop() {
    // Idle loop for verification firmware (never blocks on the sensor).
    delay(5000);
}
