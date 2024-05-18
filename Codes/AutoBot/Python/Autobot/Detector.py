import cv2
from ultralytics import YOLO
import math
import logging

class Detector:
    def __init__(self, filename, imgsz=640, conf=0.45, iou=0.45, xCenter=320, yCenter=480):
        self._model = self._loadModel(filename)
        self._imgsz = imgsz
        self._conf = conf
        self._iou = iou
        self.xCenter = xCenter
        self.yCenter = yCenter

        self.echo = False
        self._logger = self.initialiseLogger()


    def getPrediction(self, frame):
        """
        Predicts the position of the OOI(Object of Interest) in the given frame.

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
            return count, [center_x, center_y], frame

    def setEcho(self, value):
        """
        Sets the Echo of Logging of Commands (ON: messages are printed on terminal, OFF: otherwise)

        Args:
            command(bool): 'True' for ECHO on, 'False' for ECHO off
        
        Raises:
            Exception: If given value is not bool
        """

        if (type(value)==bool):
            self.echo = value

            console_handler = logging.StreamHandler()   # Creating handler for logging in console 
            console_handler.setLevel(logging.INFO)      # Set the logging level for handlers
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            console_handler.setFormatter(formatter)     # Set formatter for the handler

            if (self.echo):
                self._logger.addHandler(console_handler)
            else:
                self._logger.removeHandler(console_handler)


    def logMessage(self, message):
        self._logger.info(message)


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

    @staticmethod
    def initialiseLogger():
        """
        Creates a Custom logger (Logging Module)

        Returns:
            Logger: Instance of Custom Logger
        """

        logger = logging.getLogger('autobot_logger')
        logger.setLevel(logging.INFO)

        # Create handlers
        file_handler = logging.FileHandler("autobot.log", mode='a')    # Handler for logging to a file

        # Set the logging level for handlers
        file_handler.setLevel(logging.INFO)

        # Create a formatter and set it for the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)

        return logger