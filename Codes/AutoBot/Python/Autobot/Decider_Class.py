from .BallDetector import BallDetector
from .SiloDetector import SiloDetector
from .Driver import Driver
from .Detector import Detector
from .MasterChef import MasterChef
#For threading 
from threading import Thread


class Decider:
    @staticmethod
    def ballFollow(close_ball_detector, far_ball_detector, close_frame, far_frame, driver, masterChef):
        
        #Close detector thread
        t1 = Thread(target = BallDetector.updateDetection,args=(close_ball_detector,close_frame,))

        #Far detector thread
        t2 = Thread(target=BallDetector.updateDetection,args=(far_ball_detector,far_frame,))
        #Start both threads
        t1.start()
        t2.start()

        #Wait for threads to join
        t1.join()
        t2.join()       
    
        #If no close balls
        close_ball = close_ball_detector.getPrediction(close_frame)

        #Default speed
        

        #If close ball exists (Position is (-1,-1))
        if(close_ball[0]>0):
            #Find the location
            loc_val = BallDetector.classifyPresence(close_ball[0],close_ball[1])
            """
            # if the ball is already in focused range then poke the masterchef to change mode to silo search
            if (Detector.focusAligned(close_ball[0], close_ball[1])):
                print("Focus Aligned: Now Poking MasterChef")
                masterChef.poke(MasterChef.SILO_FOLLOW)
                if ((masterChef.getMode() == MasterChef.SILO_FOLLOW) and (masterChef.isCreditAvailable())):
                    masterChef.spendCredit()
                    driver.triggerGripper()
                    driver.gripperUp()
                    """
         
            if(loc_val == BallDetector.CENTER):
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
        close_ball_detector.updateDetection(close_frame)
        
        if (masterChef.isCreditAvailable()):
            driver.triggerRelease()
            driver.gripperDown()
            masterChef.spendCredit()

        pos = close_ball_detector.getPrediction(close_frame)

        print(pos)
        if (pos[0] < 0):
            masterChef.poke(MasterChef.BALL_FOLLOW)

        else:

            presenceStatus = close_ball_detector.classifyCloseBallPresence(pos[0], pos[1])
            match presenceStatus:
                    case BallDetector.CENTER:
                        if close_ball_detector.focusAligned(pos[0],pos[1]):
                            print("=\n"*50)
                            masterChef.earnCredit()

                            if masterChef.isCreditAvailable():
                                #PICK UP THE BALL
                                driver.stop()
                                driver.triggerGripper()
                                

                                driver.gripperUp()
                                masterChef.spendCredit()

                                #FORCE MASTERCHEF TO CHANGE
                                masterChef.forceMaster(MasterChef.SILO_FOLLOW)                                    

                            
                        else:
                            driver.moveForward()
                        
                                
                    case BallDetector.LEFT:
                        driver.rotAClock()
                    case BallDetector.RIGHT:
                        driver.rotClock()
                        
        
        
    @staticmethod
    def siloFollow(silo_detector:SiloDetector, frame, driver:Driver , masterChef:MasterChef):
        driver.startSonicTransmission()
        sonicThreshold = 20 #The distance which is the threshold for the ultrasound to activate
        silo_loc = silo_detector.getLocOptimalSilo(frame)


        driver.readBuffer()

        left_val = float(driver.data['l'])

        right_val = float(driver.data['r'])

        print(left_val,":",right_val)


        if (silo_loc[0]>0):
            
            loc_val = SiloDetector.classifyPresence(silo_loc[0],  silo_loc[1])

            # if we are near silo (ultrasonic calibration)
            #If both Ultrasounds are close
            if(left_val < sonicThreshold and right_val<sonicThreshold):
                if(silo_loc[0]>200):
                    print("Move Right")
                    driver.moveRight()
                else:
                    print("Release")
                    driver.triggerRelease()
                    masterChef.forceMaster(MasterChef.BALL_FOLLOW)

            #Else if the left ultrasound is close and the right is far
            elif(left_val<sonicThreshold):

                print("SILO ANCHORING USING LEFT")
                #We rotate anticlockwise,using the left silo as an achor
                driver.rotAClock()
            #Else if the right ultrasound is close and left is far
            elif(right_val<sonicThreshold):
                print("SILO ANCHORING USING RIGHT")
                driver.rotClock()
            
            #Else if the silo is far away

            else:
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


        #If silo is not detected
        else:
            print("NO SILO FOUND")
            driver.rotAClock()

        