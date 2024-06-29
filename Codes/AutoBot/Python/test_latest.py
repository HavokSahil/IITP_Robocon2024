from Autobot.BallDetector import BallDetector
from Autobot.Driver import Driver
from Autobot.SiloDetector import SiloDetector
import cv2
import time

cap = cv2.VideoCapture(3)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Couldn't open the camera.")
    exit()

_ball_weights_file = 'Resource/ball.pt'
_silo_weights_file = 'Resource/silo.pt'
_baud_rate = 115200
_serial_address = '/dev/ttyUSB0'

class MasterChef:

    CONF_THRES = 15

    BALL_SEARCH = 0x0
    BALL_FOLLOW = 0x1
    BALL_FOCUS  = 0x2
    SILO_SEARCH = 0x3
    SILO_FOLLOW = 0x4
    
    CREDIT_ON = 0x5
    CREDIT_OFF = 0x6

    RED_MODE = 0x7
    BLUE_MODE = 0x8

    def __init__(self, id, mode):
        self.id = id
        self.mode = mode
        self.consider = None
        self.condidence = 0
        self.credit = MasterChef.CREDIT_ON
    
    def poke(self, proposal):
        if (proposal == self.consider):
            self.condidence+=1
            if (self.condidence>=MasterChef.CONF_THRES):
                self.setMode(proposal)
                self.earnCredit()
        else:
            self.consider = proposal

    def forceMaster(self, order):
        self.mode = order

    def getMode(self):
        return self.mode
    
    def setMode(self, mode):
        self.mode = mode

    def earnCredit(self):
        self.credit = MasterChef.CREDIT_ON
    
    def spendCredit(self):
        self.credit = MasterChef.CREDIT_OFF
    
    def isCreditAvailable(self):
        return self.credit == MasterChef.CREDIT_ON



def ballSearchModeConfig(driver):
    driver.stop()
    driver.gripperDown()
    driver.cameraUp()
    driver.upperSpeed()
    driver.triggerRelease()

def focusModeConfig(driver):
    driver.stop()
    driver.cameraDown()
    driver.lowerSpeed()

def siloSearchModeConfig(driver):
    driver.stop()
    driver.triggerGripper()
    driver.gripperUp()
    driver.cameraUp()
    driver.upperSpeed()

def ballSearchMode(frame, ballDetector, driver, masterChef):
    count, pos, _frame = ballDetector.getPrediction(frame)
    if count!=0:
        driver.stop()
        masterChef.forceMaster(MasterChef.BALL_FOLLOW)
    else:
        driver.rotClock()
    
    return _frame


def ballFollowMode(frame, ballDetector, driver, masterChef):
    count, pos, _frame = ballDetector.getPrediction(frame)

    if (count == 0):

        missingStatus = ballDetector.classifyMissingBall()

        match missingStatus:
            case BallDetector.MISSING_RIGHT:
                driver.rotClock()
            case BallDetector.MISSING_LEFT:
                driver.rotAClock()
            case BallDetector.MISSING_BELOW:
                masterChef.poke(MasterChef.BALL_FOCUS)

    else:

        presenceStatus = ballDetector.classifyBallPresence(pos[0], pos[1])

        match presenceStatus:
            case BallDetector.CENTER:
                driver.moveForward()
            case BallDetector.LEFT:
                driver.rotAClock()
            case BallDetector.RIGHT:
                driver.rotClock()
    
    return _frame


def ballFocusmode(frame, ballDetector, driver, masterChef):

    count, pos, _frame = ballDetector.getPrediction(frame)

    if (count == 0):
        masterChef.poke(MasterChef.BALL_SEARCH)

    else:

        presenceStatus = ballDetector.classifyBallPresence(pos[0], pos[1])

        if (BallDetector.focusAligned(pos[0], pos[1])):
            masterChef.poke(MasterChef.SILO_SEARCH)

        else:
            match presenceStatus:
                case BallDetector.CENTER:
                    driver.moveForward()
                case BallDetector.LEFT:
                    driver.rotAClock()
                case BallDetector.RIGHT:
                    driver.rotClock()
    
    return _frame


def siloSearchMode(frame, siloDetector, driver, masterChef):
    pass

def siloFollowMode(frame, siloDetector, driver, masterChef):
    pass

def main():

    ballDetector = BallDetector(_ball_weights_file)
    siloDetector = SiloDetector(_silo_weights_file)

    driver = Driver()
    driver.initialiseSerial(_serial_address, _baud_rate)

    masterChef = MasterChef("", MasterChef.BALL_SEARCH)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame Drop")
            continue
        
        match masterChef.getMode():

            case MasterChef.BALL_SEARCH:
                if (masterChef.isCreditAvailable()):
                    ballSearchModeConfig(driver)
                    masterChef.spendCredit()

                frame = ballSearchMode(frame, ballDetector, driver, masterChef)

            case MasterChef.BALL_FOLLOW:
                frame = ballFollowMode(frame, ballDetector, driver, masterChef)
                    
            case MasterChef.BALL_FOCUS:
                if (masterChef.isCreditAvailable()):
                    focusModeConfig(driver)
                    masterChef.spendCredit()
                
                frame = ballFocusmode(frame, ballDetector, driver, masterChef)
            
            case MasterChef.SILO_SEARCH:
                if (masterChef.isCreditAvailable()):
                    siloSearchModeConfig(driver)
                    masterChef.spendCredit()

                frame = siloSearchMode(frame, siloDetector, driver, masterChef)

            case MasterChef.SILO_FOLLOW:

                frame = siloFollowMode(frame, siloDetector, driver, masterChef)
            

        cv2.imshow("AutoBot's Vision", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break





