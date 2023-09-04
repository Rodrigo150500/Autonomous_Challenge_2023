import os
import ultralytics
from roboflow import Roboflow
from IPython import display
from ultralytics import YOLO
import subprocess

#Colocar a pastar na raiz e na datasets


#Pega o dataset rotulado no roboflow
rf = Roboflow(api_key="MEvZPHINvbeyB0QxbIq5")
project = rf.workspace("highway-e8ii4").project("autonomous-vehicle-fk49l")
dataset = project.version(1).download("yolov8")

#comando = "yolo task=detect mode=train model=yolov8n.pt data='Autonomous_Challenge_2023/datasets/Autonomous-Vehicle-1/data.yaml' epochs=100 imgsz=800 plots=True"



#Executa o treinamento e deixa o modelo treinado dentro da ultima pasta de train
caminho_data_yaml = r"datasets/Autonomous-Vehicle-1/data.yaml"

comando_yolo = f"yolo task=detect mode=train model=yolov8n.pt data={caminho_data_yaml} epochs=10 imgsz=800 plots=True"

# Execute o comando usando subprocess
processo = subprocess.Popen(comando_yolo, shell=True)
processo.wait()

