#pragma once

#include <Arduino.h>

bool scanSection(uint8_t section);
void energizeSection(uint8_t section);
void deenergizeAllSections();
void pulseOverdrive(uint8_t section);
