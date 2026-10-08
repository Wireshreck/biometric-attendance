#pragma once

#include <Arduino.h>
#include <freertos/semphr.h>

struct AttendanceEvent {
    char uuid[37];
    uint16_t slot;
    char capturedAt[32];
    char syncStatus[20];
};

class AttendanceStore {
public:
    bool begin();
    bool append(const AttendanceEvent& event);
    bool nextPending(AttendanceEvent& event);
    bool acknowledge(const char* uuid);
    size_t pendingCount();
    size_t totalCount();
    bool readAll(AttendanceEvent* out, size_t capacity, size_t& count);
    bool clear();
    bool healthy() const { return healthy_; }
private:
    bool healthy_ = false;
    SemaphoreHandle_t mutex_ = nullptr;
    bool compactLocked();
};
