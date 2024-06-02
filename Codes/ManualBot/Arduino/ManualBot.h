#ifndef MANUAL_BOT_H
#define MANUAL_BOT_H

#include <Arduino.h>

#define BAUD_RATE 115200
#define TRIGGER_UP 'u'
#define TRIGGER_DOWN 'd'
#define TRIGGER_STOP 'e'
#define TRIGGER_PNEUMATIC 'r'
#define TRIGGER_GRAB_POS 'g'
#define TRIGGER_GRAB_NEG 'l'

class ManualBot {
  public:
  ManualBot(int pwmPin1, int dirPin1, int pwmPin2, int dirPin2, int pwmPin3, int dirPin3, int pwmPin4, int dirPin4, int rx, int tx);
  ~ManualBot();

  // methods for actuating agent
  void setMotorSpeedCoefficients(float coeff1, float coeff2, float coeff3, float coeff4);
  void setOperatingSpeed(int speed);
  void drive(int x, int y);
  void driveFRONT();
  void driveLEFT();
  void driveRIGHT();
  void driveBACK();
  void rotCLK(int factor);
  void rotACLK(int factor);
  void setWheelSpeeds(int motorSpeeds[]);

  // methods for transmission agent
  void sendToArduino(const char *message);
  void triggerShooting();
  void triggerPICK(bool);
  void triggerGRAB(bool);
  void triggerStop();
  
  private:
    // properties of actuating agent
    int pwmPins[4];
    int dirPins[4];
    float motorSpeedCoefficients[4];
    int operatingSpeed;

    // properties of transmission agent
    int serialPins[2]; // [tx, rx]
};

#endif
