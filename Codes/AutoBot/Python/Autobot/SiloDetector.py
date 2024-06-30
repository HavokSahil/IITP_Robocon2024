from .Detector import Detector
import cv2


class SiloDetector(Detector):

    # Class Variables
    BLUE, RED, EMP = 1, -1, 0           # Encoded Constants
    
    #Blue priority map
    priority_map_blue = {
        (BLUE, RED, EMP): 1,            # Priority 1 for BLUE followed by RED then EMPty
        (RED, BLUE, EMP): 2,            # Priority 2 for RED followed by BLUE then EMPty
        (BLUE, BLUE, EMP): 3,           # Priority 3 for two BLUE balls followed by EMPty
        (RED, RED, EMP): 4,             # Priority 4 for two RED balls followed by EMPty
        (EMP, EMP, EMP): 5,             # Priority 5 for all EMPty silos
        (BLUE, EMP, EMP): 6,            # Priority 6 for BLUE followed by EMPty then EMPty
        (RED, EMP, EMP): 7              # Priority 7 for RED followed by EMPty then EMPty
    }

    priority_map_red = {
        (RED, BLUE, EMP): 1,            # Priority 1 for BLUE followed by RED then EMPty
        (BLUE, RED, EMP): 2,            # Priority 2 for RED followed by BLUE then EMPty
        (RED, RED, EMP): 3,           # Priority 3 for two BLUE balls followed by EMPty
        (BLUE, BLUE, EMP): 4,             # Priority 4 for two RED balls followed by EMPty
        (EMP, EMP, EMP): 5,             # Priority 5 for all EMPty silos
        (RED, EMP, EMP): 6,            # Priority 6 for BLUE followed by EMPty then EMPty
        (BLUE, EMP, EMP): 7              # Priority 7 for RED followed by EMPty then EMPty
    }
    def __init__(self, filename, imgsz=640, conf=0.45, iou=0.45, xCenter=320, yCenter=480,team=1):
        super().__init__(filename, imgsz, conf, iou, xCenter, yCenter,)
        self.team = team
        self.priority_map = list()
        if(self.team == 1):
            self.priority_map = SiloDetector.priority_map_blue
        #ELSE IF RED
        if(self.team == -1):
            self.priority_map = SiloDetector.priority_map_red



    def getLocOptimalSilo(self, frame):
        """
        Identify the best silo

        Returns:
            Tuple: (x, y) The coordinate of centre of the best silo.
            (-1,-1) if no silo
        """
        self.updateDetection(frame)
        #Reset silostate
        self.silostate = list()
        
        #Changing depending on team
        #IF BLUE
        


        #For every silos
        for silo in self.silos:

            #Count number of red balls in the silo and the number of blue balls in the silo (Actual order does not matter)
            redballcount = 0
            blueballcount = 0

            #Now checking every red ball
            for ball in self.red_balls:
                #Getting the ball centre
                centre_x = (ball[0]+ball[2])//2
                centre_y = (ball[1]+ball[3])//2
                
                #Getting the silo centre
                x1 = silo[0]
                y1 = silo[1]
                x2 = silo[2]
                y2 = silo[3]

                #Now checking if the ball is inside the silo
                if(centre_x>x1 and centre_x<x2 and centre_y>y1 and centre_y<y2):
                    redballcount+=1

            #Now checking every blue ball
            for ball in self.blue_balls:
                #Getting the ball centre
                centre_x = (ball[0]+ball[2])//2
                centre_y = (ball[1]+ball[3])//2
                
                #Getting the silo centre
                x1 = silo[0]
                y1 = silo[1]
                x2 = silo[2]
                y2 = silo[3]

                #Now checking if the ball is inside the silo
                if(centre_x>x1 and centre_x<x2 and centre_y>y1 and centre_y<y2):
                    blueballcount+=1


            #Create a new silo
            new_silo = list()
            #Adding the red balls
            for i in range(0,redballcount):
                new_silo.append(SiloDetector.RED)

            #Adding the blue balls
            for i in range(0,blueballcount):
                new_silo.append(SiloDetector.BLUE)

            self.silostate.append(new_silo)            

            print(self.silostate)#For debugginh


        #Find the best silo
        order = []
            
            
        # Calculate priorities
        for row in self.silostate:
            priority = self.priority_map.get(tuple(row), 1000)
            order.append(priority)

            # Find the min priority number and silo number
        if(len(order)>0):
            min_priority = min(order)
            silo_number = order.index(min_priority) 
        
            
            cx = (self.silos[silo_number][0]+self.silos[silo_number][2])/2
            cy = (self.silos[silo_number][1]+self.silos[silo_number][3])/2

            return (cx,cy)

        else:
            self.best_silo = -1
            return(-1,-1)

        
        '''#Reset reading
        self.updateDetection(frame)
        
        #Creating a new silostate
        final_result = list()
        for i in range(0, len(self.silos)):
            new_record = list([i, 0, 0])
            final_result.append(new_record)

            for j in range(0, len(self.red_balls)):
                #Centre of ball 
                #x co-ordinate
                bx = (self.red_balls[j][0]+self.red_balls[j][0])/2
                #y-co-ordinate
                by = (self.red_balls[j][0]+self.red_balls[j][0])/2

                if( bx > self.silos[i][0] and
                    bx < self.silos[i][2] and
                    by > self.silos[i][1] and
                    by < self.silos[i][3]):
                    
                    final_result[i][1] += 1
                
            for j in range(0, len(self.blue_balls)):
                #Centre of ball 
                #x co-ordinate
                bx = (self.red_balls[j][0]+self.red_balls[j][0])/2
                #y-co-ordinate
                by = (self.red_balls[j][0]+self.red_balls[j][0])/2
                if(bx > self.silos[i][0] and 
                    bx < self.silos[i][2] and 
                    by > self.silos[i][1] and 
                    by < self.silos[i][3]):
                    
                    final_result[i][2] += 1

        final_data = list()
        for i in final_result:
            rec = list()
            k = 0

            for j in range(i[i]):
                rec.append(SiloDetector.RED)
                k+=1
            for j in range(i[2]):
                rec.append(SiloDetector.BLUE)
                k += 1
            for j in range(3-k):
                rec.append(SiloDetector.EMP)
            
            final_data.append(rec)

        silo_id = self.predictOptimal(final_data)

        cx, cy = 0, 0
        if (len(self.silos)>0):
            cx = (self.silos[silo_id][0] + self.silos[silo_id][2]) / 2
            cy = (self.silos[silo_id][1] + self.silos[silo_id][3]) / 2
            self.logMessage(f"{silo_id}: ({cx}, {cy})")

            return (cx, cy)
        
        return None
        '''
