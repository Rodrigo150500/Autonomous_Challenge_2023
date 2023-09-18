import os
import ultralytics
from roboflow import Roboflow
from ultralytics import YOLO
import subprocess

#Colocar a pastar na raiz e na datasets


#Pega o dataset rotulado no roboflow

#rf = Roboflow(api_key="lE0MW8JlxXNEUuFW3czT")
#project = rf.workspace("fiap-wzxme").project("autonomous-car-m3fz5")
#dataset = project.version(1).download("yolov8")


#Executa o treinamento e deixa o modelo treinado dentro da ultima pasta de train
caminho_data_yaml = r"Dataset/Autonomous-Car-1/data.yaml"

comando_yolo = f"yolo task=detect mode=train model=yolov8n.pt data={caminho_data_yaml} epochs=1 imgsz=800 plots=True"

# Execute o comando usando subprocess
processo = subprocess.Popen(comando_yolo, shell=True)
processo.wait()

