#pragma once

#include <Arduino.h>
#include <Adafruit_Fingerprint.h>
#include <RTClib.h>
#include <freertos/semphr.h>

enum class FingerprintScan { NO_FINGER, MATCH, NO_MATCH, SENSOR_ERROR };

class RtcService {
public:
    bool begin();
    bool valid() const { return valid_; }
    bool ready() const { return ready_; }
    bool lostPower();
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
    void setReport(void (*report)(const char*));
    void shortBeep();
    void successPulse();
    void failurePulse();
    void twoBeep();
    bool selfTest();
private:
    void (*report_)(const char*) = nullptr;
};

enum class EnrollResult {
    OK,
    NO_SENSOR,
    BAD_SLOT,
    STORAGE_FULL,
    CANCELLED,
    TIMEOUT_FIRST,
    BAD_IMAGE_FIRST,
    DUPLICATE,
    TIMEOUT_REMOVAL,
    TIMEOUT_SECOND,
    BAD_IMAGE_SECOND,
    MISMATCH,
    STORE_FAILED
};

class FingerprintService {
public:
    FingerprintService();
    bool begin();
    bool identify(uint16_t& slotId, uint16_t& confidence);
    FingerprintScan scan(uint16_t& slotId, uint16_t& confidence);
    EnrollResult enroll(uint16_t slotId, void (*prompt)(const char*, const char*));
    void cancelEnroll();
    bool isEnrolling() const { return enrolling_; }
    bool readInventory(uint16_t& capacity, uint16_t& usedTemplates);
    bool getCount(uint16_t& capacity, uint16_t& used);
    bool deleteModel(uint16_t slotId);
    bool deleteAll();
    bool ready() const { return ready_; }
private:
    HardwareSerial serial_;
    Adafruit_Fingerprint sensor_;
    bool ready_ = false;
    volatile bool cancelEnroll_ = false;
    bool enrolling_ = false;
    SemaphoreHandle_t mutex_ = nullptr;
    uint8_t errStreak_ = 0;
};
