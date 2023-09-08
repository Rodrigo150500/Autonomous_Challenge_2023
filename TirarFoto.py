import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time
def tirarFoto():

    # Inicializar a captura de vídeo
    cap = cv2.VideoCapture(1)  # 0 representa a câmera padrão

    # Verificar se a câmera foi aberta com sucesso
    if not cap.isOpened():
        print("Erro ao abrir a câmera.")
        exit()

    # Capturar um quadro
    ret, frame = cap.read()
    while True:
        cv2.imshow("Janele", frame)
        time.sleep(2)
        cv2.imwrite("foto.jpg", frame)

        break


    if not ret:
        print("Não foi possível capturar o quadro.")
        exit()

    # Salvar o quadro como uma imagem

    # Liberar a captura
    cap.release()

    print("Foto tirada e salva como 'foto.jpg'.")


def mostrarFoto():

    # Carregar a imagem
    imagem = mpimg.imread("foto.jpg")

    # Exibir a imagem
    plt.imshow(imagem)
    cv2.line(imagem,(0,240),(640,240),(255,255,0),2)
    plt.title('Minha Imagem')
    plt.show()


tirarFoto()
mostrarFoto()