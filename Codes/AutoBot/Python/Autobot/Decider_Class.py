from .BallDetector import BallDetector
from .SiloDetector import SiloDetector
from .Driver import Driver
from .Detector import Detector
from .MasterChef import MasterChef
#For threading 
from threading import Thread


class Decider:
    #Line follow methof
    @staticmethod
    def LineFollow(driver:Driver,masterchef:MasterChef):
        
        #In case it has not started line following, send the command again
        driver.startLineFollow()


        #If line follow has ended
        if(driver.shouldStartWinning()):
            masterchef.forceMaster(MasterChef.BALL_FOLLOW)


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
        driver.setRotSpeed(30)

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
        driver.setRotSpeed(30)
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
                                masterChef.spendCredit()                                    

                            
                        else:
                            driver.moveForward()
                        
                                
                    case BallDetector.LEFT:
                        driver.rotAClock()
                    case BallDetector.RIGHT:
                        driver.rotClock()
                        
    
        
    @staticmethod
    def siloFollow(silo_detector:SiloDetector, frame, driver:Driver , masterChef:MasterChef):
        driver.setRotSpeed(30)
        areaThreshold = 85000 #The distance which is the threshold for the silo to be considered near
        silo_loc = silo_detector.getLocOptimalSilo(frame)

        if (silo_loc[0]>0):
            
            loc_val = SiloDetector.classifyPresence(silo_loc[0],  silo_loc[1])

            print("Area ",silo_loc[2])
            #If silo size is greater than a certain threshold (aka it is close)
            if(silo_loc[2]>areaThreshold and len(silo_detector.silos)==1):
                print("SILO FOCUSING")
                masterChef.poke(MasterChef.SILO_FOCUS)
                print("POKING FOR SILO FOCUS")
                # if we are near silo (ultrasonic calibration)
                #If both Ultrasounds are close
                driver.stop()
            else:
                print("SILO UNFOCUSING")
                masterChef.demotivateMaster()
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
            masterChef.demotivateMaster()
            driver.rotAClock()

    @staticmethod
    def siloFocus(siloDetector: SiloDetector, frame, driver: Driver, masterChef: MasterChef):
        driver.setRotSpeed(20)
        driver.startInfraTransmission()
        driver.readBuffer()

        left_val, right_val = float(driver.data['l']), float(driver.data['r'])
        print("SILO FOCUS MODE")
        print(left_val,":",right_val)
        silo_loc = siloDetector.getLocOptimalSilo(frame)

        if (silo_loc[0]>0):
            if(left_val==1 and right_val==1):
                print("ALIGNED")
                silo_loc = siloDetector.getLocOptimalSilo(frame)
                #X cord
                xcord = silo_loc[0]

                #Final adjustments
                if(xcord<90):
                    driver.moveLeft()

                elif(xcord>135):
                    driver.moveRight()
                
                #Else drop the ball
                else:
                    driver.triggerRelease()
                    #driver.stopInfraTransmission()#CHECK THIS
                    masterChef.forceMaster(MasterChef.BALL_FOLLOW)
                
            
        
            #Elif only left is aligned
            elif(left_val==1):
                print("LEFT IS ALIGNED, ALIGNING RIGHT")
                driver.moveForward()

            elif(right_val==1):
                print("RIGHT IS ALIGNED, ALIGNING LEFT")
                driver.moveForward()

            #Go nearer to silo if the IRs are not triggered
            else: 
                loc_val = SiloDetector.classifyPresence(silo_loc[0],  silo_loc[1])

                if (loc_val == SiloDetector.CENTER):
                    print("Silo close and is in front")
                    driver.moveForward()
                elif (loc_val == SiloDetector.LEFT):
                    print("Silo close is in left")
                    driver.rotAClock()
                elif (loc_val == SiloDetector.RIGHT):
                    print("Silo close is in right")
                    driver.rotClock()

        #Revert back to silo follow mode by "POKING" it
        else:
            print("UNABLE TO FIND SILO IN SILO FOCUS MODE, REVERTING TO SILO FOLLOW MODE")
            masterChef.poke(MasterChef.SILO_FOLLOW)




        ''' #If both are aligned
        if(left_val==1 and right_val==1):
            print("ALIGNED")
            silo_loc = siloDetector.getLocOptimalSilo(frame)

            if(silo_loc[0] in range())
            
        
        #Elif only left is aligned
        elif(left_val==1):
            print("LEFT IS ALIGNED, ROTATING ANTICLOCKWISE")
            driver.rotAClock()

        elif(right_val==1):
            print("RIGHT IS ALIGNED, ROTATING CLOCKWISE")
            driver.rotClock()

        #Elif if neither is triggered silo is found
        else: 
            silo_loc = siloDetector.getLocOptimalSilo(frame)
            
            #IF silo is found,move towards it
            if (silo_loc[0]>0):
                loc_val = SiloDetector.classifyPresence(silo_loc[0],  silo_loc[1])

                if (loc_val == SiloDetector.CENTER):
                    print("Silo close and is in front")
                    driver.moveForward()
                elif (loc_val == SiloDetector.LEFT):
                    print("Silo close is in left")
                    driver.rotAClock()
                elif (loc_val == SiloDetector.RIGHT):
                    print("Silo close is in right")
                    driver.rotClock()
            
            #Else if even silo cant be found
            else:
                print("UNABLE TO FIND SILO IN SILO FOCUS MODE, REVERTING TO SILO FOLLOW MODE")
                masterChef.poke(MasterChef.SILO_FOLLOW)
            '''


        
        