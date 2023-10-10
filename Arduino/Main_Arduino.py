import time
import serial
import cv2
import Metodo_Aila as aila
import Object_Detection as od
#Conectando com o Arduino
#conectar = serial.Serial("COM5", 9600)

#Abrindo a câmera
cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if cam.isOpened():
    while True:
        #Capturando os frames
        ret, frame = cam.read()
        retObj, frameObj = cap.read()
        #Identificando o ângulo
        Aila = aila.Lane(frame)
        anguloMD = Aila.angulo(frame=frame)

        obj = od.Object_Detection(frameObj)
        objeto = obj.main()
        print(objeto)
        #Enviando o angulo para o arduino
        #conectar.write(anguloMD.encode())
        print(anguloMD)
        #Recebendo o que tem no serial do arduino com delay de 100 milisegundo
        #time.sleep(0.2)

        #Fechando a câmera ao apertar q
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break
