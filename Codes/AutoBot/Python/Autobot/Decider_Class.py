from .BallDetector import BallDetector
from .SiloDetector import SiloDetector
from .Driver import Driver


class Decider:
    @staticmethod
    def ballFollow(close_ball_detector,far_ball_detector,close_frame,far_frame,driver,pid):
        
        #Update the prediction
        close_ball_detector.updateDetection(close_frame)
        far_ball_detector.updateDetection(far_frame)


        #Decider.ballFollow(close_ball_detector,far_ball_detector,close_frame,far_frame,driver)
        close_ball_detector.getPrediction()
        far_centre = far_ball_detector.getPrediction()
        close_centre = close_ball_detector.getPrediction()

        
        #If ball is close
        if(close_centre[0]>=0):
            print("CLOSE")
            if(close_centre[0] <100 or close_centre[0]>540):
                print("CENTER::::::::::::::::",close_centre[0])
                pid_val = pid.run(close_centre[0])
                abs_pid = abs(pid.run(close_centre[0]))
                val = abs_pid/(abs_pid+40)

                print(pid.getError(close_centre[0]),"::",abs_pid,"::",val**4)
                
        
                if(pid_val<0):
                    print("CLOSE AND ATTEMPTING TO ROTATE ANTI CLOCK")
                    driver.rotAClock()
                else:
                    print("CLOSE AND ATTEMPTING TO ROTATE CLOCK")
                    driver.rotClock()
            #elif(close_centre[1]<300):
                #Ball is in centre and close, STOP
                #driver.moveForward()
            else:
                print("REACHED")
                driver.stop()
                #Change state using masterchef to focus

        #Calculate PID
        elif(far_centre[0]>=0):
            print("FAR")
            if(BallDetector.classifyBallPresence(far_centre[0],far_centre[1])!=BallDetector.CENTER):
                pid_val = pid.run(far_centre[0])
                abs_pid = abs(pid.run(far_centre[0]))
                val = abs_pid/(abs_pid+40)

                print(pid.getError(far_centre[0]),"::",abs_pid,"::",val**4)
                
               
                if(pid_val<0):
                    print("FAR AND ATTEMPTING TO ROTATE ANTI CLOCK")
                    driver.rotAClock()
                else:
                    print("FAR AND ATTEMPTING TO ROTATE CLOCK")
                    driver.rotClock()
            else:
                print("MOVING FORWARD")
                #Ball is in centre, go ahead
                driver.moveForward()
            

        else:
            print("NO BALL")
            driver.stop()


