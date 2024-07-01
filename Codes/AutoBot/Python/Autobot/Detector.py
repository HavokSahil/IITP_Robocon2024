import cv2
from ultralytics import YOLO
import math
import logging

class Detector:
    # Class Variables
    MISSING_LEFT = 7
    MISSING_RIGHT = 8
    MISSING_UNKNOWN = 9
    MISSING_BELOW = 10

    CENTER = 4
    LEFT = 5
    RIGHT = 6
    SILO, RED_BALL, BLUE_BALL = 2, 1, 0 # Class Index For Classification

    #Our team
    BLUE_TEAM = 1
    RED_TEAM  = -1

    #Initializing 
    def __init__(self, filename, imgsz=640, conf=0.45, iou=0.45, xCenter=320, yCenter=480):
        #Creating a model
        self._model = YOLO(filename)
        #Getting class names if it is required later
        self.class_names = self._model.names


        #Setting hyperparameters
        self._imgsz = imgsz
        self._conf = conf
        self._iou = iou
        self.xCenter = xCenter
        self.yCenter = yCenter
        

        #Logging used for debugging
        self.echo = False
        self._logger = self.initialiseLogger()

        #Create 3 silo states for predicting silos, red balls and blue balls
        self.silos = list()
        self.red_balls = list()
        self.blue_balls = list()

    def updateDetection(self,frame):
        #Reading from the frame
    

        #Refresing predictions
        self.silos = list()
        self.red_balls = list()
        self.blue_balls = list()

        #Now we create the result of our predictions
        results = self._model.predict(frame, imgsz=640, conf=0.2, iou=0.45)
        results = results[0]

        #Now for every detected ball
        for i,box in enumerate(results.boxes):
            tensor = box.xyxy[0]
            #Getting the bounding box
            x1, y1, x2, y2 = int(tensor[0].item()), int(tensor[1].item()), int(tensor[2].item()), int(tensor[3].item())
        
            # Calculate center coordinates
            #center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
           
            # Get class index, name, and confidence
            class_index = int(box.cls[0].item())

            #Calculating them just in case they are required later
            class_label = self.class_names[class_index] if 0 <= class_index < len(self.class_names) else f"Class {class_index + 1}"
            confidence = round(float(box.conf[0].item()), 2)

            #Now we are updating the various lists
             #IF IT IS A SILO   
            if(class_index==Detector.SILO):#SILO
                
            
                #Adding box
                box = list()
                box.extend([x1,y1,x2,y2])
                self.silos.append(box)
                    
            #If it is a red ball
            elif(class_index == Detector.RED_BALL):
                
                ball = list()
                ball.extend([x1,y1,x2,y2])
                self.red_balls.append(ball)

            #If it is a blue ball
            elif(class_index == Detector.BLUE_BALL):
                ball = list()
                ball.extend([x1,y1,x2,y2])
                self.blue_balls.append(ball)

    def highlightFrame(self,frame):

        #Highlight every item from the list
        for i in self.blue_balls:
            cv2.rectangle(frame,[i[0],i[1]],[i[2],i[3]],(255,0,0),5)
        for i in self.red_balls:
            cv2.rectangle(frame,[i[0],i[1]],[i[2],i[3]],(0,0,255),5)
        for i in self.silos:
            cv2.rectangle(frame,[i[0],i[1]],[i[2],i[3]],(0,255,0),5)

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
    def classifyPresence(x, y):
        """
        Classifies the position of the object based on its coordinates.

        Args:
            x (int): X-coordinate of the object.
            y (int): Y-coordinate of the object.

        Returns:
            str: State of the object (CENTRE, RIGHT, LEFT).
        """

        # Check if the point lies inside the trapezium
        f1 = 7*y-24*x+2880
        f2 = 7*y+24*x-12480

        if (f1<0 and f2<0):
            return Detector.CENTER
        elif (f1<0 and f2>0):
            return Detector.RIGHT
        else:
            return Detector.LEFT

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
