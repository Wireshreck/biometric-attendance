#pragma once

#include <Arduino.h>
#include <Adafruit_Fingerprint.h>
#include <Adafruit_SSD1306.h>
#include <RTClib.h>

enum class FingerprintScan { NO_FINGER, MATCH, NO_MATCH, SENSOR_ERROR };

class DisplayService {
public:
    DisplayService();
    bool begin();
    void show(const char* title, const char* detail = "");
    void showClock(const char* title, const char* detail, const char* timestamp);
private:
    Adafruit_SSD1306 display_;
    bool ready_ = false;
};

class RtcService {
public:
    bool begin();
    bool valid() const { return valid_; }
    bool read(DateTime& out);
    bool timestamp(char* out, size_t size);
    bool setLocalTime(uint16_t year, uint8_t month, uint8_t day, uint8_t hour, uint8_t minute, uint8_t second);
private:
    RTC_DS3231 rtc_;
    bool ready_ = false;
    bool valid_ = false;
};

class IndicatorService {
public:
    void begin();
    void successPulse();
    void failurePulse();
};

class FingerprintService {
public:
    FingerprintService();
    bool begin();
    bool identify(uint16_t& slotId, uint16_t& confidence);
    FingerprintScan scan(uint16_t& slotId, uint16_t& confidence);
    bool enroll(uint16_t slotId, void (*prompt)(const char*, const char*));
    bool readInventory(uint16_t& capacity, uint16_t& usedTemplates);
    bool ready() const { return ready_; }
private:
    HardwareSerial serial_;
    Adafruit_Fingerprint sensor_;
    bool ready_ = false;
};
