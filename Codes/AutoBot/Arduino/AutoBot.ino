#include "autobot.h"
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <AsyncWebSocket.h>
#include <ArduinoJson.h>


#define PWM_PIN_1 12
#define PWM_PIN_2 19
#define PWM_PIN_3 27
#define PWM_PIN_4 26

#define DIR_PIN_1 13
#define DIR_PIN_2 21
#define DIR_PIN_3 18
#define DIR_PIN_4 23

#define CAM_SERVO_PIN 25
#define GRAB_SERVO_PIN 32

#define STEPPER_PWM_PIN 33
#define STEPPER_DIR_PIN 22

#define RX_ARDUINO_COMM 16
#define TX_ARDUINO_COMM 17

#define DEVICE_NAME "ESP32 MANUAL"
#define BAUD_RATE 115200

#define NORMAL_SPEED 20
#define FOCUS_SPEED 10

AutoBot myAutoBot(PWM_PIN_1, DIR_PIN_1, PWM_PIN_2, DIR_PIN_2, PWM_PIN_3, DIR_PIN_3, PWM_PIN_4, DIR_PIN_4, RX_ARDUINO_COMM, TX_ARDUINO_COMM, CAM_SERVO_PIN, GRAB_SERVO_PIN, STEPPER_PWM_PIN, STEPPER_DIR_PIN);
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

// temporary
bool DEBUG = false;
int speed1 = 0;
int speed2 = 0;
int speed3 = 0;
int speed4 = 0;

const char *ssid = "7.0 GHz";
const char *password = "havoksahil";
void setup() {
  Serial.begin(BAUD_RATE);
  Serial2.begin(BAUD_RATE, SERIAL_8N1, RX_ARDUINO_COMM, TX_ARDUINO_COMM);
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
  myAutoBot.setOperatingSpeed(20);
  myAutoBot.setMotorSpeedCoefficients(1, 1, 1, 1);
  myAutoBot.initServo();
  myAutoBot.setState('x');
}

void loop() {
  // put your main code here, to run repeatedly:
  // ball following mode
  //myAutoBot.StepUP();
  if (Serial.available()>0) {
    char val = Serial.read();
      if (val>='a' && val<='z')
        myAutoBot.setState(val);
  }
  Serial.println(myAutoBot.getState());

  if (myAutoBot.getState() == BOT_FORWARD) {
    myAutoBot.driveFRONT();
  }
  else if (myAutoBot.getState() == BOT_ROT_CLOCK) {
    myAutoBot.rotCLK();
  } 
  else if (myAutoBot.getState() == BOT_ROT_ACLOCK) {
    myAutoBot.rotACLK();
  }
  else if(myAutoBot.getState()==TRIGGER_GRIPPER_ACT)
  {
    myAutoBot.pick();
    myAutoBot.setState(BOT_IDLE);
  }
  else if (myAutoBot.getState() == TRIGGER_GRIPPER_DEACT) {
    myAutoBot.drop();
    myAutoBot.setState(BOT_IDLE);
  }
  else if(myAutoBot.getState()== CAM_ROT_DOWN)
  {
    myAutoBot.camRotdown();
  }
  else if(myAutoBot.getState()==CAM_ROT_UP)
  {
    myAutoBot.camRotup();
  }
  else if (myAutoBot.getState()==BOT_LOWER_SPEED) {
    myAutoBot.setOperatingSpeed(10);
    myAutoBot.setState('x');
  }
  else if (myAutoBot.getState()==BOT_UPPER_SPEED) {
    myAutoBot.setOperatingSpeed(20);
    myAutoBot.setState('x');
  }
  else if (myAutoBot.getState() == STEPPER_UP) {
    myAutoBot.StepUp();
  }
  else if (myAutoBot.getState() == STEPPER_DOWN) {
    myAutoBot.StepDown();
  } else {
    if (!(speed1 || speed2 || speed3 || speed4)) {
      myAutoBot.stop();
    }
  }

  if (speed1 || speed2 || speed3 || speed4) {
    int speeds[4] = {speed1, speed2, speed3, speed4};
    myAutoBot.setWheelSpeeds(speeds);
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
    return;
  }

  if (jsonDocument.containsKey("type") && (jsonDocument["type"]=="MCMD")) {
    if (jsonDocument.containsKey("cmd")) {
      String val = jsonDocument["cmd"];
      char cmd = val[0];
      myAutoBot.setState(cmd);
    }
  }
  else if (jsonDocument.containsKey("type") && (jsonDocument["type"] == "DV")) {
    if (jsonDocument.containsKey("speed1") && jsonDocument.containsKey("speed2") && jsonDocument.containsKey("speed3") && jsonDocument.containsKey("speed4")) {
      if (DEBUG) DEBUG = false;
      speed1 = (int)jsonDocument["speed1"];
      speed2 = (int)jsonDocument["speed2"];
      speed3 = (int)jsonDocument["speed3"];
      speed4 = (int)jsonDocument["speed4"];
    }
  } else if (jsonDocument.containsKey("type") && (jsonDocument["type"] == "DBG")) {
    if (jsonDocument.containsKey("speed1") && jsonDocument.containsKey("speed2") && jsonDocument.containsKey("speed3") && jsonDocument.containsKey("speed4")) {
      if (!DEBUG) DEBUG = true;
      speed1 = (int)jsonDocument["speed1"];
      speed2 = (int)jsonDocument["speed2"];
      speed3 = (int)jsonDocument["speed3"];
      speed4 = (int)jsonDocument["speed4"];
    }
  } else if (jsonDocument.containsKey("type") && (jsonDocument["type"] == "SDV")) {
    if (jsonDocument.containsKey("speed1") && jsonDocument.containsKey("speed2") && jsonDocument.containsKey("speed3") && jsonDocument.containsKey("speed4")) {
      if (DEBUG) DEBUG = false;
      speed1 = (int)jsonDocument["speed1"];
      speed2 = (int)jsonDocument["speed2"];
      speed3 = (int)jsonDocument["speed3"];
      speed4 = (int)jsonDocument["speed4"];
    }
  }
}