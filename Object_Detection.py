from ultralytics import YOLO

model = YOLO("best.pt")


results = model.predict(source="0", show=True, conf=0.80)

print(results.boxes)