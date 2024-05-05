from ultralytics import YOLO
import serial
import math
import cv2

class BallDetector:
    def __init__(self, filename, imgsz=640, conf=0.45, iou=0.45, xCenter=320, yCenter=480):
        self._model = self._loadModel(filename)
        self._imgsz = imgsz
        self._conf = conf
        self._iou = iou
        self.xCenter = xCenter
        self.yCenter = yCenter
        self.lastPos = None
        self.serialObj = None
        self.clutch = False

    def getPrediction(self, frame):
        """
        Predicts the position of the ball in the given frame.

        Returns:
            Tuple: (count, [x, y], frame[annotated])
        """
        result = self._model.predict(frame, imgsz=self._imgsz, conf=self._conf, iou=self._iou)[0]
        count = len(result)
        if count == 0:
            return 0, None, None
        else:
            i = 0
            box = result.boxes[i]
            tensor = box.xyxy[0]
            x1, y1, x2, y2 = int(tensor[0].item()), int(tensor[1].item()), int(tensor[2].item()), int(tensor[3].item())
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
            center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
            self.lastPos = [center_x, center_y]
            return count, [center_x, center_y], frame

    def classifyMissingBall(self):
        """
        Classifies the missing ball condition.

        Returns:
            str: Missing class (MISSING_RIGHT, MISSING_LEFT, MISSING_BELOW, MISSING_UNKNOWN)
        """
        missingClass = "MISSING_UNKNOWN"
        if self.lastPos:
            if self.lastPos[0] in range(160, 480):
                if self.lastPos[1] in range(240, 480):
                    missingClass = "MISSING_BELOW"
            elif self.lastPos[0] <= 160:
                missingClass = "MISSING_LEFT"
            elif self.lastPos[0] >= 480:
                missingClass = "MISSING_RIGHT"
        return missingClass

    def classifyBallPresence(self, x, y):
        """
        Classifies the position of the ball based on its coordinates.

        Args:
            x (int): X-coordinate of the ball.
            y (int): Y-coordinate of the ball.

        Returns:
            str: State of the ball (CENTRE, RIGHT, LEFT).
        """

        # Check if the point lies inside the trapezium
        f1 = 7*y-24*x+2880
        f2 = 7*y+24*x-12480

        if (f1<0 and f2<0):
            return "CENTRE"
        elif (f1<0 and f2>0):
            return "RIGHT"
        else:
            return "LEFT"

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

    def eraseMemory(self):
        self.lastPos = None

    def setClutch(self, value):
        self.clutch = value

    @staticmethod
    def cartesian_to_polar(delx, dely):
        """
        Converts cartesian coordinates to polar coordinates.

        Args:
            delx (float): Change in x-coordinate.
            dely (float): Change in y-coordinate.

        Returns:
            Tuple: (radius, theta_degrees)
        """
        radius = math.sqrt(delx**2 + dely**2)
        theta = math.atan2(dely, delx)
        theta_degrees = math.degrees(theta)
        return radius, theta_degrees

    @staticmethod
    def mask_rad_angle(radius, angle):
        """
        Masks radius and angle.

        Args:
            radius (float): Radius.
            angle (float): Angle.

        Returns:
            float: Masked value.
        """
        return radius * 1000 + angle
    
    @staticmethod
    def _loadModel(filename):
        """
        Loads the YOLO model.

        Args:
            filename (str): Path to the YOLO model file.

        Returns:
            YOLO: Loaded YOLO model.
        """
        return YOLO(filename)

    @staticmethod
    def focusAligned(x, y):
        """
        Checks if the camera is focused on an aligned position.

        Args:
            x (int): X-coordinate.
            y (int): Y-coordinate.

        Returns:
            bool: True if the camera is focused on an aligned position, False otherwise.
        """
        return 200 <= x <= 440 and 200 <= y <= 460
