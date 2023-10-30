import time
import serial
import cv2
import Metodo_Aila as aila
import Object_Detection as od
#Conectando com o Arduino
conectar = serial.Serial("COM5", 9600)

#Abrindo a câmera
camAng = cv2.VideoCapture(2, cv2.CAP_DSHOW)
camObj = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if camAng.isOpened():
    while True:
        #Capturando os frames
        retAng, frameAng = camAng.read()
        retObj, frameObj = camObj.read()

        #Declarando os objetos
        Aila = aila.Lane(frameAng)
        Obj = od.Object_Detection(frameObj)

        anguloMD = Aila.angulo(frame=frameAng, multi=400)
        objeto = Obj.main()

        #Concatenando os valores

        envio = f'[[{anguloMD},{objeto.strip()},]'
        conectar.write(envio.encode())
        print(envio)

        time.sleep(0.1)
        #Fechando a câmera ao apertar q
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break
#possiveis soluções
#Inverter a camera
#Aumentar o diferencial
#Aumentar a altura da Aila

