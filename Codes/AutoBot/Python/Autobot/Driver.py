import serial
import time
import json 
import re

class Driver:
    def __init__(self):
        self.serialObj = None
        self.clutch = False
        
        self.pastCommand = ""
        self.pastSpeed = 20
        self.data = {'l':999,'r':999}



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
            self.serialObj = serial.Serial(address, baudrate, timeout=0.1)
    
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
        if(self.pastCommand==command):
            return
        
        elif self.serialObj:
            try:
           
                self.serialObj.write(str(command).encode("utf-8"))
                end = time.time()
                self.pastCommand = command

                print("sent char is ", command)
            
            except Exception as e:
                raise Exception("Failed to send command via serial: " + str(e))


    # Control Functions
    def moveForward(self):
        if not self.clutch:
            self.sendCommandToSerial('w')

    
    # Control Functions
    def moveBackwards(self):
        if not self.clutch:
            self.sendCommandToSerial('s')

    def moveBackLeft(self):
        if not self.clutch:
            self.sendCommandToSerial('z')

    
    def moveBackRight(self):
        if not self.clutch:
            self.sendCommandToSerial('c')
    # Control Functions
    def moveLeft(self):
        if not self.clutch:
            self.sendCommandToSerial('a')

    # Control Functions
    def moveRight(self):
        if not self.clutch:
            self.sendCommandToSerial('d')


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

    def clearBuffer(self):
        garbage = self.serialObj.read_all()
    

    #Sends command to get ultrasound values
    def startSonicTransmission(self):
        self.sendCommandToSerial("T")

    #Sends command to stop ultrasound values
    def stopSonicTransmission(self):
        self.sendCommandToSerial("I")

    def startInfraTransmission(self):
        self.sendCommandToSerial("F")
    
    def stopInfraTransmission(self):
        self.sendCommandToSerial("S")

    def readBuffer(self):
        #THe pattern to decipher
        pattern = r'\{"l":\s*([0-9]+),\s*"r":\s*([0-9]+)\s*\}'
        matches = re.findall(pattern, str(self.serialObj.read_all().decode('utf-8')))

        if matches:
            # Get the last match
            last_match = matches[-1]
            l_value = int(last_match[0])
            r_value = int(last_match[1])
            self.data = {'l':l_value,'r':r_value}
        else:
            print("No infrared data found")
            print(self.data)


    #Set rotational speed
    def setRotSpeed(self,value:int):
        if (value!=self.pastSpeed):
            encoded_speed = chr(value)
            self.sendCommandToSerial(encoded_speed)
            self.pastSpeed = value
