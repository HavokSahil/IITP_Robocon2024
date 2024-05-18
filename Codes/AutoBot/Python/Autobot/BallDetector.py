from ultralytics import YOLO
import cv2
from .Detector import Detector

class BallDetector(Detector):
    def __init__(self, filename, imgsz=640, conf=0.45, iou=0.45, xCenter=320, yCenter=480):
        super().__init__(filename, imgsz, conf, iou, xCenter, yCenter)
        self.lastPos = None

    def getPrediction(self, frame):
        """
        Predicts the position of the ball in the given frame.

        Returns:
            Tuple: (count, [x, y], frame[annotated])
        """
        
        result = self._model.predict(frame, imgsz=self._imgsz, conf=self._conf, iou=self._iou)[0]
        count = len(result)
        if count == 0:
            return 0, None, frame
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
        
    def eraseMemory(self):
        """
        Remove the Last position of detection from memory
        """
        self.lastPos = None