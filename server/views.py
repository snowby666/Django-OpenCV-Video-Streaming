import numpy as np
import dlib
import cv2
from keras.models import load_model
from imutils import face_utils
from django.shortcuts import render
import os
import csv
import time
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(DIR + '/server/models/shape_predictor_68_face_landmarks.dat')
emotion_classifier = load_model(DIR + '/server/models/_mini_XCEPTION.102-0.66.hdf5', compile=False)

(lBegin, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eyebrow"]
(rBegin, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eyebrow"]
(l_lower, l_upper) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]
(i_lower, i_upper) = face_utils.FACIAL_LANDMARKS_IDXS["inner_mouth"]
(el_lower, el_upper) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(er_lower, er_upper) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

def index(request):
    global checkpoint
    checkpoint = '1'
    return render(request, 'server/index.html')

EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised", "neutral"]
def get_emotion(faces, frame):
    try:
        x, y, w, h = face_utils.rect_to_bb(faces)
        roi = cv2.resize(frame[y:y + h, x:x + w], (64, 64))
        roi = roi / 255.0
        roi = np.array([roi]) 

        preds = emotion_classifier.predict(roi)[0]
        # emotion_probability = np.max(preds)
        emotion = EMOTIONS[preds.argmax()]

        return emotion
    except:
        pass
    
def clear_csv():
    with open(DIR+'/server/static/server/data/fps.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["FPS"])
        f.close()

# If you want to store data for diffrent users, create an OOP template and integrate to this class
import asyncio
class VideoStreamConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.i = 0
        self.fps = 0
        self.prev = 0
        self.new = 0
        self.loop = asyncio.get_running_loop()
        await self.accept()

    async def disconnect(self, close_code):
        self.i = 0
        self.fps = 0
        self.prev = 0
        self.new = 0
        clear_csv()
        # print(f"WebSocket closed with code {close_code}.")
        self.stop = True
        raise StopConsumer()

    async def fps_count(self):
        try:
            self.new = time.time()
            self.fps = int(1/(self.new-self.prev))
            self.prev = self.new
        except cv2.error as e:
            raise e
    
    async def draw_border(self, img, pt1, pt2, color, thickness, r, d):
        x1,y1 = pt1
        x2,y2 = pt2

        # Top left
        cv2.line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness)
        cv2.line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness)
        cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)

        # Top right
        cv2.line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness)
        cv2.line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness)
        cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)

        # Bottom left
        cv2.line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness)
        cv2.line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness)
        cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)

        # Bottom right
        cv2.line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness)
        cv2.line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness)
        cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)
            
    async def receive(self, bytes_data):
        
        if not (bytes_data):
            self.i = 0
            self.fps = 0
            self.prev = 0
            self.new = 0
            clear_csv()
            print('Closed connection')
            await self.close()
        else:
            
            # self.frame = cv2.imdecode(np.frombuffer(bytes_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            # self.frame = imutils.resize(self.frame, width=500,height=500)
            
            self.frame = await self.loop.run_in_executor(None, cv2.imdecode, np.frombuffer(bytes_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            self.frame = cv2.resize(self.frame, (500, 500))
            self.gray = cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
            self.i += 1
            
            # Face detection and feature extraction
            self.detections = await self.loop.run_in_executor(None, detector, self.gray, 0)
            if (self.detections):
                # In this case, we only take the first face found
                self.detection = self.detections[0]
                self.x1, self.y1, self.x2, self.y2 = self.detection.left(), self.detection.top(), self.detection.right(), self.detection.bottom()
                await self.draw_border(self.frame, (self.x1, self.y1), (self.x2, self.y2), (0, 255, 0), 2, 20, 10)
                
                self.shape = await self.loop.run_in_executor(None, predictor, self.frame, self.detection)
                self.shape = face_utils.shape_to_np(self.shape)
                
                # Feature extraction
                self.leyebrow = self.shape[lBegin:lEnd]
                self.reyebrow = self.shape[rBegin:rEnd]
                self.openmouth = self.shape[l_lower:l_upper]
                self.innermouth =self. shape[i_lower:i_upper]
                self.lefteye = self.shape[el_lower:el_upper]
                self.righteye = self.shape[er_lower:er_upper]
                
                # Convex hull
                self.reyebrowhull = cv2.convexHull(self.reyebrow)
                self.leyebrowhull = cv2.convexHull(self.leyebrow)
                self.openmouthhull = cv2.convexHull(self.openmouth) 
                self.innermouthhull = cv2.convexHull(self.innermouth)
                self.leyehull = cv2.convexHull(self.lefteye)
                self.reyehull = cv2.convexHull(self.righteye)
                self.emotion = await self.loop.run_in_executor(None, get_emotion, self.detection, self.gray)
                
                await self.fps_count()  
                cv2.putText(self.frame, "FPS: {}".format((self.fps)), (330,40),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (54, 161, 255), 1)
                cv2.putText(self.frame, "Frames: {}".format((self.i)), (220,40),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (54, 161, 255), 1)
                cv2.putText(self.frame, "Emotion: {}".format((self.emotion)), (50,40),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (54, 161, 255), 1)
                cv2.drawContours(self.frame, [self.reyebrowhull, self.leyebrowhull, self.openmouthhull, self.innermouthhull, self.leyehull, self.reyehull], -1, (219, 255, 99), 1)
                
            # Recording the FPS values in real time (this is made only for only 1 user for now)
            row = {"FPS":self.fps}
            with open(DIR+'/server/static/server/data/fps.csv', 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=row.keys())
                writer.writerow(row)
                
            # Encoding and sending the image
            self.buffer_img = await self.loop.run_in_executor(None, cv2.imencode, '.jpeg', self.frame)
            self.b64_img = base64.b64encode(self.buffer_img[1]).decode('utf-8')
            # Send the base64 encoded image back to the client
            asyncio.sleep(100/1000)
            await self.send(self.b64_img)