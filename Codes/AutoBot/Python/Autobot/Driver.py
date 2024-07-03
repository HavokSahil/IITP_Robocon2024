import serial
import time

class Driver:
    def __init__(self):
        self.serialObj = None
        self.clutch = False


    def initialiseSerial(self, address, baudrate):
        """
        Initializes serial communication.

        Args:
            address (str): Serial port address.
            baudrate (int): Baud rate.

        Raises:
            Exception: If serial communication fails to initialize.
        """
        try:
            self.serialObj = serial.Serial(address, baudrate)
    
        except Exception as e:
            raise Exception("Failed to initialize serial communication: " + str(e))
    
    
    def sendCommandToSerial(self, command):
        """
        Sends a command via serial communication.

        Args:
            command (str): Command to send.

        Raises:
            Exception: If serial communication fails.
        """
        if self.serialObj:
            try:
                start = time.time()
                self.serialObj.write(str(command).encode("utf-8"))
                end = time.time()
                print("The Time is: ",end-start, command)
            except Exception as e:
                raise Exception("Failed to send command via serial: " + str(e))


    # Control Functions
    def moveForward(self):
        if not self.clutch:
            self.sendCommandToSerial('w')

    def rotClock(self):
        if not self.clutch:
            self.sendCommandToSerial('l')

    def rotAClock(self):
        if not self.clutch:
            self.sendCommandToSerial('k')

    def cameraUp(self):
        self.sendCommandToSerial('v')

    def cameraDown(self):
        self.sendCommandToSerial('b')

    def gripperUp(self):
        self.sendCommandToSerial('U')
    
    def gripperDown(self):
        self.sendCommandToSerial('P')

    def triggerGripper(self):
        self.sendCommandToSerial('C')
        

    def triggerRelease(self):
        self.sendCommandToSerial('O')

    def stop(self):
        self.sendCommandToSerial('x')

    def lowerSpeed(self):
        self.sendCommandToSerial('L')

    def upperSpeed(self):
        self.sendCommandToSerial('U')

    def setClutch(self, value):
        self.clutch = value

    #Set rotational speed
    def setRotSpeed(self,value):
        message = "<0{}>".format(value)
        self.sendCommandToSerial(message)
