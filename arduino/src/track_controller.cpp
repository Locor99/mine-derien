#include "track_controller.h"
#include "pins.h"

namespace {
constexpr uint8_t POWER_FLAG_MASK = 0x80;
constexpr uint8_t MODULE_ACTIVE_LEVEL = LOW;
constexpr uint8_t MODULE_INACTIVE_LEVEL = HIGH;

void driveControlLines(uint8_t latchLevel, uint8_t transactionEndLevel) {
  digitalWrite(PIN_LATCH, latchLevel);
  digitalWrite(PIN_TRANSACTION_END, transactionEndLevel);
}
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
  driveControlLines(MODULE_ACTIVE_LEVEL, MODULE_INACTIVE_LEVEL);
}

void endTransaction() {
  driveControlLines(MODULE_INACTIVE_LEVEL, MODULE_ACTIVE_LEVEL);
}

void pulseEndTransaction() {
  endTransaction();
  releaseAll();
}

void releaseAll() {
  driveControlLines(MODULE_INACTIVE_LEVEL, MODULE_INACTIVE_LEVEL);
}

bool senseTrainPresence() {
  return digitalRead(PIN_TRAIN_SENSE) == HIGH;
}

}
