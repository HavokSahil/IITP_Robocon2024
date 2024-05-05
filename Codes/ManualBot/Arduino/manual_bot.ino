#include "ManualBot.h"
#include <WiFi.h>
#include <AsyncTCP.h>
#include <AsyncWebSocket.h>
#include <ArduinoJson.h>

#define DRIVE_PWM_1 22
#define DRIVE_PWM_2 12
#define DRIVE_PWM_3 19
#define DRIVE_PWM_4 14

#define DRIVE_DIR_1 23
#define DRIVE_DIR_2 13
#define DRIVE_DIR_3 21
#define DRIVE_DIR_4 18

#define RX_ARDUINO_COMM 16
#define TX_ARDUINO_COMM 17

#define DEVICE_NAME "ESP32 MANUAL"
#define BAUD_RATE 115200

int pos_JOYSTICK_X = 0;
int pos_JOYSTICK_Y = 0;
float pos_ROTSTICK_y = 0;

ManualBot myManualBot(DRIVE_PWM_1, DRIVE_DIR_1, DRIVE_PWM_2, DRIVE_DIR_2, DRIVE_PWM_3, DRIVE_DIR_3, DRIVE_PWM_4, DRIVE_DIR_4, RX_ARDUINO_COMM, TX_ARDUINO_COMM);
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

const char *ssid = "7.0 GHz";
const char *password = "havoksahil";

// initial value for trigger button states
String val1 = "false";
String val2 = "false";
String val3 = "false";\
String val4 = "false";

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
  myManualBot.setMotorSpeedCoefficients(1, 1, 1, 1);
}

void loop() {
  // put your main code here, to run repeatedly:
  myManualBot.drive(pos_JOYSTICK_X, pos_JOYSTICK_Y);
  // Serial.println(pos_ROTSTICK_y);
  if (pos_ROTSTICK_y>0) {
    myManualBot.rotCLK(pos_ROTSTICK_y);
  } else if (pos_ROTSTICK_y<0) {
    myManualBot.rotACLK(pos_ROTSTICK_y);
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
    if (jsonDocument.containsKey("y")) {
        int _ = jsonDocument["y"];
        pos_ROTSTICK_y = (float)_/1000.0;
    } 
  if (jsonDocument.containsKey("type") && (jsonDocument["type"]=="BSTS")) {
    if (jsonDocument.containsKey("grab") && jsonDocument.containsKey("arm1") && jsonDocument.containsKey("shoot") && jsonDocument.containsKey("stop")) {
      // presently not connected
      String grab = jsonDocument["grab"];
      String arm = jsonDocument["arm1"];
      String shoot = jsonDocument["shoot"];
      String stop = jsonDocument["stop"];
      
      if (shoot!=val3) {
        myManualBot.triggerShooting();
      }
      else if (grab!=val1) {
        val1 = grab;
        if (val1=="true") {
          myManualBot.triggerGRAB(true);
        } else {
          myManualBot.triggerGRAB(false);
        }
      }
      else if (arm!=val2) {
        val2 = arm;
        if (val2 == "true") {
          myManualBot.triggerPICK(true);
        } else {
          myManualBot.triggerPICK(false);
        }
      }
      else if (stop!=val4) {
        val4 = stop;
        if (val4 == "true") {
          myManualBot.triggerStop();
        }
      }
    };
  }
}