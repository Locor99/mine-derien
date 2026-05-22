#include "serial_commands.h"

constexpr uint32_t SERIAL_BAUD = 115200;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(SERIAL_BAUD);
}

void loop() {
  processSerialInput();
}
