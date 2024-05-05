#include "esp32-hal.h"
#include "esp32-hal-gpio.h"
#include <math.h>
#include "autobot.h"
#include <cmath>
#include <ESP32Servo.h>

AutoBot::AutoBot(int pwmPin1, int dirPin1, int pwmPin2, int dirPin2, int pwmPin3, int dirPin3, int pwmPin4, int dirPin4, int rx, int tx, int camservo_pin, int gservo_pin, int stepperPulse, int stepperDir)
{
  pwmPins[0] = pwmPin1;
  dirPins[0] = dirPin1;
  pwmPins[1] = pwmPin2;
  dirPins[1] = dirPin2;
  pwmPins[2] = pwmPin3;
  dirPins[2] = dirPin3;
  pwmPins[3] = pwmPin4;
  dirPins[3] = dirPin4;
  serialPins[0] = tx;
  serialPins[1] = rx;
  cServoPin = camservo_pin;
  gServoPin = gservo_pin;
  steppulse = stepperPulse;
  stepdir = stepperDir;

  state = 'x';

  // Initialise motor speed coefficients to 1.0 (no modification)
  for (int i = 0; i < 4; ++i) motorSpeedCoefficients[i] = 1.0;
  
  // setup pwm and dir pins
  for (int i = 0; i < 4; ++i) {
    pinMode(pwmPins[i], OUTPUT);
    pinMode(dirPins[i], OUTPUT);
  }

  pinMode(steppulse,OUTPUT);
  pinMode(stepdir,OUTPUT);

  // setting up rx and tx pins
  Serial2.begin(BAUD_RATE, SERIAL_8N1, rx, tx);

  // set default operating speed to max speed
  operatingSpeed = 40;
  //default cam state
  camMode=0;
  gripperState=0;
}

AutoBot::~AutoBot() {
  //Destructor
}

void AutoBot::setState(char val) {
  AutoBot::state = val;
}

char AutoBot::getState() {
  return AutoBot::state;
}

void AutoBot::setWheelSpeeds(int motorSpeeds[]) {
  Serial.print("[");
  for (int i = 0; i < 4; ++i) {
    // Ensure motor speeds are within valid range (-255 to 255)
    motorSpeeds[i] = constrain(motorSpeeds[i], -255, 255);

    // Set direction based on the sign of motor speed
    digitalWrite(dirPins[i], (motorSpeeds[i] >= 0) ? HIGH : LOW);

    // Set PWM signal
    analogWrite(pwmPins[i], abs(motorSpeeds[i]));

    // Print PWM values
    Serial.print(motorSpeeds[i]);
    if (i < 3) {
      Serial.print(", ");
    }
  }
  Serial.println("]");
}

// =============== Additional Servo Functions

void AutoBot::pick()
{
  if (gripperState == GRIPPER_INACTIVE)
  {
    for(int i=60;i>=20;i--)
    {
      Serial.println("pick");
      gservo.write(i);
      delay(20);
    }
    gripperState=GRIPPER_ACTIVE;
  }
}


void AutoBot::drop()
{
  if (gripperState==GRIPPER_ACTIVE)
  {
    for(int i=20;i<=60;i++)
    {
      Serial.println("drop");
      gservo.write(i);
      delay(20);
    }
    gripperState=GRIPPER_INACTIVE;
  }
}

void AutoBot::camRotdown()
{
  while(camMode==WATCH_MODE)
  {
    for(int i=120;i>=45;i--)
    {
      cservo.write(i);
    }
    camMode = FOCUS_MODE;
  }
}

void AutoBot::camRotup()
{
  while(camMode==FOCUS_MODE)
  {
    for(int i=45;i<=120;i++)
    {
      cservo.write(i);
    }
    camMode = WATCH_MODE;
  }
}

void AutoBot::rotCLK() {
  int motorSpeeds[4]=ROTATE_CLOCK;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * operatingSpeed;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * operatingSpeed;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * operatingSpeed;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * operatingSpeed;
  AutoBot::setWheelSpeeds(motorSpeeds);
}

void AutoBot::rotACLK() {
  int motorSpeeds[4] = ROTATE_ANTICLOCK;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * operatingSpeed;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * operatingSpeed;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * operatingSpeed;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * operatingSpeed;
  AutoBot::setWheelSpeeds(motorSpeeds);
}

