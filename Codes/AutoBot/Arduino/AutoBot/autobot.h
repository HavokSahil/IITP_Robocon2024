#ifndef AUTOBOT_H
#define AUTOBOT_H

#include <Arduino.h>
#include <Servo.h>

#define BAUD_RATE 9600

// Kinematic Macros
#define DRIVE_FRONT {1, 1, 1, 1}
#define DRIVE_REAR {-1, -1, -1, -1}
#define DRIVE_LEFT {-1, 1, -1, 1}
#define DRIVE_RIGHT {1, -1, 1, -1}
#define DRIVE_FRONT_RIGHT {1, 0, 1, 0}
#define DRIVE_FRONT_LEFT {0, 1, 0, 1}
#define DRIVE_REAR_RIGHT {-1, 0, -1, 0}
#define DRIVE_REAR_LEFT {0, -1, 0, -1}
#define ROTATE_CLOCK {1, -1, -1, 1}
#define ROTATE_ANTICLOCK {-1, 1, 1, -1}
#define STOP {0, 0, 0, 0}

// Command Macros
#define BOT_ROT_CLOCK 'l'
#define BOT_ROT_ACLOCK 'k'
#define BOT_FORWARD 'w'
#define BOT_BACKWARD 's'
#define BOT_LEFT 'a'
#define BOT_RIGHT 'd'
#define BOT_FRONT_RIGHT 'e'
#define BOT_FRONT_LEFT 'q'
#define BOT_BACK_RIGHT 'c'
#define BOT_BACK_LEFT 'z'
#define BOT_IDLE 'x'

#define TRIGGER_LIFTER_UP 'U'
#define TRIGGER_LIFTER_DOWN 'P'
#define TRIGGER_GRIPPER_CLOSE 'C'
#define TRIGGER_GRIPPER_OPEN 'O'
#define TRIGGER_LIFTER_CEISE 'Z'
#define TRIGGER_CAMERA_UP 'V'
#define TRIGGER_CAMERA_DOWN 'B'
#define TRIGGER_LATERAL_SONIC_TRANSMISSION 'T'
#define TRIGGER_LATERAL_PROXIMITY_TRANS 'F'
#define PERI_IDLE 'I'

#define IN_RANGE_BALL true
#define OUT_RANGE_BALL false

#define LIFTER_INACTIVE false
#define LIFTER_ACTIVE true

#define GRIPPER_OPEN false
#define GRIPPER_CLOSE true

#define CAMERA_POS_UP false
#define CAMERA_POS_DOWN true

// Macros for Positions
#define CLOSE_ANGLE 10
#define OPEN_ANGLE 70
#define SONIC_BUFF_SIZE 10
#define LIFTER_SPEED 200
#define CAMERA_UP_ANGLE 150
#define CAMERA_DOWN_ANGLE 120

// Pins for Peripherals
#define PIN_SONIC_TRIG 48 // 11
#define PIN_SONIC_ECHO 50 // 12

#define PIN_PWM_LIFTER 33
#define PIN_DIR_LIFTER 22
#define PIN_TACTILE_UP 46    // 8
#define PIN_TACTILE_DOWN 26  // 7
#define PIN_SERVO_GRIPPER 12 // 5
#define PIN_SERVO_CAMERA 11  // 3

#define PIN_SONIC_LEFT_TRIG 43
#define PIN_SONIC_RIGHT_TRIG 44

#define PIN_SONIC_LEFT_ECHO 41
#define PIN_SONIC_RIGHT_ECHO 42

#define PIN_PROXIMITY_LEFT 41
#define PIN_PROXIMITY_RIGHT 42

#define FLAG_SONIC_GRIP 0
#define FLAG_SONIC_LEFT 1
#define FLAG_SONIC_RIGHT 2

class AutoBot
{
public:
  // Variables for State Management of the Bot
  double SONIC_BUFFER[SONIC_BUFF_SIZE];
  int OPERATING_SPEED;
  int GRIPPER_STATE;
  int CAMERA_STATE;
  int LIFTER_STATE;
  int RANGE_STATE;
  int ROTATING_SPEED;

  AutoBot(
      int pwmPin1,
      int dirPin1,
      int pwmPin2,
      int dirPin2,
      int pwmPin3,
      int dirPin3,
      int pwmPin4,
      int dirPin4);
  ~AutoBot();

  // Function to Change the Speed Multiplier of the Bot
  void setMotorSpeedCoefficients(float coeff1, float coeff2, float coeff3, float coeff4);

  void setOperatingSpeed(int speed);
  void setRotatingSpeed(int speed);

  void drive(int x, int y);
  void stop();

  void driveFRONT();
  void driveLEFT();
  void driveRIGHT();
  void driveREAR();

  void rotCLK();
  void rotACLK();

  void driveFRONT_RIGHT();
  void driveFRONT_LEFT();
  void driveREAR_RIGHT();
  void driveREAR_LEFT();

  void setWheelSpeeds(int motorSpeeds[]);

  // Function for Bot Peripherals
  void triggerGripperWrapper(bool value, Servo gripServo, double BUFFER[]);
  void triggerGripper(bool value, Servo gripServo);
  void triggerCamera(bool value, Servo camServo);

  void gripperUp();
  void gripperDown();

  void cameraUp();
  void cameraDown();

  void getLateralProximityReading();

  void setBroadcast(bool);
  bool getBroadcast();

  // Functions for UltraSonic Distance Sensors
  void getLateralSonicReading(double LEFT_SONIC_BUFFER[], double RIGHT_SONIC_BUFFER[]);
  double getFinalDistance(double BUFFER[], int PIN_TRIG, int PIN_ECHO, int FLAG);
  double getUltraDist(int PIN_TRIG, int PIN_ECHO);
  double powAvg(double BUFFER[]);

  char getPeriState();
  char getDriveState();
  void setPeriState(char val);
  void setDriveState(char val);

private:
  char driveState;
  char periState;
  bool broadcast;

  int pwmPins[4];
  int dirPins[4];

  float motorSpeedCoefficients[4];
};

#endif