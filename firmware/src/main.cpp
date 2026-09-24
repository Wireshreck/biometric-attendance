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

// GPIO Pin Definitions (as specified in docs/wiring.md)
#define PIN_AS608_RX 16
#define PIN_AS608_TX 17
#define PIN_I2C_SDA   21
#define PIN_I2C_SCL   22
#define PIN_LED_GREEN 18
#define PIN_LED_RED   19
#define PIN_BUZZER    23

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
}

void loop() {
    // Idle loop for verification firmware
    delay(5000);
}
