#pragma once

#include <Arduino.h>

namespace Cycle {

void start(uint16_t frequencyHz, uint8_t dutyCyclePercent);
void stop();
void update();

}
