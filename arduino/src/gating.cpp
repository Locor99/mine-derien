#include "gating.h"
#include "sections.h"

namespace {
constexpr uint8_t SLOW_CYCLE_PERIOD = 9;
constexpr uint8_t SLOW_CYCLE_PHASE = 1;

bool isInSlowCycleZone(uint8_t section, uint32_t cycleCount) {
  if (cycleCount % SLOW_CYCLE_PERIOD != SLOW_CYCLE_PHASE) {
    return false;
  }
  return section == 0 || section == 1 || section == 2
      || section == 7 || section == 14;
}

bool isUpstreamOfTrainInSection8(uint8_t section) {
  if (!trainPresent[8]) {
    return false;
  }
  return section == 0 || section == 1 || section == 2 || section == 7;
}

bool isApproachOccupied() {
  return trainPresent[0] || trainPresent[1]
      || trainPresent[2] || trainPresent[3];
}

bool isJunctionBlockedByApproachingTrain(uint8_t section) {
  if (section != 8 && section != 15) {
    return false;
  }
  return isApproachOccupied();
}

bool isSection14BlockedByTrainsBeforeIt(uint8_t section) {
  if (section != 14) {
    return false;
  }
  return trainPresent[2] || trainPresent[3];
}
}

bool shouldSkipSection(uint8_t section, uint32_t cycleCount) {
  return isInSlowCycleZone(section, cycleCount)
      || isUpstreamOfTrainInSection8(section)
      || isJunctionBlockedByApproachingTrain(section)
      || isSection14BlockedByTrainsBeforeIt(section);
}
