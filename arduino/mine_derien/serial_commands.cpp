#include <Arduino.h>
#include <string.h>
#include "serial_commands.h"

namespace {
constexpr uint8_t LINE_BUFFER_SIZE = 64;
constexpr uint16_t ACKNOWLEDGE_BLINK_MS = 40;

char lineBuffer[LINE_BUFFER_SIZE];
uint8_t lineLength = 0;

void blinkAcknowledge() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(ACKNOWLEDGE_BLINK_MS);
  digitalWrite(LED_BUILTIN, LOW);
}

void dispatchCommand(const char* command) {
  if (strcmp(command, "PING") == 0) {
    Serial.println("PONG");
    blinkAcknowledge();
  }
}

void consumeCompletedLine() {
  lineBuffer[lineLength] = '\0';
  dispatchCommand(lineBuffer);
  lineLength = 0;
}
}

void processSerialInput() {
  while (Serial.available() > 0) {
    char received = Serial.read();
    bool endOfLine = received == '\n' || received == '\r';
    if (endOfLine) {
      if (lineLength > 0) {
        consumeCompletedLine();
      }
    } else if (lineLength < LINE_BUFFER_SIZE - 1) {
      lineBuffer[lineLength++] = received;
    }
  }
}
