from .BallDetector import BallDetector
from .SiloDetector import SiloDetector
from .Driver import Driver
from .Detector import Detector
from .MasterChef import MasterChef

class Decider:
    @staticmethod
    def ballFollow(close_ball_detector, far_ball_detector, close_frame, far_frame, driver, masterChef):
        
        #Close detector
        close_ball_detector.updateDetection(close_frame)

        #Far detector
        far_ball_detector.updateDetection(far_frame)



        #If no close balls
        close_ball = close_ball_detector.getPrediction(close_frame)

        #If close ball exists (Position is (-1,-1))
        if(close_ball[0]>0):
            #Find the location
            loc_val = BallDetector.classifyPresence(close_ball[0],close_ball[1])

            # if the ball is already in focused range then poke the masterchef to change mode to silo search
            if (Detector.focusAligned(close_ball[0], close_ball[1])):
                print("Focus Aligned: Now Poking MasterChef")
                masterChef.poke(MasterChef.SILO_FOLLOW)
                if ((masterChef.getMode() == MasterChef.SILO_FOLLOW) and (masterChef.isCreditAvailable())):
                    masterChef.spendCredit()
                    driver.triggerGripper()
                    driver.gripperUp()

            elif(loc_val == BallDetector.CENTER):
                print("Ball is close and in the centre")
                driver.stop()
                masterChef.poke(MasterChef.BALL_FOCUS)
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
                loc_val = BallDetector.classifyPresence(far_ball[0],far_ball[1])
                
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

    def ballFocusmode(close_frame, close_ball_detector, driver, masterChef):

        count, pos, close_frame = close_ball_detector.getPrediction(close_frame)

        if (count == 0):
            masterChef.poke(MasterChef.BALL_FOCUS)

        else:

            presenceStatus = close_ball_detector.classifyBallPresence(pos[0], pos[1])

            match presenceStatus:
                    case BallDetector.CENTER:
                        driver.stop()
                        driver.triggerRelese()
                        driver.gripperDown()
                        if close_ball_detector.focusAligned(pos[0],pos[1]):
                            driver.triggerGripper()
                            driver.gripperUp()
                        else:
                            driver.lower()
                            driver.moveForward()
                        
                        """
                        if driver.triggerGripper():
                            driver.gripperUp()
                        else:
                            while not driver.triggerGripper:
                                driver.lowerSpeed()
                                driver.moveForward()
                                driver.triggerGripper()"""
                                
                    case BallDetector.LEFT:
                        driver.rotAClock()
                    case BallDetector.RIGHT:
                        driver.rotClock()
        
        
    @staticmethod
    def siloFollow(silo_detector, frame, driver, masterChef):
        
        silo_loc = silo_detector.getLocOptimalSilo(frame)

        if (silo_loc[0]>0):
            
            loc_val = SiloDetector.classifyPresence(silo_loc[0],  silo_loc[1])

            # if we are near silo (ultrasonic calibration)
            # To be written

            #if we are far from silo
            if (loc_val == SiloDetector.CENTER):
                print("Silo is in front")
                driver.moveForward()
            elif (loc_val == SiloDetector.LEFT):
                print("Silo is in left")
                driver.rotAClock()
            elif (loc_val == SiloDetector.RIGHT):
                print("Silo is in right")
                driver.rotClock()

        else:
            driver.rotAClock()

        