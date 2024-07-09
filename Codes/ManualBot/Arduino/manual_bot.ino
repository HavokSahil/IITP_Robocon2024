#include "ManualBot.h"
#include <WiFi.h>
#include <AsyncTCP.h>
#include <AsyncWebSocket.h>
#include <ArduinoJson.h>

#define DRIVE_PWM_1 14
#define DRIVE_PWM_2 22
#define DRIVE_PWM_3 12
#define DRIVE_PWM_4 19

#define DRIVE_DIR_1 18
#define DRIVE_DIR_2 23
#define DRIVE_DIR_3 27
#define DRIVE_DIR_4 21

#define RX_ARDUINO_COMM 16
#define TX_ARDUINO_COMM 17

#define DEVICE_NAME "ESP32 MANUAL"
#define BAUD_RATE 115200

int pos_JOYSTICK_X = 0;
int pos_JOYSTICK_Y = 0;
int pos_ROTSTICK_X = 0;

ManualBot myManualBot(DRIVE_PWM_1, DRIVE_DIR_1, DRIVE_PWM_2, DRIVE_DIR_2, DRIVE_PWM_3, DRIVE_DIR_3, DRIVE_PWM_4, DRIVE_DIR_4, RX_ARDUINO_COMM, TX_ARDUINO_COMM);
AsyncWebServer server(80);
AsyncWebSocket ws("/");

const char *ssid = "Ayush";
const char *password = "AAAYUSHH";

void setup() {
  Serial.begin(BAUD_RATE);
  WiFi.begin(ssid, password);

  // connect to wifi network
  while (WiFi.status()!= WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi...");
  Serial.println(WiFi.localIP());
  ws.onEvent(onWebSocketEvent);
  server.addHandler(&ws);
  server.begin();
  myManualBot.setOperatingSpeed(100);
  myManualBot.setMotorSpeedCoefficients(1, 1, 1, 1.8);
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(WiFi.localIP());
  Serial.println(myManualBot.getState());

  if (myManualBot.getState() == 'x') {
    if (pos_ROTSTICK_X == 0) {
      myManualBot.drive(pos_JOYSTICK_X, pos_JOYSTICK_Y);
    }
    else {
      myManualBot.rotate(pos_ROTSTICK_X);
    }
  } else {
    if (myManualBot.getState() == 'w')
      myManualBot.driveFRONT();
    else if (myManualBot.getState() == 'a')
      myManualBot.driveLEFT();
    else if (myManualBot.getState() == 'z')
      myManualBot.driveRIGHT();
    else if (myManualBot.getState() == 'q')
      myManualBot.driveBACK();
    else if (myManualBot.getState() == '>')
      myManualBot.rotClock();
    else if (myManualBot.getState() == '<')
      myManualBot.rotAClock();
    else myManualBot.setState('x');
  }
}


void onWebSocketEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type, void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.println("WebSocket client connected");
      break;
    case WS_EVT_DISCONNECT:
      Serial.println("WebSocket client disconnected");
      break;
    case WS_EVT_DATA:
      handleWebSocketData(client, data, len);
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      
      break;
  }
}

void handleWebSocketData(AsyncWebSocketClient *client, uint8_t *data, size_t len) {
  // Convert the received data to a String
  String receivedData = String((char*)data);
  // Parse the JSON data using ArduinoJson library
  StaticJsonDocument<256> jsonDocument;
  DeserializationError error = deserializeJson(jsonDocument, receivedData);

  // Check for parsing errors
  if (error) {
    Serial.print("JSON parsing error: ");
    Serial.println(error.c_str());
    pos_JOYSTICK_X = 0; pos_JOYSTICK_Y=0;
    return;
  }

  if (jsonDocument.containsKey("type") && (jsonDocument["type"]=="PSJ"))
      if (jsonDocument.containsKey("x") && jsonDocument.containsKey("y")) {
        pos_JOYSTICK_X = jsonDocument["x"];
        pos_JOYSTICK_Y = jsonDocument["y"];
      }
  if (jsonDocument.containsKey("type") && jsonDocument["type"]=="RTJ")
    if (jsonDocument.containsKey("x")) {
        int _ = jsonDocument["x"];
        pos_ROTSTICK_X = _;
    } 
  if (jsonDocument.containsKey("type") && (jsonDocument["type"]=="BSTS")) {
    if (jsonDocument["action"]==TRIGGER_UP) {
      myManualBot.triggerLifter(true);
    }
    else if (jsonDocument["action"] == TRIGGER_DOWN) {
      myManualBot.triggerLifter(false);
    } 
    else if (jsonDocument["action"] == TRIGGER_STOP) {
      myManualBot.triggerStop();
    }
    else if (jsonDocument["action"] == TRIGGER_PNEUMATIC) {
      myManualBot.triggerShooting();
    }
    else if (jsonDocument["action"] == TRIGGER_GRAB_LEFT_POS) {
      myManualBot.triggerPickLeft(true);
    }
    else if (jsonDocument["action"] == TRIGGER_GRAB_LEFT_NEG) {
      myManualBot.triggerPickLeft(false);
    }
    else if (jsonDocument["action"] == TRIGGER_GRAB_RIGHT_POS) {
      myManualBot.triggerPickRight(true);
    }
    else if (jsonDocument["action"] == TRIGGER_GRAB_RIGHT_NEG) {
      myManualBot.triggerPickRight(false);
    }
    else if (jsonDocument["action"] == TRIGGER_BALL_GRAB_POS) {
      myManualBot.triggerGrab(true);
    }
    else if (jsonDocument["action"] == TRIGGER_BALL_GRAB_NEG) {
      myManualBot.triggerGrab(false);
    } 
    else if (jsonDocument["action"] == BOT_FORWARD) {
      myManualBot.setState('w');
    }
    else if (jsonDocument["action"] == BOT_LEFT) {
      myManualBot.setState('a');
    }
    else if (jsonDocument["action"] == BOT_RIGHT) {
      myManualBot.setState('z');
    }
    else if (jsonDocument["action"] == BOT_BACKWARD) {
      myManualBot.setState('q');
    }
    else if (jsonDocument["action"] == BOT_CLOCK) {
      myManualBot.setState('>');
    }
    else if (jsonDocument["action"] == BOT_ANTI_CLOCK) {
      myManualBot.setState('<');
    }
    else if (jsonDocument["action"] == BOT_IDLE) {
      myManualBot.setState('x');
    }
    else if (jsonDocument["action"] == ALTER_SPEED_COEFF) {
      float c1 = jsonDocument["c1"];
      float c2 = jsonDocument["c2"];
      float c3 = jsonDocument["c3"];
      float c4 = jsonDocument["c4"];

      myManualBot.setMotorSpeedCoefficients(c1, c2, c3, c4);
    }
  }
}