#include "cycle.h"
#include "sections.h"
#include "serial_commands.h"
#include "track_controller.h"

constexpr uint32_t SERIAL_BAUD = 115200;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(SERIAL_BAUD);
  TrackController::initialize();
  clearForcedPresence();
}

void loop() {
  processSerialInput();
  Cycle::update();
}
