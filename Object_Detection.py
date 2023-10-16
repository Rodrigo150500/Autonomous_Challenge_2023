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

global model
model = YOLO('../best.pt').to('cuda')
class Object_Detection:
    def __init__(self,frame):

        self.orig_frame = frame

    def main(self):
        results = model.predict(self.orig_frame, show = True, conf = 0.8, stream=False)

        if 'detection' not in results[0].verbose():
            res = ''
            result = results[0].verbose().strip().split(',')[:-1]
            for i in range (len(result)):
                indice = result.index(result[i])
                for j in range (len(listaObjetos)):
                    if listaObjetos[j] in result[i]:
                        result[indice] = str(j)

            for k in range (len(result)):
                if k == len(result)-1:
                    res += f'{result[k]}'
                else:
                    res += f'{result[k]},'
            return res
        else:
            return '6'


def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:
        ret, frame = cap.read()

        Object_Detection(frame).main()

        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break

