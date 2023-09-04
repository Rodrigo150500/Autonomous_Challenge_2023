import cv2

vid1 = cv2.VideoCapture(1)
vid2 = cv2.VideoCapture(0)
while True:
    _, frames = vid2.read()
    ret, frame = vid1.read()

    cv2.imshow("Janela", frame)
    cv2.imshow("Janela02",frames)
    if(cv2.waitKey(1) & 0xFF == ord('q')):
        break
cv2.destroyAllWindows()