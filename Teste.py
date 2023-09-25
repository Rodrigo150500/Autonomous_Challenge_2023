import serial
import time

#Conectando com o arduino
ser = serial.Serial('COM3', baudrate=9600, timeout=1)

while True:
    ser.write("35".encode())
    time.sleep(2)
    ser.write('90'.encode())
    time.sleep(2)

    print(ser.readline().decode('utf-8'))



"""
while 1:
    if ser.inWaiting() > 0 and messageComplete == False:
        x = ser.readline().decode('utf-8')

        if dataStarted == True:
            if x != endMarker:
                dataBuf = dataBuf + x
            else:
                messageComplete = True
                dataStarted = False
        elif x == startMarker:
            dataBuf = ''
            dataStarted = True

    if messageComplete == True:
        messageComplete = False
        print(dataBuf)
    else:
        print('XXX')
"""