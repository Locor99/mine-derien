#include "timing.h"

PwmTiming computePwmTiming(uint16_t frequencyHz, uint8_t dutyCyclePercent) {
  uint32_t periodMicros = 1000000UL / frequencyHz;
  uint32_t onMicros = (periodMicros * dutyCyclePercent) / 100;
  uint32_t offMicros = periodMicros - onMicros;
  return {onMicros, offMicros};
}
