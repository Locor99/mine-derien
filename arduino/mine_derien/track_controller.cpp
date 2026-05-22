#include "track_controller.h"
#include "pins.h"

namespace {
constexpr uint8_t POWER_FLAG_MASK = 0x80;
constexpr uint8_t MODULE_ACTIVE_LEVEL = LOW;
constexpr uint8_t MODULE_INACTIVE_LEVEL = HIGH;
}

namespace TrackController {

void initialize() {
  ADDRESS_BUS_DIRECTION = 0xFF;
  ADDRESS_BUS_PORT = 0x00;
  pinMode(PIN_LATCH, OUTPUT);
  pinMode(PIN_TRANSACTION_END, OUTPUT);
  pinMode(PIN_TRAIN_SENSE, INPUT);
  releaseAll();
}

void setAddress(uint8_t section, bool power) {
  ADDRESS_BUS_PORT = power ? (section | POWER_FLAG_MASK) : section;
}

void latch() {
  digitalWrite(PIN_LATCH, MODULE_ACTIVE_LEVEL);
}

void releaseLatch() {
  digitalWrite(PIN_LATCH, MODULE_INACTIVE_LEVEL);
}

void endTransaction() {
  digitalWrite(PIN_TRANSACTION_END, MODULE_ACTIVE_LEVEL);
}

void releaseAll() {
  digitalWrite(PIN_LATCH, MODULE_INACTIVE_LEVEL);
  digitalWrite(PIN_TRANSACTION_END, MODULE_INACTIVE_LEVEL);
}

bool senseTrainPresence() {
  return digitalRead(PIN_TRAIN_SENSE) == HIGH;
}

}
