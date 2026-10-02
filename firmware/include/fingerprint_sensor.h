#pragma once

/**
 * DEPRECATED planning-only fingerprint interface.
 *
 * This header used to declare functions that had no implementation. The active,
 * build-tested wrapper is FingerprintService in device_services.h, implemented
 * in src/hardware/device_services.cpp. No production source includes this file.
 * Keep this notice to direct future work to the single active implementation;
 * do not add a second sensor driver here.
 */
