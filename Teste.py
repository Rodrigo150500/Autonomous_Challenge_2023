import cv2

cam1 = cv2.VideoCapture(0)
cam2 = cv2.VideoCapture(1)

if not cam1.isOpened():
    print("Camera 1 Falhou")

if not cam2.isOpened():
    print("Camera 2 Falhou")

while True:

    ret1, frame1 = cam1.read()
    ret2, frame2 = cam2.read()

    frame = cv2.hconcat([frame1, frame2])
    cv2.imshow("Cameras", frame)
    if (cv2.waitKey(1) & 0xFF == ord('q')):
        break

cam1.release()
cam2.release()