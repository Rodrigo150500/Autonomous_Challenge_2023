from ultralytics import YOLO

model = YOLO('yolov8s.pt')
model.train(data="Autonomous Car dataset/data.yaml", epochs=5, imgsz=640, plots=True )

