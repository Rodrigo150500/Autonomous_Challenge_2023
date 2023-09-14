import cv2
import Edge_detection as edge
import numpy as np


video = cv2.VideoCapture("./Data/Video/Lane/Pista_03.mp4")


def threshold(frame):
    hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)

    # Isolando as faixas
    # Aplicando o algoritmo de sobel no canal de luminosidade ao longo dos eixos X e Y
    _, sxbinary = edge.threshold(hls[:, :, 1], thresh=(180, 255))
    sxbinary = edge.blur_gaussian(sxbinary, ksize=3)

    # sxbinary = edge.mag_thresh(sxbinary, sobel_kernel=3, thresh=(80, 255))

    # Aplicando o threshold no canal de saturação, pois quanto maior o seu valor mais pura a cor será
    s_channel = hls[:, :, 2]  # Captando apenas o canal de saturação
    _, s_binary = edge.threshold(s_channel, (150, 255))

    # Aplicando threshold no canal vermelho do frame, isso fará como que faça a captação da cor amarela
    # também, o branco no BGR é (255,255,255), o amarelo é (0,255,255), então se zerarmos o vermelho conseuimos
    # o amarelo.
    _, r_thresh = edge.threshold(frame[:, :, 2], thresh=(150, 255))

    rs_binary = cv2.bitwise_and(s_binary, r_thresh)
    frameBinario = cv2.bitwise_or(rs_binary, sxbinary.astype(np.uint8))

    return frameBinario


if not video.isOpened():
    print("Erro ao abrir o vídeo.")
    exit()

while True:
    # Leia um quadro do vídeo
    ret, frame = video.read()

    imgBinaria = threshold(frame)


    # Se não foi possível ler um quadro, o vídeo terminou
    if not ret:
        break

    # Faça o processamento do quadro aqui, se necessário
    # Por exemplo, você pode exibir o quadro:

    # Pressione a tecla 'q' para sair do loop
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# Libere os recursos
video.release()
cv2.destroyAllWindows()



