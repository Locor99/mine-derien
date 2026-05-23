#pragma once

#include <Arduino.h>

constexpr uint8_t SECTION_COUNT = 37;

#define ADDRESS_BUS_PORT PORTA
#define ADDRESS_BUS_DIRECTION DDRA

constexpr uint8_t PIN_LATCH = 30;
constexpr uint8_t PIN_TRANSACTION_END = 31;
constexpr uint8_t PIN_TRAIN_SENSE = 32;
