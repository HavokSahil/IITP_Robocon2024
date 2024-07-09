#include <math.h>
#include "ManualBot.h"
#include <cmath>

ManualBot::ManualBot(int pwmPin1, int dirPin1, int pwmPin2, int dirPin2, int pwmPin3, int dirPin3, int pwmPin4, int dirPin4, int rx, int tx) {
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

  // Initialise motor speed coefficients to 1.0 (no modification)
  for (int i = 0; i < 4; ++i) motorSpeedCoefficients[i] = 1.0;
  
  // setup pwm and dir pins
  for (int i = 0; i < 4; ++i) {
    pinMode(pwmPins[i], OUTPUT);
    pinMode(dirPins[i], OUTPUT);
  }

  // setting up rx and tx pins
  Serial2.begin(BAUD_RATE, SERIAL_8N1, rx, tx);

  // set default operating speed to max speed
  operatingSpeed = 255;
}

ManualBot::~ManualBot() {
  //Destructor
}

void ManualBot::drive(int x, int y) {
  float radius = sqrt(pow(x, 2) + pow(y, 2));
  float mRadius = sqrt(pow(100.0, 2) + pow(100.0, 2));
  float angle = atan2(y, x);
  float speed = std::min((radius/mRadius)*operatingSpeed, (float)255);

  int motorSpeeds[4];
  motorSpeeds[0] = motorSpeedCoefficients[0] * (speed * -sin(angle)); // Front-left
  motorSpeeds[1] = motorSpeedCoefficients[1] * (speed * -cos(angle)); // Front-right
  motorSpeeds[2] = motorSpeedCoefficients[2] * (speed * sin(angle)); // Rear-left
  motorSpeeds[3] = motorSpeedCoefficients[3] * (speed * cos(angle)); // Rear-right
  ManualBot::setWheelSpeeds(motorSpeeds);
}

void ManualBot::rotate(int factor) {
  float fac = (float)factor/100.0;
  float speed = std::min(operatingSpeed * fac, (float)255);

  int motorSpeeds[4];
  motorSpeeds[0] = motorSpeedCoefficients[0]*speed*0;
  motorSpeeds[1] = motorSpeedCoefficients[1]*speed;
  motorSpeeds[2] = motorSpeedCoefficients[2]*speed*0;
  motorSpeeds[3] = motorSpeedCoefficients[3]*speed;
  ManualBot::setWheelSpeeds(motorSpeeds);
}

void ManualBot::setWheelSpeeds(int motorSpeeds[]) {
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

void ManualBot::driveFRONT() {
  drive(0, 20);
}

void ManualBot::driveLEFT() {
  drive(-20, 0);
}

void ManualBot::driveRIGHT() {
  drive(20, 0);
}

void ManualBot::driveBACK() {
  drive(0, -20);
}

void ManualBot::rotClock() {
  this->rotate(20);
}

void ManualBot::rotAClock() {
  this->rotate(-20);
}

void ManualBot::setState(char state) {
  this->state = state;
}

char ManualBot::getState() {
  return this->state;
}

void ManualBot::setOperatingSpeed(int speed) {
  operatingSpeed = speed;
}

void ManualBot::triggerShooting() {
  Serial2.write(TRIGGER_PNEUMATIC);
}

void ManualBot::triggerPickLeft(bool value) {
  if (value) {
    Serial2.write(TRIGGER_GRAB_LEFT_POS);
  } else {
    Serial2.write(TRIGGER_GRAB_LEFT_NEG);
  }
}

void ManualBot::triggerPickRight(bool value) {
  if (value) {
    Serial2.write(TRIGGER_GRAB_RIGHT_POS);
  } else {
    Serial2.write(TRIGGER_GRAB_RIGHT_NEG);
  }
}
void ManualBot::triggerGrab(bool value) {
  if (value) {
    Serial2.write(TRIGGER_BALL_GRAB_POS);
  } else {
    Serial2.write(TRIGGER_BALL_GRAB_NEG);
  }
}

void ManualBot::triggerLifter(bool value) {
  if (value) {
    Serial2.write(TRIGGER_UP);
  } else {
    Serial2.write(TRIGGER_DOWN);
  }
}

void ManualBot::triggerStop() {
  Serial2.write(TRIGGER_STOP);
}

void ManualBot::sendToArduino(const char *message) {
  Serial2.write(message);
}

void ManualBot::setMotorSpeedCoefficients(float coeff1, float coeff2, float coeff3, float coeff4) {
  this->motorSpeedCoefficients[0] = coeff1;
  this->motorSpeedCoefficients[1] = coeff2;
  this->motorSpeedCoefficients[2] = coeff3;
  this->motorSpeedCoefficients[3] = coeff4;
}