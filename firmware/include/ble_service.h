#pragma once

#include <Arduino.h>

class RtcService;
class FingerprintService;
class IndicatorService;
class AttendanceStore;

// BLE device-management service. See docs/protocol.md.
// handleCommand() implements the full JSON command table and is shared by
// all transports (BLE characteristics, USB serial mirror). It never fakes
// hardware results: unavailable subsystems report error/SKIPPED, never PASS.
class BleService {
public:
    // Optional notify hook: invoked with JSON progress envelopes
    // (e.g. enrollment states) while a blocking command runs.
    typedef void (*NotifyFn)(const char* json);

    void configure(RtcService* rtc, FingerprintService* fp,
                   IndicatorService* buzzer, AttendanceStore* store);
    void setNotify(NotifyFn fn) { notify_ = fn; }

    // Parse request JSON, execute against real hardware/storage, write
    // response JSON. Returns true when a response was produced.
    bool handleCommand(const char* requestJson, char* responseOut, size_t responseSize);

    // BLE GATT lifecycle (no-op and returns false when BLE unavailable).
    bool begin(const char* deviceName);
    bool running() const { return running_; }
    void poll();

private:
    RtcService* rtc_ = nullptr;
    FingerprintService* fp_ = nullptr;
    IndicatorService* buzzer_ = nullptr;
    AttendanceStore* store_ = nullptr;
    NotifyFn notify_ = nullptr;
    bool running_ = false;
    uint32_t bootMs_ = 0;

    void emit(const char* json);
};
