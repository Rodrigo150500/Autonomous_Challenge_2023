from ultralytics import YOLO
import time
model = YOLO("best.pt")


def vision():
    results = model.predict(source="pessoa.jpg", show=True, conf=0.80)


    time.sleep(5)


vision()
