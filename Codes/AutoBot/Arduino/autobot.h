#ifndef AUTOBOT_H
#define AUTOBOT_H

#include <Arduino.h>
#include <ESP32Servo.h>

// Define constants for baud rate and operation modes
#define BAUD_RATE 115200
#define LINE_FOLLOW 0
#define BALL_FOLLOW 1
#define BALL_FOLLOW_FINE 2

// Define motor drive configurations
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

// Define camera and gripper modes
#define WATCH_MODE 0
#define FOCUS_MODE 1
#define GRIPPER_INACTIVE 0
#define GRIPPER_ACTIVE 1
#define GRIPPER_DEFAULT 60
#define CAM_DEFAULT 120

class AutoBot {
  public:
    // Constructor and Destructor
    AutoBot(int pwmPin1, int dirPin1, int pwmPin2, int dirPin2, int pwmPin3, int dirPin3, int pwmPin4, int dirPin4, int rx, int tx, int camservo, int grabservo,int stepperPulse, int stepperDir);
    ~AutoBot();

    // Methods for actuating agent
    void setMotorSpeedCoefficients(float coeff1, float coeff2, float coeff3, float coeff4); // Set motor speed coefficients
    void setOperatingSpeed(int speed); // Set operating speed
    void drive(int x, int y); // Drive based on x and y inputs
    void driveFRONT(); // Move forward
    void driveLEFT(); // Turn left
    void driveRIGHT(); // Turn right
    void driveREAR(); // Move backward
    void rotCLK(); // Rotate clockwise
    void rotACLK(); // Rotate anticlockwise
    void driveFRONT_RIGHT(); // Move diagonally front-right
    void driveFRONT_LEFT(); // Move diagonally front-left
    void driveREAR_RIGHT(); // Move diagonally rear-right
    void driveREAR_LEFT(); // Move diagonally rear-left
    void setWheelSpeeds(int motorSpeeds[]); // Set individual wheel speeds
    void triggerGripper(bool value); // Activate or deactivate gripper
    void pick(); // Pick an object
    void drop(); // Drop an object
    void camRotdown(); // Rotate camera down
    void camRotup(); // Rotate camera up
    void stop(); // Stop all movement
    void initServo(); // Initialize servos
    void StepUp(); // Move stepper motor up
    void StepDown(); // Move stepper motor down

    // Getters and setters
    char getState(); // Get current state
    void setState(char val); // Set current state

    // Methods for transmission agent
    void sendToArduino(const char *message); // Send message to Arduino
    void sendToPython(const char *message); // Send message to Python
  
  private:
    // Properties of actuating agent
    char state; // Current state
    int pwmPins[4]; // PWM pins for motors
    int dirPins[4]; // Direction pins for motors
    int stepdir; // Direction pin for stepper motor
    int steppulse; // Pulse pin for stepper motor
    float motorSpeedCoefficients[4]; // Coefficients for motor speeds
    int operatingSpeed; // Operating speed
    int camMode; // Camera mode
    int gripperState; // Gripper state
    int cServoPin; // Pin for camera servo
    int gServoPin; // Pin for gripper servo
    Servo cservo; // Camera servo object
    Servo gservo; // Gripper servo object

    // Properties of transmission agent
    int serialPins[2]; // Serial communication pins (tx, rx)
};

#endif
