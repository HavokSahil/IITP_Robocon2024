#ifndef AUTOBOT_H
#define AUTOBOT_H

#include <Arduino.h>
#include <ESP32Servo.h>

#define BAUD_RATE 115200
#define LINE_FOLLOW 0
#define BALL_FOLLOW 1
#define BALL_FOLLOW_FINE 2

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
#define BOT_FRONT_RIGHT 'e'
#define BOT_FRONT_LEFT 'q'
#define BOT_BACK_RIGHT 'c'
#define BOT_BACK_LEFT 'z'
#define BOT_UPPER_SPEED 'U'
#define BOT_LOWER_SPEED 'L'

#define CAM_ROT_UP 'v'
#define CAM_ROT_DOWN 'b'
#define TRIGGER_GRIPPER_ACT 'g'
#define TRIGGER_GRIPPER_DEACT 'h'
#define STEPPER_UP 'o'
#define STEPPER_DOWN 'p'
#define BOT_IDLE 'x'

#define WATCH_MODE 0
#define FOCUS_MODE 1

#define GRIPPER_INACTIVE 0
#define GRIPPER_ACTIVE 1

#define GRIPPER_DEFAULT 60
#define CAM_DEFAULT 120

class AutoBot {
  public:
  AutoBot(int pwmPin1, int dirPin1, int pwmPin2, int dirPin2, int pwmPin3, int dirPin3, int pwmPin4, int dirPin4, int rx, int tx, int camservo, int grabservo,int stepperPulse, int stepperDir);
  ~AutoBot();

  // methods for actuating agent
  void setMotorSpeedCoefficients(float coeff1, float coeff2, float coeff3, float coeff4);
  void setOperatingSpeed(int speed);
  void drive(int x, int y);
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
  void triggerGripper(bool value);
  void pick();
  void drop();
  void camRotdown();
  void camRotup();
  void stop();
  void initServo();
  void StepUp();
  void StepDown();

  char getState();
  void setState(char val);

  // methods for transmission agent
  void sendToArduino(const char *message);
  void sendToPython(const char *message);
  
  
  private:
    // properties of actuating agent

    char state;

    int pwmPins[4];
    int dirPins[4];
    int stepdir;
    int steppulse;
    float motorSpeedCoefficients[4];
    int operatingSpeed;
    int camMode;
    int gripperState;
    int cServoPin;
    int gServoPin;
    Servo cservo;
    Servo gservo;

    // properties of transmission agent
    int serialPins[2]; // [tx, rx]
};

#endif