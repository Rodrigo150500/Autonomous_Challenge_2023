import cv2
import os

#Criando o nome do arquivo
cont = 1
pasta = f'./Record/'
fileName = f'Record{cont}.mp4'

caminho = os.path.join(pasta, fileName)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
if os.path.exists(caminho):
    while (os.path.exists(caminho)):
        cont += 1
        fileName = f'Record{cont}.mp4'
        caminho = os.path.join(pasta, fileName)
        if ((os.path.exists(caminho)) == False):
            writer = cv2.VideoWriter(f"Record/{fileName}", fourcc, 25.0, (640, 480))
            break
else:
    writer = cv2.VideoWriter(f"Record/{fileName}", fourcc, 25.0, (640, 480))

recording = False

while True:
    ret, frame = cap.read()

    if ret:
        cv2.imshow('Video', frame)

        if recording:
            writer.write(frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('r'):
        recording = not recording
        print(f'Recording: {recording}')

cap.release()
writer.release()
cv2.destroyWindow()
