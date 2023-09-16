import cv2
import Edge_detection as edge
import numpy as np


video = cv2.VideoCapture("./Data/Video/Lane/Pista_03.mp4")



while True:
    ret, frame = video.read()
    img = cv2.resize(frame, (640,480))
    cv2.imshow("Janela", img)
    cv2.waitKey(1)



