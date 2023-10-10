from ultralytics import YOLO
import cv2

global model
model = YOLO('../best.pt').to('cuda')
class Object_Detection:
    def __init__(self,frame):

        self.orig_frame = frame

    def main(self):
        result = model.predict(self.orig_frame, show = True, conf = 0.7, stream=False)
        return result[0].verbose()

