import time

from ultralytics import YOLO
import cv2

#{
# 0: 'Faixa_de_Pedestre',
# 1: 'Farol_Amarelo',
# 2: 'Farol_Verde',
# 3: 'Farol_Vermelho',
# 4: 'Pare',
# 5: 'Pessoa'
# }

listaObjetos = ['Faixa_de_Pedestre','Farol_Amarelo','Farol_Verde','Farol_Vermelho','Pare','Pessoa']
#Pare 220px largura
#Semafaro 93px largura
global model
model = YOLO('../objectDetection.pt').to('cuda')
class Object_Detection:
    def __init__(self,frame):

        self.orig_frame = frame

    def main(self):
        #Aplicando o frame no treinamento
        results = model.predict(self.orig_frame, show = True, conf = 0.4, stream=False)
        #Condição para verificar se tem algo sendo detectado
        if 'detection' not in results[0].verbose():
            lista = []
            res = ''
            #Armazena os objetos detectados
            result = results[0].verbose().strip().split(',')[:-1] #['2 Pessoas', '1 Pare']
            #Armazena o indice dos objetos
            for i in range(len(result)):
                indice = result.index(result[i]) #Armazena a quantidade de objetos detectados 0:1 obj, 1:2 obj

                #Faz uma varredura na listaObjeto e compara se o objeto detectado consta na lista e armazena o indice do objeto
                for j in range(len(listaObjetos)):
                    for resultado in results:
                        if ('Vermelho' in resultado[i].verbose()):
                            largura = resultado.boxes.xywh[i][2].item()
                            distancia = 100 / (largura / 85)
                            if listaObjetos[j] in result[i] and distancia <= 300:
                                lista.append((j)) #Armazena o indice do objeto detectado de acordo com o YOLO ['4','5']
                        if ("Pare" in resultado[i].verbose()):
                            largura = resultado.boxes.xywh[i][2].item()
                            distancia = 100/(largura/220)
                            if listaObjetos[j] in result[i] and distancia <= 300:
                                lista.append((j)) #Armazena o indice do objeto detectado de acordo com o YOLO ['4','5']
                        if("Pessoa" in resultado[i].verbose()):
                            largura = resultado.boxes.xywh[i][2].item()
                            distancia = 100/(largura/160)
                            if listaObjetos[j] in result[i] and distancia <= 300:
                                lista.append((j)) #Armazena o indice do objeto detectado de acordo com o YOLO ['4','5']



            #Concatena os indices do yolo detectados, retira da lista e coloca tudo em uma unica string
            for k in range(len(lista)):
                if k == len(lista)-1:
                    res += f'{lista[k]}'
                else:
                    res += f'{lista[k]},'
            return res

        else:
            return '6'


def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:
        ret, frame = cap.read()

        print(Object_Detection(frame).main())

        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break