from .BallDetector import BallDetector
from .SiloDetector import SiloDetector
from .Driver import Driver


class Decider:
    @staticmethod
    def ballFollow(close_ball_detector,far_ball_detector,close_frame,far_frame,driver):
        
        #Close detector
        close_ball_detector.updateDetection(close_frame)

        #Far detector
        far_ball_detector.updateDetection(far_frame)



        #If no close balls
        close_ball = close_ball_detector.getPrediction(close_frame)

        #If close ball exists (Position is (-1,-1))
        if(close_ball[0]>0):
            #Find the location
            loc_val = BallDetector.classifyBallPresence(close_ball[0],close_ball[1])
            
            print(close_ball)
            if(loc_val == BallDetector.CENTER):
                print("Ball is close and in the centre")
                driver.stop()
            elif(loc_val == BallDetector.LEFT):
                print("Ball is close and in the left")
                driver.rotAClock()
            elif(loc_val == BallDetector.RIGHT):
                print("Ball is close and in the right")
                driver.rotClock()
            else:
                print("The ball is close, but location can't be determined")

        else:
            far_ball = far_ball_detector.getPrediction(far_frame)
            if(far_ball[0]>0):    
                #Find the location
                loc_val = BallDetector.classifyBallPresence(far_ball[0],far_ball[1])
                
                if(loc_val == BallDetector.CENTER):
                    print("Ball is far and in the centre")
                    driver.moveForward()
                elif(loc_val == BallDetector.LEFT):
                    print("Ball is far and in the left")
                    driver.rotAClock()
                elif(loc_val == BallDetector.RIGHT):
                    print("Ball is far and in the right")
                    driver.rotClock()
                else:
                    
                    print("The ball is far, but location can't be determined")
            
            else:
                print("BALL CANT BE FOUND, ROTATE")
                driver.rotClock()
