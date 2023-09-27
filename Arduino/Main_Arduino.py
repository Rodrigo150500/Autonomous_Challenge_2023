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

        anguloInicial = anguloMD[:2]

        if anguloInicial != "+0" and anguloMD[0] == "+":
            #Trocar o anguloMD para -
            anguloLista = list(anguloMD)
            anguloLista[0] = '-'
            novoAngulo = ''.join(anguloLista)
            conectar.write(novoAngulo.encode())
        else:
            #Trocar o anguloMD para +
            anguloLista = list(anguloMD)
            anguloLista[0] = '+'
            novoAngulo = ''.join(anguloLista)
            conectar.write(novoAngulo.encode())
        #Enviando o angulo para o arduino
        #conectar.write(anguloMD.encode())

        #Recebendo o que tem no serial do arduino com delay de 100 milisegundo
        time.sleep(0.1)

        #Fechando a câmera ao apertar q
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break
