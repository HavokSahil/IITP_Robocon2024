from Utils import BallDetector, SiloDetector
import cv2
import time

cap = cv2.VideoCapture(3)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Couldn't open the camera.")
    exit()

def serialTest_checkpoint0():
    filename="Resource/ball.pt"
    ballDetectorObject = BallDetector.BallDetector(filename)
    ballDetectorObject.initialiseSerial('/dev/ttyUSB0', 115200)

    while True:
        val = str(input("Enter character: "))
        if (val=="e"):
            break
        else:
            ballDetectorObject.sendCommandToSerial(val)

def ballTEST_checkpoint1():
    filename="Resource/ball.pt"

    confirmIter = 0

    ballDetectorObject = BallDetector.BallDetector(filename)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Couldn't capture a frame.")

        cv2.imshow("Feed", frame)

        count, pos, frame = ballDetectorObject.getPrediction(frame)
        if (count==0):
            print("No balls found")
            message = ballDetectorObject.classifyMissingBall()
            print(message)
        else:
            message = ballDetectorObject.classifyBallPresence(pos[0], pos[1])
            print(message)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

CONF_ITER_THRES = 15
confirmIterFocus = 0
confirmIterSilo = 0
confirmIterBall = 0
currentMode = "Silo"

def ballFollow_checkPoint2():
    filename="Resource/ball.pt"
    ballDetectorObject = BallDetector.BallDetector(filename)
    ballDetectorObject.initialiseSerial('/dev/ttyUSB0', 115200)
    siloModeConfig(ballDetectorObject)

    while True:
        print(currentMode)
        ballDetectorObject.setClutch(False)
        ret, frame = cap.read()
        if not ret:
            print("Error: Couldn't capture a frame.")
        else:
            cv2.imshow("Hi", frame)
            count, pos, _ = ballDetectorObject.getPrediction(frame)
            if (count==0):
                print("No balls found")
                message = ballDetectorObject.classifyMissingBall()
                print(message)
                if (message=="MISSING_RIGHT"):
                    ballDetectorObject.rotAClock()
                elif (message=="MISSING_LEFT"):
                    ballDetectorObject.rotClock()
                elif (message=="MISSING_BELOW"):
                    if (currentMode!="Focus"):
                        focusModeConfig(ballDetectorObject)
                    else:
                        siloModeConfig(ballDetectorObject)
                else:
                    if (currentMode == "Focus"):
                        siloModeConfig(ballDetectorObject)
                    else:
                        ballDetectorObject.rotAClock()
            
            else:
                message = ballDetectorObject.classifyBallPresence(pos[0], pos[1])
                print(message)

                if (currentMode=="Focus"):
                    if (BallDetector.BallDetector.focusAligned(pos[0], pos[1])):
                        triggerGripperConfig(ballDetectorObject)

                if (message=="CENTRE"):
                    ballDetectorObject.moveForward()
                elif (message=="LEFT"):
                    ballDetectorObject.rotClock()
                elif (message=="RIGHT"):
                    ballDetectorObject.rotAClock()
                else:
                    ballDetectorObject.stop()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

def focusModeConfig(ballDetectorObject):
    global currentMode
    global confirmIterFocus
    ballDetectorObject.stop()
    if (confirmIterFocus>CONF_ITER_THRES):
        currentMode = "Focus"
        confirmIterFocus=0
        ballDetectorObject.triggerRelease()
        ballDetectorObject.cameraDown()
        ballDetectorObject.eraseMemory()
        ballDetectorObject.lowerSpeed()
        time.sleep(2)
        ballDetectorObject.setClutch(False)
    else:
        ballDetectorObject.setClutch(True)
        print("WAITING FOR CONFIRMATION (FOCUS MODE)")
        confirmIterFocus+=1

def siloModeConfig(ballDetectorObject):
    global currentMode
    global confirmIterSilo
    ballDetectorObject.stop()
    if (confirmIterSilo>CONF_ITER_THRES):
        currentMode="Silo"
        confirmIterSilo = 0
        ballDetectorObject.cameraUp()
        ballDetectorObject.eraseMemory()
        ballDetectorObject.upperSpeed()
        time.sleep(2)
        ballDetectorObject.setClutch(False)
    else:
        ballDetectorObject.setClutch(True)
        confirmIterSilo+=1
        print("WATITING FOR CONF (SILO MODE)")


def triggerGripperConfig(ballDetectorObject):
    global currentMode
    global confirmIterBall
    ballDetectorObject.stop()
    if (confirmIterBall>CONF_ITER_THRES):
        print("=================Gripper Triggered===================\n"*5)
        confirmIterBall = 0
        ballDetectorObject.triggerGripper()
        currentMode="Silo"
        siloConfigBypass(ballDetectorObject)
        time.sleep(3)
        ballDetectorObject.setClutch(False)
    else:
        ballDetectorObject.setClutch(True)
        confirmIterBall+=1
        print("WATITING FOR CONF (BALL)")

def siloConfigBypass(ballDetectorObject):
    ballDetectorObject.cameraUp()
    ballDetectorObject.eraseMemory()
    ballDetectorObject.upperSpeed()

def siloDetect_checkpoint1():
        while True:
            silo_detector=SiloDetector("Resource/best.pt")
            ret, frame = cap.read()
            if not ret:
                print("Error: Couldn't capture a frame.")
            else:
                silo_detector.detectSilo(frame)
                cv2.imshow("Hi", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

if __name__== '__main__':
    ballFollow_checkPoint2()
    cap.release()
    cv2.destroyAllWindows()
