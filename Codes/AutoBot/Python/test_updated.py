from Autobot.BallDetector import BallDetector
from Autobot.Driver import Driver
from Autobot.SiloDetector import SiloDetector
from Autobot.Decider_Class import Decider
from Autobot.PID import PID
import cv2
import time
#length for angle of the computer is 38 cm
#angle 50 degrees

#Create a driver object
driver = Driver()
driver.initialiseSerial("COM6",9600)

#Create a PID object
pid = PID(1,0,0,320)

#Create a ball for the close camera for ball find mode
close_ball_detector = BallDetector("C:/Users/Suvra/OneDrive/Documents/IIT Patna/Robocon/Codes/Auto Bot/Python Code/really_big_model.pt",640,0.45,0.45,320,480,1)
#Create a ball detector for the far camera for ball find mode
far_ball_detector = BallDetector("C:/Users/Suvra/OneDrive/Documents/IIT Patna/Robocon/Codes/Auto Bot/Python Code/really_big_model.pt",640,0.45,0.45,320,480,1)
#And a silo detector for silo search mode
far_silo_detector = BallDetector("C:/Users/Suvra/OneDrive/Documents/IIT Patna/Robocon/Codes/Auto Bot/Python Code/really_big_model.pt",640,0.45,0.45,320,480,1)

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





#TO account for time lag
pid.restart()
while True:
   #Get the close camera frame
    close_ret,close_frame = close_cap.read()
    if not close_ret:
        print("Close Camera Frame Drop")
    
       
   #Get image stream from the far camera
    far_ret,far_frame = far_cap.read()

    if not far_ret:
        print("Far Camera frame drop")
    
    Decider.ballFollow(close_ball_detector,far_ball_detector,close_frame,far_frame,driver,pid)
    #Highlight frames
    close_ball_detector.highlightFrame(close_frame)            
    far_ball_detector.highlightFrame(far_frame)

    close_frame = cv2.flip(close_frame,1)
    far_frame = cv2.flip(far_frame,1)
    #Draw
    cv2.imshow("CLOSE",close_frame)
    cv2.imshow("FAR",far_frame)

    #Exit conditionscv2.imshow("AutoBot's Vision", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

driver.stop()
