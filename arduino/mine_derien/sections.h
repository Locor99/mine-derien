#pragma once

#include <Arduino.h>
#include "pins.h"

extern bool trainPresent[SECTION_COUNT];

bool scanSection(uint8_t section);
void scanAllSections();
void energizeSection(uint8_t section);
void deenergizeAllSections();
void pulseOverdrive(uint8_t section);
void runOverdriveCycle();
void forcePresence(uint8_t section, bool present);
void clearForcedPresence();
