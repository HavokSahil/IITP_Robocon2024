#include "Arduino.h"
#include "HardwareSerial.h"
#include "Servo.h"
#include <avr/interrupt.h>
#include "autobot.h"
#include <math.h>

AutoBot::AutoBot(
    int pwmPin1,
    int dirPin1,
    int pwmPin2,
    int dirPin2,
    int pwmPin3,
    int dirPin3,
    int pwmPin4,
    int dirPin4)
{

  pwmPins[0] = pwmPin1;
  dirPins[0] = dirPin1;
  pwmPins[1] = pwmPin2;
  dirPins[1] = dirPin2;
  pwmPins[2] = pwmPin3;
  dirPins[2] = dirPin3;
  pwmPins[3] = pwmPin4;
  dirPins[3] = dirPin4;

  this->driveState = BOT_IDLE;
  this->periState = PERI_IDLE;
  this->broadcast = false;

  // Initialise motor speed coefficients to 1.0 (no modification)
  for (int i = 0; i < 4; ++i)
    motorSpeedCoefficients[i] = 1.0;

  // setup pwm and dir pins
  for (int i = 0; i < 4; ++i)
  {
    pinMode(pwmPins[i], OUTPUT);
    pinMode(dirPins[i], OUTPUT);
  }

  this->ROTATING_SPEED = 30;
  this->OPERATING_SPEED = 40;
  this->GRIPPER_STATE = GRIPPER_CLOSE;
  this->CAMERA_STATE = CAMERA_POS_DOWN;
  this->LIFTER_STATE = LIFTER_ACTIVE;
  this->RANGE_STATE = OUT_RANGE_BALL;
}

AutoBot::~AutoBot()
{
  // Destructor
}

void AutoBot::setPeriState(char val)
{
  this->periState = val;
}

void AutoBot::setDriveState(char val)
{
  this->driveState = val;
}

char AutoBot::getDriveState()
{
  return this->driveState;
}

char AutoBot::getPeriState()
{
  return this->periState;
}

void AutoBot::setWheelSpeeds(int motorSpeeds[])
{
  Serial.print("[");
  for (int i = 0; i < 4; ++i)
  {
    // Ensure motor speeds are within valid range (-255 to 255)
    motorSpeeds[i] = constrain(motorSpeeds[i], -255, 255);

    // Set direction based on the sign of motor speed
    digitalWrite(dirPins[i], (motorSpeeds[i] >= 0) ? HIGH : LOW);

    // Set PWM signal
    analogWrite(pwmPins[i], abs(motorSpeeds[i]));

    // Print PWM values
    Serial.print(motorSpeeds[i]);
    if (i < 3)
    {
      Serial.print(", ");
    }
  }
  Serial.println("]");
}

// =============== Additional Servo Functions

void AutoBot::rotCLK()
{
  int motorSpeeds[4] = ROTATE_CLOCK;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * this->ROTATING_SPEED;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * this->ROTATING_SPEED;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * this->ROTATING_SPEED;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * this->ROTATING_SPEED;
  this->setWheelSpeeds(motorSpeeds);
}

void AutoBot::rotACLK()
{
  int motorSpeeds[4] = ROTATE_ANTICLOCK;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * this->ROTATING_SPEED;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * this->ROTATING_SPEED;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * this->ROTATING_SPEED;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * this->ROTATING_SPEED;
  this->setWheelSpeeds(motorSpeeds);
}

void AutoBot::stop()
{
  int motorSpeeds[4] = STOP;
  this->setWheelSpeeds(motorSpeeds);
}

void AutoBot::driveFRONT()
{
  int motorSpeeds[4] = DRIVE_FRONT;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * this->OPERATING_SPEED;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * this->OPERATING_SPEED;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * this->OPERATING_SPEED;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * this->OPERATING_SPEED;
  this->setWheelSpeeds(motorSpeeds);
}

void AutoBot::driveLEFT()
{
  int motorSpeeds[4] = DRIVE_LEFT;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * this->OPERATING_SPEED * 1.4;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * this->OPERATING_SPEED * 1.4;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * this->OPERATING_SPEED * 1.4;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * this->OPERATING_SPEED * 1.4;
  this->setWheelSpeeds(motorSpeeds);
}

void AutoBot::driveRIGHT()
{
  int motorSpeeds[4] = DRIVE_RIGHT;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * this->OPERATING_SPEED * 1.4;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * this->OPERATING_SPEED * 1.4;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * this->OPERATING_SPEED * 1.4;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * this->OPERATING_SPEED * 1.4;
  this->setWheelSpeeds(motorSpeeds);
}

