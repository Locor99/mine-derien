#include "cycle.h"
#include "pins.h"
#include "sections.h"
#include "timing.h"

namespace {
enum Phase { STOPPED, POWERED, RESTING };

Phase phase = STOPPED;
uint32_t phaseStartMicros = 0;
uint32_t poweredDurationMicros = 0;
uint32_t restingDurationMicros = 0;

void energizeEverySection() {
  for (uint8_t section = 0; section < SECTION_COUNT; section++) {
    energizeSection(section);
  }
}

void enterPhase(Phase next) {
  phase = next;
  phaseStartMicros = micros();
}

bool phaseElapsed(uint32_t durationMicros) {
  return micros() - phaseStartMicros >= durationMicros;
}
}

namespace Cycle {

void start(uint16_t frequencyHz, uint8_t dutyCyclePercent) {
  PwmTiming timing = computePwmTiming(frequencyHz, dutyCyclePercent);
  poweredDurationMicros = timing.onMicros;
  restingDurationMicros = timing.offMicros;
  scanAllSections();
  energizeEverySection();
  enterPhase(POWERED);
}

void stop() {
  phase = STOPPED;
  deenergizeAllSections();
}

void update() {
  if (phase == POWERED && phaseElapsed(poweredDurationMicros)) {
    deenergizeAllSections();
    enterPhase(RESTING);
  } else if (phase == RESTING && phaseElapsed(restingDurationMicros)) {
    scanAllSections();
    energizeEverySection();
    enterPhase(POWERED);
  }
}

}
