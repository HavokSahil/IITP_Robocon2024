from .Detector import Detector
import cv2


class SiloDetector(Detector):

    # Class Variables
    SILO, RED_BALL, BLUE_BALL = 2, 1, 0 # Class Index For Classification
    BLUE, RED, EMP = 1, -1, 0           # Encoded Constants
    priority_map = {
        (BLUE, RED, EMP): 1,            # Priority 1 for BLUE followed by RED then EMPty
        (RED, BLUE, EMP): 2,            # Priority 2 for RED followed by BLUE then EMPty
        (BLUE, BLUE, EMP): 3,           # Priority 3 for two BLUE balls followed by EMPty
        (RED, RED, EMP): 4,             # Priority 4 for two RED balls followed by EMPty
        (EMP, EMP, EMP): 5,             # Priority 5 for all EMPty silos
        (BLUE, EMP, EMP): 6,            # Priority 6 for BLUE followed by EMPty then EMPty
        (RED, EMP, EMP): 7              # Priority 7 for RED followed by EMPty then EMPty
    }

    def __init__(self, filename, imgsz=640, conf=0.45, iou=0.45, xCenter=320, yCenter=480):
        super().__init__(filename, imgsz, conf, iou, xCenter, yCenter)

    
    def predictOptimal(self, silo):
        """
        Assigns the Optimal Choice based on Priority Map

        Args:
           silo (List): A list of states of silo.
        
        Returns:
            Int: Index of chosen silo
        """
        order = []
        for row in silo:
            priority = SiloDetector.priority_map.get(tuple(row), 1000)
            self.logMessage(row)
            order.append(priority)

        self.logMessage(len(order))

        # Find the min priority number and silo number
        if (len(order)>0):
            min_priority = min(order)
            silo_number = order.index(min_priority)
            return silo_number
    
        else: return 0

    
    def detectSiloState(self, frame):
        """
        Detect silos in frame and Calculate its State

        Args:
            frame(Mat): OpenCV frame
        
        Returns:
            Tuple: A tuple of lists of (Silo, Blue Balls, Red Balls)
        """
        siloList, blueList, redList = list(), list(), list()

        class_names = self._model.names
        result = self._model.predict(frame, imgsz=self._imgsz, conf=self._conf, iou=self._iou)[0]

        self.logMessage(str(result))

        for i, box in enumerate(result.boxes):
            tensor = box.xyxy[0]
            x1, y1, x2, y2 = int(tensor[0].item()), int(tensor[1].item()), int(tensor[2].item()), int(tensor[3].item())
            center_x, center_y = (x1 + x2)//2, (y1 + y2)//2

            class_index = int(box.cls[0].item())
            class_label = class_names[class_index] if (0<=class_index<len(class_names)) else f"Class {class_index + 1}"
            confidence = round(float(box.conf[0].item()), 2)

            if (class_index == SiloDetector.SILO):
                info_text = f"Object {i + 1}: {class_label} - Confidence: {confidence}\n Center: ({center_x}, {center_y})"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
                cv2.putText(frame, info_text, (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                box = list()
                box.extend([x1, y1, x2, y2])
                siloList.append(box)

            elif (class_index == SiloDetector.RED):
                info_text = f"Object {i + 1}: {class_label} - Confidence: {confidence}\n Center: ({center_x}, {center_y})"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(frame, info_text, (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
                ball = list()
                ball.extend([center_x, center_y])
                redList.append(ball)
            
            elif (class_index == SiloDetector.BLUE):
                info_text = f"Object {i + 1}: {class_label} - Confidence: {confidence}\n Center: ({center_x}, {center_y})"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
                cv2.putText(frame, info_text, (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
                ball = list()
                ball.extend([center_x, center_y])
                blueList.append(ball)

        return siloList, blueList, redList


    def getLocOptimalSilo(self, frame):
        """
        Identify the best silo

        Returns:
            Tuple: (x, y) The coordinate of centre of the best silo.
        """
        siloList, blueList, redList = self.detectSiloState(frame)
    
        final_result = list()
        for i in range(0, len(siloList)):
            new_record = list([i, 0, 0])
            final_result.append(new_record)

            for j in range(0, len(redList)):
                if(redList[j][0] > siloList[i][0] and
                    redList[j][0] < siloList[i][2] and
                    redList[j][1] > siloList[i][1] and
                    redList[j][1] < siloList[i][3]):
                    
                    final_result[i][1] += 1
                
            for j in range(0, len(blueList)):
                if(blueList[j][0] > siloList[i][0] and 
                    blueList[j][0] < siloList[i][2] and 
                    blueList[j][1] > siloList[i][1] and 
                    blueList[j][1] < siloList[i][3]):
                    
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
        if (len(siloList)>0):
            cx = (siloList[silo_id][0] + siloList[silo_id][2]) / 2
            cy = (siloList[silo_id][0] + siloList[silo_id][2]) / 2
            self.logMessage(f"{silo_id}: ({cx}, {cy})")

            return cx, cy
        
        return None