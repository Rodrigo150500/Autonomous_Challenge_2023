import serial
import cv2
import Metodo_Aila as aila

conectar = serial.Serial("COM3", 115200, timeout=1)
cam = cv2.VideoCapture(0)

if cam.isOpened():
    while True:
        ret, frame = cam.read()
        Aila = aila.Lane(frame)

        anguloMD = Aila.angulo(frame=frame)

        conectar.write(anguloMD.encode("utf-8"))

        print(conectar.readline().decode("utf-8"))

        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break