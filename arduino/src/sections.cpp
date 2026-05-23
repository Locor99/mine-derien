#include "sections.h"
#include "pins.h"
#include "track_controller.h"

bool trainPresent[SECTION_COUNT];

namespace {
constexpr int8_t NOT_FORCED = -1;
int8_t forcedPresence[SECTION_COUNT];

constexpr uint16_t OVERDRIVE_PAUSE_MICROS = 350;
constexpr uint8_t OVERDRIVE_GROUP_1_END = 8;
constexpr uint8_t OVERDRIVE_GROUP_2_END = 16;

void pulseOverdriveGroup(uint8_t firstSection, uint8_t endSection) {
  for (uint8_t section = firstSection; section < endSection; section++) {
    pulseOverdrive(section);
  }
  delayMicroseconds(OVERDRIVE_PAUSE_MICROS);
}
}

bool scanSection(uint8_t section) {
  TrackController::setAddress(section, false);
  TrackController::latch();
  bool present = TrackController::senseTrainPresence();
  TrackController::releaseAll();
  TrackController::pulseEndTransaction();
  return present;
}

void scanAllSections() {
  for (uint8_t section = 0; section < SECTION_COUNT; section++) {
    if (forcedPresence[section] != NOT_FORCED) {
      trainPresent[section] = forcedPresence[section] != 0;
    } else {
      trainPresent[section] = scanSection(section);
    }
  }
}

void forcePresence(uint8_t section, bool present) {
  if (section < SECTION_COUNT) {
    forcedPresence[section] = present ? 1 : 0;
  }
}

void clearForcedPresence() {
  for (uint8_t section = 0; section < SECTION_COUNT; section++) {
    forcedPresence[section] = NOT_FORCED;
  }
}

void energizeSection(uint8_t section) {
  TrackController::setAddress(section, true);
  TrackController::latch();
  TrackController::releaseAll();
}

void deenergizeAllSections() {
  for (uint8_t section = 0; section < SECTION_COUNT; section++) {
    TrackController::setAddress(0, false);
    TrackController::latch();
    TrackController::releaseAll();
    TrackController::pulseEndTransaction();
  }
}

void pulseOverdrive(uint8_t section) {
  TrackController::setAddress(section, true);
  TrackController::releaseAll();
  TrackController::latch();
}

void runOverdriveCycle() {
  pulseOverdriveGroup(0, OVERDRIVE_GROUP_1_END);
  pulseOverdriveGroup(OVERDRIVE_GROUP_1_END, OVERDRIVE_GROUP_2_END);
  pulseOverdriveGroup(OVERDRIVE_GROUP_2_END, SECTION_COUNT);
  TrackController::setAddress(0, false);
  TrackController::latch();
  TrackController::releaseAll();
  TrackController::pulseEndTransaction();
}
