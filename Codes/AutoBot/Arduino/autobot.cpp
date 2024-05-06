#include "esp32-hal.h"
#include "esp32-hal-gpio.h"
#include <math.h>
#include "autobot.h"
#include <cmath>
#include <ESP32Servo.h>

// Constructor: Initializes AutoBot object
AutoBot::AutoBot(int pwmPin1, int dirPin1, int pwmPin2, int dirPin2, int pwmPin3, int dirPin3, int pwmPin4, int dirPin4, int rx, int tx, int camservo_pin, int gservo_pin, int stepperPulse, int stepperDir) {
  // Assign pin values to respective variables
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

  // Set initial state
  state = BOT_IDLE;

  // Initialize motor speed coefficients to 1.0 (no modification)
  for (int i = 0; i < 4; ++i) motorSpeedCoefficients[i] = 1.0;
  
  // Setup PWM and direction pins for motors
  for (int i = 0; i < 4; ++i) {
    pinMode(pwmPins[i], OUTPUT);
    pinMode(dirPins[i], OUTPUT);
  }

  // Setup pins for stepper motor
  pinMode(steppulse, OUTPUT);
  pinMode(stepdir, OUTPUT);

  // Initialize serial communication
  Serial2.begin(BAUD_RATE, SERIAL_8N1, rx, tx);

  // Set default operating speed
  operatingSpeed = 40;

  // Set default camera mode and gripper state
  camMode = WATCH_MODE;
  gripperState = GRIPPER_INACTIVE;
}

// Destructor: Cleans up resources
AutoBot::~AutoBot() {
  // Destructor
}

// Set the state of the AutoBot
void AutoBot::setState(char val) {
  state = val;
}

// Get the current state of the AutoBot
char AutoBot::getState() {
  return state;
}

// Set individual wheel speeds
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

// Pick an object with the gripper
void AutoBot::pick() {
  if (gripperState == GRIPPER_INACTIVE) {
    for (int i = 60; i >= 20; i--) {
      gservo.write(i);
      delay(20);
    }
    gripperState = GRIPPER_ACTIVE;
  }
}

// Drop an object held by the gripper
void AutoBot::drop() {
  if (gripperState == GRIPPER_ACTIVE) {
    for (int i = 20; i <= 60; i++) {
      gservo.write(i);
      delay(20);
    }
    gripperState = GRIPPER_INACTIVE;
  }
}

// Rotate the camera downwards
void AutoBot::camRotdown() {
  while (camMode == WATCH_MODE) {
    for (int i = 120; i >= 45; i--) {
      cservo.write(i);
    }
    camMode = FOCUS_MODE;
  }
}

// Rotate the camera upwards
void AutoBot::camRotup() {
  while (camMode == FOCUS_MODE) {
    for (int i = 45; i <= 120; i++) {
      cservo.write(i);
    }
    camMode = WATCH_MODE;
  }
}

// Rotate the AutoBot clockwise
void AutoBot::rotCLK() {
  int motorSpeeds[4] = ROTATE_CLOCK;
  for (int i = 0; i < 4; ++i) {
    motorSpeeds[i] *= motorSpeedCoefficients[i] * operatingSpeed;
  }
  setWheelSpeeds(motorSpeeds);
}

// Rotate the AutoBot anticlockwise
void AutoBot::rotACLK() {
  int motorSpeeds[4] = ROTATE_ANTICLOCK;
  for (int i = 0; i < 4; ++i) {
    motorSpeeds[i] *= motorSpeedCoefficients[i] * operatingSpeed;
  }
  setWheelSpeeds(motorSpeeds);
}

// Stop all movement of the AutoBot
void AutoBot::stop() {
  int motorSpeeds[4] = STOP;
  setWheelSpeeds(motorSpeeds);
}

// Drive the AutoBot forwards
void AutoBot::driveFRONT() {
  int motorSpeeds[4] = DRIVE_FRONT;
  for (int i = 0; i < 4; ++i) {
    motorSpeeds[i] *= motorSpeedCoefficients[i] * operatingSpeed;
  }
  setWheelSpeeds(motorSpeeds);
}

