from ultralytics import YOLO
import time
model = YOLO("yolov7_custom.pt")


def vision():
    results = model.predict(source="0",conf=0.80)

    for result in results:
        #bbox = result.xyxy[0]  # Coordenadas da caixa delimitadora [x_min, y_min, x_max, y_max]
        classe = result.names[0]  # Classe do objeto detectado
        confianca = result.pred[0][4]  # Nível de confiança da detecção
        print(f"Classe: {classe}, Coordenadas da Caixa Delimitadora: , Confiança: {confianca}")


vision()
