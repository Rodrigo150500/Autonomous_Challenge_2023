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


#comando = "yolo task=detect mode=train model=yolov8n.pt data='Autonomous_Challenge_2023/datasets/Autonomous-Vehicle-1/data.yaml' epochs=100 imgsz=800 plots=True"



#Executa o treinamento e deixa o modelo treinado dentro da ultima pasta de train
caminho_data_yaml = r"dataset/Autonomous-Car-1/data.yaml"

comando_yolo = f"yolo task=detect mode=train model=yolov8n.pt data={caminho_data_yaml} epochs=1 imgsz=800 plots=True"

# Execute o comando usando subprocess
processo = subprocess.Popen(comando_yolo, shell=True)
processo.wait()