// Drive the AutoBot to the left
void AutoBot::driveLEFT() {
  int motorSpeeds[4] = DRIVE_LEFT;
  for (int i = 0; i < 4; ++i) {
    motorSpeeds[i] *= motorSpeedCoefficients[i] * operatingSpeed;
  }
  setWheelSpeeds(motorSpeeds);
}

// Drive the AutoBot to the right
void AutoBot::driveRIGHT() {
  int motorSpeeds[4] = DRIVE_RIGHT;
  for (int i = 0; i < 4; ++i) {
    motorSpeeds[i] *= motorSpeedCoefficients[i] * operatingSpeed;
  }
  setWheelSpeeds(motorSpeeds);
}

// Drive the AutoBot backwards
void AutoBot::driveREAR() {
  int motorSpeeds[4] = DRIVE_REAR;
  for (int i = 0; i < 4; ++i) {
    motorSpeeds[i] *= motorSpeedCoefficients[i] * operatingSpeed;
  }
  setWheelSpeeds(motorSpeeds);
}

// Drive the AutoBot diagonally front-right
void AutoBot::driveFRONT_RIGHT() {
  int motorSpeeds[4] = DRIVE_FRONT_RIGHT;
  for (int i = 0; i < 4; ++i) {
    motorSpeeds[i] *= motorSpeedCoefficients[i] * operatingSpeed;
  }
  setWheelSpeeds(motorSpeeds);
}

// Drive the AutoBot diagonally front-left
void AutoBot::driveFRONT_LEFT() {
  int motorSpeeds[4] = DRIVE_FRONT_LEFT;
  for (int i = 0; i < 4; ++i) {
    motorSpeeds[i] *= motorSpeedCoefficients[i] * operatingSpeed;
  }
  setWheelSpeeds(motorSpeeds);
}

// Drive the AutoBot diagonally rear-right
void AutoBot::driveREAR_RIGHT() {
  int motorSpeeds[4] = DRIVE_REAR_RIGHT;
  for (int i = 0; i < 4; ++i) {
    motorSpeeds[i] *= motorSpeedCoefficients[i] * operatingSpeed;
  }
  setWheelSpeeds(motorSpeeds);
}

// Drive the AutoBot diagonally rear-left
void AutoBot::driveREAR_LEFT() {
  int motorSpeeds[4] = DRIVE_REAR_LEFT;
  for (int i = 0; i < 4; ++i) {
    motorSpeeds[i] *= motorSpeedCoefficients[i] * operatingSpeed;
  }
  setWheelSpeeds(motorSpeeds);
}

// Set the operating speed of the AutoBot
void AutoBot::setOperatingSpeed(int speed) {
  operatingSpeed = speed;
}

// Send message to Arduino
void AutoBot::sendToArduino(const char *message) {
  Serial2.write(message);
}

// Send message to Python
void AutoBot::sendToPython(const char *message) {
  Serial.write(message);
}

// Activate or deactivate the gripper
void AutoBot::triggerGripper(bool value) {
  if (value) {
    Serial.println("Activate Gripper");
  } else {
    Serial.println("Deactivate Gripper");
  }
}

// Move the stepper motor up
void AutoBot::StepUp() {
  digitalWrite(stepdir, LOW);
  for (int i = 0; i < 100; i++) {
    digitalWrite(steppulse, HIGH);
    delayMicroseconds(50);
    digitalWrite(steppulse, LOW);
    delayMicroseconds(50);
  }
}

// Move the stepper motor down
void AutoBot::StepDown() {
  digitalWrite(stepdir, HIGH);
  for (int i = 0; i < 100; i++) {
    digitalWrite(steppulse, HIGH);
    delayMicroseconds(50);
    digitalWrite(steppulse, LOW);
    delayMicroseconds(50);
  }
}

// Initialize servos
void AutoBot::initServo() {
  cservo.attach(cServoPin);
  gservo.attach(gServoPin);
  gservo.write(GRIPPER_DEFAULT);
  cservo.write(CAM_DEFAULT);
}

// Set motor speed coefficients
void AutoBot::setMotorSpeedCoefficients(float coeff1, float coeff2, float coeff3, float coeff4) {
  motorSpeedCoefficients[0] = coeff1;
  motorSpeedCoefficients[1] = coeff2;
  motorSpeedCoefficients[2] = coeff3;
  motorSpeedCoefficients[3] = coeff4;
}
