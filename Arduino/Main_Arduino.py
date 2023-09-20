import serial

serialPort = serial.Serial("COM3", baudrate=9600, timeout=1)


def receberArduino():
    while 1:
        arduinoData = serialPort.read().decode("utf-8")
        print(arduinoData)

def enviarArduino(msg):
    serialPort.write(msg.encode("utf-8"))


angulo = 'G'
while True:
    enviarArduino(angulo)