void AutoBot::driveREAR()
{
  int motorSpeeds[4] = DRIVE_REAR;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * this->OPERATING_SPEED;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * this->OPERATING_SPEED;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * this->OPERATING_SPEED;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * this->OPERATING_SPEED;
  this->setWheelSpeeds(motorSpeeds);
}

void AutoBot::driveFRONT_RIGHT()
{
  int motorSpeeds[4] = DRIVE_FRONT_RIGHT;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * this->OPERATING_SPEED;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * this->OPERATING_SPEED;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * this->OPERATING_SPEED;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * this->OPERATING_SPEED;
  this->setWheelSpeeds(motorSpeeds);
}
void AutoBot::driveFRONT_LEFT()
{
  int motorSpeeds[4] = DRIVE_FRONT_LEFT;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * this->OPERATING_SPEED;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * this->OPERATING_SPEED;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * this->OPERATING_SPEED;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * this->OPERATING_SPEED;
  this->setWheelSpeeds(motorSpeeds);
}

void AutoBot::driveREAR_RIGHT()
{
  int motorSpeeds[4] = DRIVE_REAR_RIGHT;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * this->OPERATING_SPEED;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * this->OPERATING_SPEED;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * this->OPERATING_SPEED;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * this->OPERATING_SPEED;
  this->setWheelSpeeds(motorSpeeds);
}

void AutoBot::driveREAR_LEFT()
{
  int motorSpeeds[4] = DRIVE_REAR_LEFT;
  motorSpeeds[0] *= motorSpeedCoefficients[0] * this->OPERATING_SPEED;
  motorSpeeds[1] *= motorSpeedCoefficients[1] * this->OPERATING_SPEED;
  motorSpeeds[2] *= motorSpeedCoefficients[2] * this->OPERATING_SPEED;
  motorSpeeds[3] *= motorSpeedCoefficients[3] * this->OPERATING_SPEED;
  this->setWheelSpeeds(motorSpeeds);
}

void AutoBot::setOperatingSpeed(int speed)
{
  this->OPERATING_SPEED = speed;
}

void AutoBot::setRotatingSpeed(int speed)
{
  this->ROTATING_SPEED = speed;
}

void AutoBot::triggerGripperWrapper(bool value, Servo gripServo, double BUFFER[])
{
  if (value == GRIPPER_CLOSE)
  {
    if (this->getFinalDistance(BUFFER, PIN_SONIC_TRIG, PIN_SONIC_ECHO, FLAG_SONIC_GRIP) < 15)
      this->triggerGripper(GRIPPER_CLOSE, gripServo);
  }
  else
  {
    this->triggerGripper(GRIPPER_OPEN, gripServo);
  }
}

void AutoBot::triggerGripper(bool value, Servo gripServo)
{

  if (value == GRIPPER_CLOSE)
  {

    if (GRIPPER_STATE == GRIPPER_CLOSE)
    {
      return;
    }

    for (int i = OPEN_ANGLE; i >= CLOSE_ANGLE; i--)
    {
      gripServo.write(i);
      Serial.println(i);
      delay(25);
      Serial.println("Closing Gripper");
    }
    GRIPPER_STATE = GRIPPER_CLOSE;
  }
  else
  {

    if (GRIPPER_STATE == GRIPPER_OPEN)
    {
      return;
    }

    for (int i = CLOSE_ANGLE; i <= OPEN_ANGLE; i++)
    {
      gripServo.write(i);
      Serial.println(i);
      delay(25);
      Serial.println("Opening Gripper");
    }
    GRIPPER_STATE = GRIPPER_OPEN;
  }
}

void AutoBot::getLateralSonicReading(double LEFT_SONIC_BUFFER[], double RIGHT_SONIC_BUFFER[])
{
  double dist[2];
  dist[0] = getFinalDistance(LEFT_SONIC_BUFFER, PIN_SONIC_LEFT_TRIG, PIN_SONIC_LEFT_ECHO, FLAG_SONIC_LEFT);
  dist[1] = getUltraDist(PIN_SONIC_RIGHT_TRIG, PIN_SONIC_RIGHT_ECHO);

  Serial.print("{\"l\": ");
  Serial.print(dist[0]);
  Serial.print(", \"r\": ");
  Serial.print(dist[1]);
  Serial.println(" }");
}

