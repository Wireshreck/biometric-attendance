#pragma once

enum class AttendanceState {
    BOOT,
    SELF_TEST,
    READY,
    WAITING_FOR_FINGER,
    IDENTIFYING,
    ATTENDANCE_RECORDED,
    SYNCING,
    ERROR,
    OFFLINE,
    RECOVERY
};

const char* attendance_state_name(AttendanceState state);
