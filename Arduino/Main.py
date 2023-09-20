import time

import serial

conectar = serial.Serial("COM3", 115200, timeout=1)


while True:
    conectar.write("teste".encode())
    print(conectar.readline().decode("utf-8"))

