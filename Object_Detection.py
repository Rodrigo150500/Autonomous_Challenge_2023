from ultralytics import YOLO
from ultralytics.yolo.v8.detect import DetectionPredictor
import cv2

cap = cv2.VideoCapture(0)
model = YOLO("best.pt")

model.predict(source="0", show=True, conf=0.5)

