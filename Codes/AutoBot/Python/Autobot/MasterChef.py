#Explaination given by Sahil: A masterchef is a master of the kitchen and decides what ingredients his underlings can bring him
#He can only be forced by the supreme one aka me :)
class MasterChef:

    #The confidence threshold (Higher than the confidence of the average engineer,which lasts 13 frames :) )
    CONF_THRES = 15


    #Written in hexadecimal because we like overcomplicating simple things
    BALL_FOLLOW = 0x1
    BALL_FOCUS  = 0x2
    SILO_FOLLOW = 0x4
    
    CREDIT_ON = 0x5
    CREDIT_OFF = 0x6

    RED_MODE = 0x7
    BLUE_MODE = 0x8


    #We are initializing duh..... Why are you even reading this comment
    def __init__(self, id, mode):
        self.id = id
        self.mode = mode
        self.consider = None
        self.condidence = 0
        self.credit = MasterChef.CREDIT_ON
    

    #Gently poke things to increase confidence................. WHAT???
    def poke(self, proposal):
        if (proposal == self.consider):
            self.condidence+=1
            if (self.condidence>=MasterChef.CONF_THRES):
                self.setMode(proposal)
                self.earnCredit()
        else:
            self.consider = proposal


    #The ultimate tool to make the masterchef obey us
    def forceMaster(self, order):
        self.mode = order
        self.earnCredit()

    #This function get's the current mode... like the header says
    def getMode(self):
        return self.mode
    
    #DO I NEED TO ADD A COMMENT HERE
    def setMode(self, mode):
        self.mode = mode

    #CREDIT +10000
    def earnCredit(self):
        self.credit = MasterChef.CREDIT_ON
    

    #SPEND A CREDIT 
    def spendCredit(self):
        self.credit = MasterChef.CREDIT_OFF
    
    #Checks if we are broke or not
    def isCreditAvailable(self):
        return self.credit == MasterChef.CREDIT_ON
