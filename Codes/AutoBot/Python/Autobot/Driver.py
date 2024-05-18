import serial

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
                self.serialObj.write(str(command).encode("utf-8"))
            except Exception as e:
                raise Exception("Failed to send command via serial: " + str(e))


    # Control Functions
    def moveForward(self):
        if not self.clutch:
            self.sendCommandToSerial('w')

    def rotClock(self):
        if not self.clutch:
            self.sendCommandToSerial('d')

    def rotAClock(self):
        if not self.clutch:
            self.sendCommandToSerial('a')

    def cameraUp(self):
        self.sendCommandToSerial('s')

    def cameraDown(self):
        self.sendCommandToSerial('b')

    def triggerGripper(self):
        self.sendCommandToSerial('g')

    def triggerRelease(self):
        self.sendCommandToSerial('h')

    def stop(self):
        self.sendCommandToSerial('x')

    def lowerSpeed(self):
        self.sendCommandToSerial('l')

    def upperSpeed(self):
        self.sendCommandToSerial('u')

    def setClutch(self, value):
        self.clutch = value