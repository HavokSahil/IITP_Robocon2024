from Autobot.BallDetector import BallDetector
from Autobot.Driver import Driver
from Autobot.SiloDetector import SiloDetector
from Autobot.Decider_Class import Decider
from Autobot.MasterChef import MasterChef
import cv2
import time

#Create a driver object
driver = Driver()
driver.initialiseSerial("COM11",9600)

masterChef = MasterChef("suvrayan", MasterChef.BALL_FOLLOW)

#Create a ball for the close camera for ball find mode
close_ball_detector = BallDetector("Resource/really_big_model.pt",640,0.45,0.45,320,480,1)
#Create a ball detector for the far camera for ball find mode
far_ball_detector = BallDetector("Resource/really_big_model.pt",640,0.45,0.45,320,480,1)
#And a silo detector for silo search mode
far_silo_detector = SiloDetector("Resource/really_big_model.pt",640,0.45,0.45,320,480,1)

#The laptop camera is the far camera
far_cap = cv2.VideoCapture(0)
far_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
far_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#The top camera is the close camera
close_cap = cv2.VideoCapture(1)
close_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
close_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

#If we cant open the far camera
if not far_cap.isOpened():
    print("ERROR::CANNOT OPEN FAR CAMERA")
    exit()

#If we cant open the close camera
if not close_cap.isOpened():
    print("ERROR::CANNOT OPEN CLOSE CAMERA")
    exit()    



       




while True:
   #Get the close camera frame
    close_ret,close_frame = close_cap.read()
    if not close_ret:
        print("Close Camera Frame Drop")
    
       
   #Get image stream from the far camera
    far_ret,far_frame = far_cap.read()

    if not far_ret:
        print("Far Camera frame drop")


    match masterChef.getMode():
        case MasterChef.BALL_FOLLOW:
            Decider.ballFollow(close_ball_detector,far_ball_detector,close_frame,far_frame,driver, masterChef)
            #Highlight frames
            close_ball_detector.highlightFrame(close_frame)            
            far_ball_detector.highlightFrame(far_frame)

            #Draw
            cv2.imshow("CLOSE",close_frame)
            cv2.imshow("FAR",far_frame)
            
        case MasterChef.BALL_FOCUS:
            Decider.ballFocusmode(close_frame, close_ball_detector, driver, masterChef)
        case MasterChef.SILO_FOLLOW:
            Decider.siloFollow(far_silo_detector, far_frame, driver, masterChef)
            far_silo_detector.highlightFrame(far_frame)

            cv2.imshow("SILO FAR", far_frame)
            
        
    #Exit conditions cv2.imshow("AutoBot's Vision", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

driver.stop()
