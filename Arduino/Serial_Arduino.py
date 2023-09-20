import threading
import time

import serial

startMarker = '<'
endMarker = '>'
divMarker = '|'
dataStarted = False
dataBuf = ""
messageComplete = False


# ========================
# ========================
# the functions

def setupSerial(baudRate, serialPortName):
    global serialPort

    serialPort = serial.Serial(port=serialPortName, baudrate=baudRate, timeout=0, rtscts=True)

    print("Serial port " + serialPortName + " opened  Baudrate " + str(baudRate))



# ========================

def sendToArduino(stringToSend):
    # this adds the start- and end-markers before sending
    global startMarker, endMarker, serialPort

    stringWithMarkers = (startMarker)
    stringWithMarkers += stringToSend
    stringWithMarkers += (endMarker)

    serialPort.write(stringWithMarkers.encode('utf-8'))  # encode needed for Python3

def sendToArduino_Multi(msg1, msg2, msg3):
    # this adds the start- and end-markers before sending
    global startMarker, endMarker, serialPort

    stringWithMarkers = (startMarker)
    stringWithMarkers += msg1
    stringWithMarkers += (divMarker)
    stringWithMarkers += msg2
    stringWithMarkers += (divMarker)
    stringWithMarkers += msg3
    stringWithMarkers += (endMarker)

    serialPort.write(stringWithMarkers.encode('utf-8'))  # encode needed for Python3


# =======================

def recvLikeArduino():
    global startMarker, endMarker, serialPort, dataStarted, dataBuf, messageComplete

    if serialPort.inWaiting() > 0 and messageComplete == False:
        x = serialPort.read().decode("utf-8")  # decode needed for Python3

        if dataStarted == True:
            if x != endMarker:
                dataBuf = dataBuf + x
            else:
                dataStarted = False
                messageComplete = True
        elif x == startMarker:
            dataBuf = ''
            dataStarted = True

    if (messageComplete == True):
        messageComplete = False
        return dataBuf
    else:
        return "XXX"

    # ==================


def waitForArduino():
    # wait until the Arduino sends 'Arduino is ready' - allows time for Arduino reset
    # it also ensures that any bytes left over from a previous message are discarded

    print("Waiting for Arduino to reset")

    msg = "Arduino pronto"
    while msg.find("Arduino pronto") == -1:
        msg = recvLikeArduino()
        if not (msg == 'XXX'):
            print(msg)

    # Teste de envio
    sendToArduino("Teste de comunicacao")
    resp = ""
    espera = time.time()
    print("SERIAL-ARDUINO | Testando envio e recebimento")
    '''while resp != "OK":
        resp = recvLikeArduino()
        if time.time() - espera >= 5:
            print("SERIAL-ARDUINO | Aguardando confirmação do Arduino...")'''
    print("SERIAL-ARDUINO | Envio: OK; Recebimento: OK")


def desconectar():
    global serialPort
    serialPort.close()


class RecebimentoAutomatico(threading.Thread):
    resp = ""
    rec = True
    habilitado = True

    def __init__(self, id, nome):
        threading.Thread.__init__(self)
        self.id = id
        self.nome = nome

    def run(self):
        while True:
            if self.habilitado:
                if self.rec:
                    self.resp = recvLikeArduino()

                    if self.resp == "OK":
                        self.rec = False
                    '''else:
                        print(self.resp)'''

                    '''if self.resp.find("OK") != -1:
                        self.rec = False
                    print(self.resp)'''

    def getResp(self):
        if not self.rec:
            self.rec = True
            return self.resp
        else:
            return "---"

    def encerrar(self):
        self.habilitado = False

    def retomar(self):
        self.habilitado = True
