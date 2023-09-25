import time
import serial
import cv2
import Metodo_Aila as aila

#Conectando com o Arduino
conectar = serial.Serial("COM3", 9600)

#Abrindo a câmera
cam = cv2.VideoCapture(0)

if cam.isOpened():
    while True:
        #Capturando os frames
        ret, frame = cam.read()

        #Identificando o Ângulo
        Aila = aila.Lane(frame)
        anguloMD = Aila.angulo(frame=frame)

        #Enviando o angulo para o arduino
        conectar.write(anguloMD.encode())
        print(anguloMD)

        #Recebendo o que tem no serial do arduino com delay de 100 milisegundo
        time.sleep(1)

        #Fechando a câmera ao apertar q
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break