void AutoBot::gripperUp()
{
  digitalWrite(PIN_DIR_LIFTER, LOW); // for upward direction
  while ((digitalRead(PIN_TACTILE_UP) != HIGH) && (LIFTER_STATE == LIFTER_ACTIVE))
  {
    analogWrite(PIN_PWM_LIFTER, LIFTER_SPEED);
    Serial.println("Going Up");
  }
  analogWrite(PIN_PWM_LIFTER, 0);
}

void AutoBot::gripperDown()
{
  digitalWrite(PIN_DIR_LIFTER, HIGH); // for downward direction
  while ((digitalRead(PIN_TACTILE_DOWN) != HIGH) && (LIFTER_STATE == LIFTER_ACTIVE))
  {
    analogWrite(PIN_PWM_LIFTER, LIFTER_SPEED);
    Serial.println("Going Down");
  }
  analogWrite(PIN_PWM_LIFTER, 0);
}

void AutoBot::triggerCamera(bool value, Servo camServo)
{
  Serial.print("Oh no");
  if (value == CAMERA_POS_DOWN)
  {
    if (CAMERA_STATE == CAMERA_POS_DOWN)
      return;
    for (int i = CAMERA_DOWN_ANGLE; i <= CAMERA_UP_ANGLE; i++)
    {
      camServo.write(i);
      delay(15);
    }
    CAMERA_STATE = CAMERA_POS_DOWN;
  }
  else
  {
    if (CAMERA_STATE == CAMERA_POS_UP)
      return;
    for (int i = CAMERA_UP_ANGLE; i >= CAMERA_DOWN_ANGLE; i--)
    {
      camServo.write(i);
      delay(15);
    }
    CAMERA_STATE = CAMERA_POS_UP;
  }
}

double AutoBot::getFinalDistance(double BUFFER[], int PIN_TRIG, int PIN_ECHO, int FLAG)
{

  static int g = 0; // Counter for Gripper Sonic Sensor
  static int l = 0; // Counter for Left Sonic Sensor
  static int r = 0; // Counter for Right Sonic Sensor

  double latest_dist = getUltraDist(PIN_TRIG, PIN_ECHO);

  if (FLAG == FLAG_SONIC_GRIP)
  {
    if (g > SONIC_BUFF_SIZE)
      g = 0;
    BUFFER[g++] = latest_dist;
    return powAvg(BUFFER);
  }
  else if (FLAG == FLAG_SONIC_LEFT)
  {
    if (l > SONIC_BUFF_SIZE)
      l = 0;
    BUFFER[l++] = latest_dist;
    return powAvg(BUFFER);
  }
  else if (FLAG == FLAG_SONIC_RIGHT)
  {
    if (r > SONIC_BUFF_SIZE)
      r = 0;
    BUFFER[r++] = latest_dist;
    return powAvg(BUFFER);
  }
}

double AutoBot::getUltraDist(int PIN_TRIG, int PIN_ECHO)
{

  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(5);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  double duration = pulseIn(PIN_ECHO, HIGH);
  double dist_cm = (duration / 2) / 29.1;

  return dist_cm;
}

double AutoBot::powAvg(double BUFFER[])
{
  double x = 0.2;
  double ret = 0;
  for (int i = 0; i < SONIC_BUFF_SIZE; i++)
  {
    ret += pow(BUFFER[i], x);
  }
  ret = ret / (double)SONIC_BUFF_SIZE;
  ret = pow(ret, 1.0 / x);
  return ret;
}

void AutoBot::getLateralProximityReading()
{

  int l = !digitalRead(PIN_PROXIMITY_LEFT);
  int r = !digitalRead(PIN_PROXIMITY_RIGHT);

  Serial.print("{\"l\": ");
  Serial.print(l);
  Serial.print(", \"r\": ");
  Serial.print(r);
  Serial.println(" }");
}

bool AutoBot::getBroadcast()
{
  return this->broadcast;
}

void AutoBot::setBroadcast(bool value)
{
  this->broadcast = value;
}

void AutoBot::setMotorSpeedCoefficients(float coeff1, float coeff2, float coeff3, float coeff4)
{
  this->motorSpeedCoefficients[0] = coeff1;
  this->motorSpeedCoefficients[1] = coeff2;
  this->motorSpeedCoefficients[2] = coeff3;
  this->motorSpeedCoefficients[3] = coeff4;
}
