from ultralytics import YOLO
import cv2
from .Detector import Detector

class BallDetector(Detector):

    #Codes to define where the ball is missing
    MISSING_LEFT = 0
    MISSING_RIGHT = 1
    MISSING_UNKNOWN = 2
    MISSING_BELOW = 3
    CENTER = 4
    LEFT = 5
    RIGHT = 6

    #Our team
    BLUE_TEAM  = 1
    RED_TEAM = -1


    #Initialization 
    def __init__(self, filename, imgsz=640, conf=0.45, iou=0.45, xCenter=320, yCenter=480,team = 1):
        super().__init__(filename, imgsz, conf, iou, xCenter, yCenter)
        self.lastPos = None
        self.team = team


    #Get prediction will give us the largest class
    def getPrediction(self, frame):
        """
        
        Remember to update predictions before using this
        Predicts the position of the closest ball in the screen

        Returns:
            [x, y] if ball is present
            [-1.-1] if no ball is present
        """
        
        

        #Use list of blue balls if we are in the blue team, else use red balls
        balls = list()
        if(self.team == BallDetector.BLUE_TEAM):
            balls = self.blue_balls
        else:
            balls = self.red_balls

        #If balls are present
        if(len(balls)>0):
            area = 0

            closest = [-1,-1,-1,-1]
            #Find the largest ball (using area) and return that
            for i in balls:
                new_area = abs(i[0]-i[2])*abs(i[1]-i[3])
                
                #Find the ball with the largest area
                if(new_area>area):
                    closest = i
                    area = new_area
                
            #Find new centres
            centre_x = (closest[0]+closest[2])/2
            centre_y = (closest[1]+closest[3])/2


            #Update the last position
            
            #If ball found
         
            self.lastPos = [centre_x,centre_y]
            #Return the new centers
            return [centre_x,centre_y]
        
        #If no ball is found
        else:
            return [-1,-1]




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
                    missingClass = BallDetector.MISSING_BELOW
            elif self.lastPos[0] <= 160:
                missingClass = BallDetector.MISSING_LEFT
            elif self.lastPos[0] >= 480:
                missingClass = BallDetector.MISSING_RIGHT
        return missingClass

    @staticmethod
    def classifyBallPresence(x, y):
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
            return BallDetector.CENTER
        elif (f1<0 and f2>0):
            return BallDetector.RIGHT
        else:
            return BallDetector.LEFT
        
    @staticmethod
    def classifyCloseBallPresence(x, y):
        if (x<200):
            return BallDetector.LEFT
        elif (x>440):
            return BallDetector.RIGHT
        else:
            return BallDetector.CENTER
        
    def eraseMemory(self):
        """
        Remove the Last position of detection from memory
        """
        self.lastPos = None
