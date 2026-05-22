#pragma once

#include <Arduino.h>

namespace TrackController {

void initialize();
void setAddress(uint8_t section, bool power);
void latch();
void endTransaction();
void releaseAll();
bool senseTrainPresence();

}
