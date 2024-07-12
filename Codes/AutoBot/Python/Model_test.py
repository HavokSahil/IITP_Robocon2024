from Autobot.BallDetector import BallDetector
from Autobot.Driver import Driver
from Autobot.SiloDetector import SiloDetector
from Autobot.Decider_Class import Decider
from Autobot.MasterChef import MasterChef
import cv2
import time
import numpy as np


model_path = "C:/Users/Suvra/OneDrive/Documents/IIT Patna/Robocon/Codes/Auto Bot/IITP_Robocon2024/Codes/AutoBot/python/Resource/final.pt"
close_ball_detector = BallDetector(model_path,640,0.45,0.45,320,480,1)

#The top camera is the close camera
close_cap = cv2.VideoCapture(0)
close_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
close_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


while True:
    #Get the close camera frame
    close_ret,close_frame = close_cap.read()

    close_ball_detector.updateDetection(close_frame)
    close_ball_detector.highlightFrame(close_frame)
    

    #Show the frame
    cv2.imshow("Close",close_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

