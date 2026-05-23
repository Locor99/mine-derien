#pragma once

#include <Arduino.h>

struct PwmTiming {
  uint32_t onMicros;
  uint32_t offMicros;
};

PwmTiming computePwmTiming(uint16_t frequencyHz, uint8_t dutyCyclePercent);
