from Autobot.BallDetector import BallDetector
from Autobot.Driver import Driver
from Autobot.SiloDetector import SiloDetector
import cv2
import time


#Create a video Caputure
detector = SiloDetector("C:/Users/Suvra/OneDrive/Documents/IIT Patna/Robocon/Codes/Auto Bot/Python Code/really_big_model.pt",640,0.45,0.45,320,480,1)
cap = cv2.VideoCapture(0)




while True:
    ret,frame = cap.read()

    print(detector.getLocOptimalSilo(frame))



    detector.highlightFrame(frame)
    cv2.imshow("Frame",frame)
    #Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
