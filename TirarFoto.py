import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time
def tirarFoto():

    # Inicializar a captura de vídeo
    cap = cv2.VideoCapture(0,cv2.CAP_DSHOW )  # 0 representa a câmera padrão

    # Verificar se a câmera foi aberta com sucesso
    # Capturar um quadro
    ret, frame = cap.read()
    time.sleep(2)
    cv2.imshow("Janele", frame)

    cv2.imwrite("foto.jpg", frame)


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