void AutoBot::stop() {
  int motorSpeeds[4]=STOP;
  AutoBot::setWheelSpeeds(motorSpeeds);
}

void AutoBot::driveFRONT() {
  int motorSpeeds[4]=DRIVE_FRONT;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * operatingSpeed;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * operatingSpeed;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * operatingSpeed;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * operatingSpeed;
  setWheelSpeeds(motorSpeeds);
}

void AutoBot::driveLEFT() {
  int motorSpeeds[4]=DRIVE_LEFT;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * operatingSpeed;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * operatingSpeed;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * operatingSpeed;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * operatingSpeed;
  setWheelSpeeds(motorSpeeds);
}

void AutoBot::driveRIGHT() {
  int motorSpeeds[4]=DRIVE_RIGHT;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * operatingSpeed;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * operatingSpeed;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * operatingSpeed;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * operatingSpeed;
  setWheelSpeeds(motorSpeeds);
}

void AutoBot::driveREAR() {
  int motorSpeeds[4]=DRIVE_REAR;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * operatingSpeed;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * operatingSpeed;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * operatingSpeed;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * operatingSpeed;
  setWheelSpeeds(motorSpeeds);
}

void AutoBot::driveFRONT_RIGHT() {
  int motorSpeeds[4]=DRIVE_FRONT_RIGHT;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * operatingSpeed;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * operatingSpeed;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * operatingSpeed;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * operatingSpeed;
  setWheelSpeeds(motorSpeeds);
}
void AutoBot::driveFRONT_LEFT() {
  int motorSpeeds[4]=DRIVE_FRONT_LEFT;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * operatingSpeed;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * operatingSpeed;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * operatingSpeed;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * operatingSpeed;
  setWheelSpeeds(motorSpeeds);
}

void AutoBot::driveREAR_RIGHT() {
  int motorSpeeds[4]=DRIVE_REAR_RIGHT;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * operatingSpeed;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * operatingSpeed;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * operatingSpeed;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * operatingSpeed;
  setWheelSpeeds(motorSpeeds);
}

void AutoBot::driveREAR_LEFT() {
  int motorSpeeds[4]=DRIVE_REAR_LEFT;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * operatingSpeed;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * operatingSpeed;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * operatingSpeed;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * operatingSpeed;
  setWheelSpeeds(motorSpeeds);
}

void AutoBot::setOperatingSpeed(int speed) {
  AutoBot::operatingSpeed = speed;
}

void AutoBot::sendToArduino(const char *message) {
  Serial2.write(message);
}

void AutoBot::sendToPython(const char *message) {
  Serial.write(message);
}

void AutoBot::triggerGripper(bool value) {
  if (value) {
    Serial.println("Activate Gripper");
  } else {
    Serial.println("Deactivate Gripper");
  }
}

void AutoBot::StepUp()
{
  digitalWrite(AutoBot::stepdir,LOW);
  for (int i = 0; i < 100 ; i++) {
    digitalWrite(AutoBot::steppulse, HIGH);
    delayMicroseconds(50);
    digitalWrite(AutoBot::steppulse, LOW);
    delayMicroseconds(50);
  }
}

void AutoBot::StepDown() {
  digitalWrite(AutoBot::stepdir, HIGH);
  for (int i = 0; i < 100; i++) {
    digitalWrite(AutoBot::steppulse, HIGH);
    delayMicroseconds(50);
    digitalWrite(AutoBot::steppulse, LOW);
    delayMicroseconds(50);
  }
}

void AutoBot::initServo()
{
  cservo.attach(AutoBot::cServoPin);
  gservo.attach(AutoBot::gServoPin);
  gservo.write(GRIPPER_DEFAULT);
  cservo.write(CAM_DEFAULT);
}

void AutoBot::setMotorSpeedCoefficients(float coeff1, float coeff2, float coeff3, float coeff4) {
  motorSpeedCoefficients[0] = coeff1;
  motorSpeedCoefficients[1] = coeff2;
  motorSpeedCoefficients[2] = coeff3;
  motorSpeedCoefficients[3] = coeff4;
}