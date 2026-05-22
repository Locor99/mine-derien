#include <Arduino.h>
#include <stdlib.h>
#include <string.h>
#include "serial_commands.h"

namespace {
constexpr uint8_t LINE_BUFFER_SIZE = 64;
constexpr uint8_t MAX_TOKENS = 4;
constexpr uint16_t ACKNOWLEDGE_BLINK_MS = 40;

char lineBuffer[LINE_BUFFER_SIZE];
uint8_t lineLength = 0;

void blinkAcknowledge() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(ACKNOWLEDGE_BLINK_MS);
  digitalWrite(LED_BUILTIN, LOW);
}

uint8_t tokenize(char* line, char* tokens[]) {
  uint8_t count = 0;
  char* token = strtok(line, " ");
  while (token != nullptr && count < MAX_TOKENS) {
    tokens[count++] = token;
    token = strtok(nullptr, " ");
  }
  return count;
}

void handlePing() {
  Serial.println("PONG");
  blinkAcknowledge();
}

void handleSetPin(uint8_t pin, int value) {
  pinMode(pin, OUTPUT);
  digitalWrite(pin, value != 0 ? HIGH : LOW);
  Serial.println("OK");
}

void handleGetPin(uint8_t pin) {
  pinMode(pin, INPUT);
  Serial.println(digitalRead(pin) == HIGH ? 1 : 0);
}

void dispatchCommand(char* line) {
  char* tokens[MAX_TOKENS];
  uint8_t count = tokenize(line, tokens);
  if (count == 0) {
    return;
  }

  if (strcmp(tokens[0], "PING") == 0) {
    handlePing();
  } else if (strcmp(tokens[0], "SET") == 0 && count == 3) {
    handleSetPin(atoi(tokens[1]), atoi(tokens[2]));
  } else if (strcmp(tokens[0], "GET") == 0 && count == 2) {
    handleGetPin(atoi(tokens[1]));
  } else {
    Serial.println("ERR");
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
