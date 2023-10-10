import cv2
from ultralytics import YOLO

def main():
    model = YOLO('best.pt').to('cuda')
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    while True:
        if cap.isOpened():

            ret, frame = cap.read()

            results = model(frame, show=True, conf=0.7, stream=True)

            for r in results:
                result = r.cuda().verbose()
                print(result)
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break

main()
