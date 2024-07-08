#include "autobot.h"
#include <ArduinoJson.h>

// PWM Pins for Motors
#define PWM_PIN_1 4 // 27 5
#define PWM_PIN_2 6 // 33 6
#define PWM_PIN_3 8 // 12 3
#define PWM_PIN_4 2 // 19 11

// Direction Pins for Motors
#define DIR_PIN_1 5 // 18 12
#define DIR_PIN_2 7 // 23 7
#define DIR_PIN_3 9 // 13 4
#define DIR_PIN_4 3 // 21 10

#define BAUD_RATE 9600

Servo gripServo;

AutoBot myAutoBot(
  PWM_PIN_1,
  DIR_PIN_1,
  PWM_PIN_2,
  DIR_PIN_2,
  PWM_PIN_3, 
  DIR_PIN_3, 
  PWM_PIN_4, 
  DIR_PIN_4);


double GRIPPER_SONIC_BUFFER[10];
double LEFT_SONIC_BUFFER[10];
double RIGHT_SONIC_BUFFER[10];

void setup() {
  Serial.begin(BAUD_RATE);
  myAutoBot.setMotorSpeedCoefficients(1.6, 1, 1.6, 1);
  myAutoBot.setDriveState(BOT_IDLE);
  myAutoBot.setPeriState(PERI_IDLE);
  gripServo.attach(PIN_SERVO_GRIPPER);
  pinMode(PIN_SONIC_TRIG, OUTPUT);
  pinMode(PIN_SONIC_ECHO, INPUT);
  pinMode(PIN_DIR_LIFTER, OUTPUT);
  pinMode(PIN_PWM_LIFTER, OUTPUT);
  pinMode(PIN_TACTILE_UP, INPUT);
  pinMode(PIN_TACTILE_DOWN, INPUT);
  pinMode(PIN_SONIC_LEFT_TRIG, OUTPUT);
  pinMode(PIN_SONIC_RIGHT_TRIG, OUTPUT);
  pinMode(PIN_SONIC_LEFT_ECHO, INPUT);
  pinMode(PIN_SONIC_RIGHT_ECHO, INPUT);

  digitalWrite(PIN_TACTILE_UP, LOW);


  double a = myAutoBot.getUltraDist(PIN_SONIC_TRIG, PIN_SONIC_ECHO);
  double b = myAutoBot.getUltraDist(PIN_SONIC_LEFT_TRIG, PIN_SONIC_LEFT_ECHO);
  double c = myAutoBot.getUltraDist(PIN_SONIC_RIGHT_TRIG, PIN_SONIC_RIGHT_ECHO);

  for (auto &x: GRIPPER_SONIC_BUFFER) x = a;
  for (auto &x: LEFT_SONIC_BUFFER) x = b;
  for (auto &x: RIGHT_SONIC_BUFFER) x = c;
}


void loop() {
  if (Serial.available()) {
    int ch = Serial.read();

    if ((ch>=(int)'a') && (ch <= (int)'z')) {
      myAutoBot.setDriveState((char)ch);

    } else if ((ch >= (int)'A') && (ch <= (int)'Z')) {
      if (ch == 'F')
        myAutoBot.setBroadcast(true);
      else if (ch == 'S')
        myAutoBot.setBroadcast(false);
      else
        myAutoBot.setPeriState((char)ch);
    } else if (ch != '\n') {
      myAutoBot.setRotatingSpeed(ch);
    }
  }

  Serial.print("The Speed is ");
  Serial.println(myAutoBot.ROTATING_SPEED);

  int a = digitalRead(PIN_TACTILE_DOWN);
  int b = digitalRead(PIN_TACTILE_UP);

  switch (myAutoBot.getDriveState()) {
    case BOT_FORWARD:
      myAutoBot.driveFRONT();
      break;
    case BOT_ROT_CLOCK:
      myAutoBot.rotCLK();
      break;
    case BOT_ROT_ACLOCK:
      myAutoBot.rotACLK();
      break;
    case BOT_RIGHT:
      myAutoBot.driveRIGHT();
      break;
    case BOT_LEFT:
      myAutoBot.driveLEFT();
      break;
    case BOT_BACKWARD:
      myAutoBot.driveREAR();
      break;

    default:
      myAutoBot.stop();
      break;
  }

  switch (myAutoBot.getPeriState()) {

    case TRIGGER_GRIPPER_CLOSE:
      myAutoBot.triggerGripper(GRIPPER_CLOSE, gripServo);
      break;
    
    case TRIGGER_GRIPPER_OPEN:
      myAutoBot.triggerGripper(GRIPPER_OPEN, gripServo);
      break;
    
    case TRIGGER_LIFTER_UP:
      myAutoBot.gripperUp();
      break;
    
    case TRIGGER_LIFTER_DOWN:
      myAutoBot.gripperDown();
      break;

    default:
      break;
    
  }

  if (myAutoBot.getBroadcast()) {
    myAutoBot.getLateralProximityReading();
  }

  myAutoBot.setPeriState(PERI_IDLE);

  delay(150);
}