#include <Arduino.h>
#include <stdlib.h>
#include <string.h>
#include "serial_commands.h"
#include "sections.h"
#include "track_controller.h"

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

bool dispatchBasicCommand(char* tokens[], uint8_t count) {
  if (strcmp(tokens[0], "PING") == 0) {
    Serial.println("PONG");
    blinkAcknowledge();
  } else if (strcmp(tokens[0], "SET") == 0 && count == 3) {
    uint8_t pin = atoi(tokens[1]);
    pinMode(pin, OUTPUT);
    digitalWrite(pin, atoi(tokens[2]) != 0 ? HIGH : LOW);
    Serial.println("OK");
  } else if (strcmp(tokens[0], "GET") == 0 && count == 2) {
    uint8_t pin = atoi(tokens[1]);
    pinMode(pin, INPUT);
    Serial.println(digitalRead(pin) == HIGH ? 1 : 0);
  } else {
    return false;
  }
  return true;
}

bool dispatchTrackControllerCommand(char* tokens[], uint8_t count) {
  if (strcmp(tokens[0], "TC_ADDR") == 0 && count == 3) {
    TrackController::setAddress(atoi(tokens[1]), atoi(tokens[2]) != 0);
    Serial.println("OK");
  } else if (strcmp(tokens[0], "TC_LATCH") == 0) {
    TrackController::latch();
    Serial.println("OK");
  } else if (strcmp(tokens[0], "TC_END") == 0) {
    TrackController::endTransaction();
    Serial.println("OK");
  } else if (strcmp(tokens[0], "TC_RELEASE_ALL") == 0) {
    TrackController::releaseAll();
    Serial.println("OK");
  } else if (strcmp(tokens[0], "TC_SENSE") == 0) {
    Serial.println(TrackController::senseTrainPresence() ? 1 : 0);
  } else {
    return false;
  }
  return true;
}

bool dispatchSectionCommand(char* tokens[], uint8_t count) {
  if (strcmp(tokens[0], "SCAN") == 0 && count == 2) {
    Serial.println(scanSection(atoi(tokens[1])) ? 1 : 0);
  } else if (strcmp(tokens[0], "ENERGIZE") == 0 && count == 2) {
    energizeSection(atoi(tokens[1]));
    Serial.println("OK");
  } else if (strcmp(tokens[0], "DEENERGIZE_ALL") == 0) {
    deenergizeAllSections();
    Serial.println("OK");
  } else if (strcmp(tokens[0], "OVERDRIVE") == 0 && count == 2) {
    pulseOverdrive(atoi(tokens[1]));
    Serial.println("OK");
  } else {
    return false;
  }
  return true;
}

void dispatchCommand(char* line) {
  char* tokens[MAX_TOKENS];
  uint8_t count = tokenize(line, tokens);
  if (count == 0) {
    return;
  }
  if (dispatchBasicCommand(tokens, count)) {
    return;
  }
  if (dispatchTrackControllerCommand(tokens, count)) {
    return;
  }
  if (dispatchSectionCommand(tokens, count)) {
    return;
  }
  Serial.println("ERR");
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
