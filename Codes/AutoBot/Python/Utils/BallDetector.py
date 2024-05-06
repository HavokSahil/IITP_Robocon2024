from ultralytics import YOLO
import serial
import math
import cv2

# This Portion was written by Sahil

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
        
 
 # This portion is written by Satyam Bhaiya
 
'''silostate = [
    [1, 0, 0],
    [1, -1, 0],
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
]
'''

blue, red, emp = 1, -1, 0

# priority_map is a dictionary that maps tuples representing the state of a silo (blue, red, empty) to their respective priorities.

priority_map = {
    (blue, red, emp): 1,        # Priority 1 for blue followed by red then empty
    (red, blue, emp): 2,        # Priority 2 for red followed by blue then empty
    (blue, blue, emp): 3,       # Priority 3 for two blue balls followed by empty
    (red, red, emp): 4,         # Priority 4 for two red balls followed by empty
    (emp, emp, emp): 5,         # Priority 5 for all empty silos
    (blue, emp, emp): 6,        # Priority 6 for blue followed by empty then empty
    (red, emp, emp): 7          # Priority 7 for red followed by empty then empty
}


class SiloDetector(BallDetector):
    def __init__(self, filename, imgsz=640, conf=0.45, iou=0.45, xCenter=320, yCenter=480):
        """Initializes SiloDetector object with given parameters."""
        super().__init__(filename, imgsz, conf, iou, xCenter, yCenter)
        self._model = self._loadModel(filename)
        self._imgsz = imgsz
        self._conf = conf
        self._iou = iou
        self.xCenter = xCenter
        self.yCenter = yCenter
        self.lastPos = None
        self.serialObj = None
        self.clutch = False

    def predict(self, silo):
        """Predicts the optimal silo to place a ball based on priority map."""
        order = []
        
        # Calculate priorities
        for row in silo:
            priority = priority_map.get(tuple(row), 1000)
            print(row)
            order.append(priority)
        
        print(len(order))
        # Find the min priority number and silo number
        if(len(order) > 0):
            min_priority = min(order)
            silo_number = order.index(min_priority) 
            return silo_number
        
        else:
            return 0

    def detectSilo(self, frame):
        """Detects silos and balls in the frame and determines the optimal silo for a ball."""
        silolist = list()
        blueballlist = list()
        redballlist = list()
        # Make predictions with the YOLOv8 model
        class_names = self._model.names
        results = self._model.predict(frame, imgsz=640, conf=0.40, iou=0.45)
        results = results[0]
        print(results)

        # Draw bounding boxes on the frame and display info
        for i, box in enumerate(results.boxes):
            tensor = box.xyxy[0]
            x1, y1, x2, y2 = int(tensor[0].item()), int(tensor[1].item()), int(tensor[2].item()), int(tensor[3].item())

            # Calculate center coordinates
            center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2

            # Get class index, name, and confidence
            class_index = int(box.cls[0].item())
            class_label = class_names[class_index] if 0 <= class_index < len(class_names) else f"Class {class_index + 1}"
            confidence = round(float(box.conf[0].item()), 2)

            # Display info in the frame
            # SILOS IS PURPLE
            if(class_index == 2):
                info_text = f"Object {i + 1}: {class_label} - Confidence: {confidence}\n Center: ({center_x}, {center_y})"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
                cv2.putText(frame, info_text, (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                # Adding box
                box = list()
                box.extend([x1, y1, x2, y2])
                silolist.append(box)

            elif(class_index == 1):
                info_text = f"Object {i + 1}: {class_label} - Confidence: {confidence}\n Center: ({center_x}, {center_y})"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(frame, info_text, (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
                ball = list()
                ball.extend([center_x, center_y])
                redballlist.append(ball)

            elif(class_index == 0):
                info_text = f"Object {i + 1}: {class_label} - Confidence: {confidence}\n Center: ({center_x}, {center_y})"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
                cv2.putText(frame, info_text, (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
                ball = list()
                ball.extend([center_x, center_y])
                blueballlist.append(ball)

        final_result = list()

        # Check each silo with each ball
        # FORMAT: SILO NUMBER , NO OF RED BALLS, NO OF BLUE BALLS
        for i in range(0, len(silolist)):
            new_record = list([i, 0, 0])
            final_result.append(new_record)
            for j in range(0, len(redballlist)):
                if(redballlist[j][0] > silolist[i][0] and redballlist[j][0] < silolist[i][2] and redballlist[j][1] > silolist[i][1] and redballlist[j][1] < silolist[i][3]):
                    final_result[i][1] += 1
                
            for j in range(0, len(blueballlist)):
                if(blueballlist[j][0] > silolist[i][0] and blueballlist[j][0] < silolist[i][2] and blueballlist[j][1] > silolist[i][1] and blueballlist[j][1] < silolist[i][3]):
                    final_result[i][2] += 1

        final_data = list()
        for i in final_result:
            rec = list()
            k = 0
            # ADD RED BALLS
            for j in range(i[1]):
                rec.append(-1)
                k += 1
            for j in range(i[2]):
                rec.append(1)
                k += 1
            for j in range(3 - k):
                rec.append(0)
            final_data.append(rec)

        silo_id = self.predict(final_data)
        print("SILO ID", silo_id)
        # Print pos
        cx = 0
        cy = 0
        if(len(silolist) > 0):
            cx = (silolist[silo_id][0] + silolist[silo_id][2]) / 2
            cy = (silolist[silo_id][0] + silolist[silo_id][2]) / 2
            print(silo_id, "::", cx, ",", cy)
        
            if(cx < 200):
                print("RIGHT")

            elif(cy > 400):
                print("LEFT")
        
            else:
                print("STRAIGHT")

        # Display the frame
        cv2.imshow('YOLOv8 Webcam Inference', frame)

    @staticmethod
    def _loadModel(filename):
        """Loads the YOLOv8 model from the given filename."""
        return BallDetector._loadModel(filename)
