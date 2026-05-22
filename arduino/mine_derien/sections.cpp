#include "sections.h"
#include "pins.h"
#include "track_controller.h"

bool scanSection(uint8_t section) {
  TrackController::setAddress(section, false);
  TrackController::latch();
  bool present = TrackController::senseTrainPresence();
  TrackController::releaseAll();
  TrackController::endTransaction();
  return present;
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
    TrackController::endTransaction();
  }
}

void pulseOverdrive(uint8_t section) {
  TrackController::setAddress(section, true);
  TrackController::releaseAll();
  TrackController::latch();
}
