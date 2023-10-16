import time
import cv2
import numpy as np
import Edge_detection as edge
import matplotlib.pyplot as plt
from ultralytics import YOLO


class Lane:
    def __init__(self, orig_frame):

        # Isolando as faixas
        self.orig_frame = orig_frame
        self.rs_binary = None
        self.lane_line_markings = None

        # Plotar o ROI
        self.roi_points = np.float32([
            (0, 440),  # Top-left
            (0, 480),  # Bottom-left
            (640, 480),  # Borron-right
            (640, 440)  # Top-right
        ])

        self.roi_pointsAux = np.float32([
            (0, 350),  # Top-left
            (0, 390),  # Bottom-left
            (640, 390),  # Borron-right
            (640, 350)  # Top-right
        ])

        self.roi_pointsMD = np.float32([
            (140, 300),  # Top-left
            (0, 480),  # Bottom-left
            (640, 480),  # Borron-right
            (500, 300)  # Top-right
        ])

        self.orig_image_size = self.orig_frame.shape[::-1][1:]

        width = self.orig_image_size[0]  # 640

        # ROI Principal
        self.transformation_matrix = None
        self.inv_transformation_matrix = None
        self.warped_frame = None

        # ROI Auxiliar
        self.transformation_matrixAux = None
        self.inv_transformation_matrixAux = None
        self.warped_frameAux = None

        # ROI Média Central
        self.transformation_matrixMD = None
        self.inv_transformation_matrixMD = None
        self.warped_frameMD = None

        self.padding = int(0.25 * width)
        self.orig_image_size = self.orig_frame.shape[::-1][1:]

        self.desire_roi_points = np.float32([
            [self.padding, 0],  # Top-left corner
            [self.padding, self.orig_image_size[1]],  # Bottom-left corner
            [self.orig_image_size[0] - self.padding, self.orig_image_size[1]],  # Bottom-right corner
            [self.orig_image_size[0] - self.padding, 0]  # Top-right corner
        ])

        # Histograma
        self.histogram = None
        self.histogramAux = None
        self.histogramMD = None

        # Janelas Deslizantes
        self.no_of_windows = 10
        self.margin = int((1 / 12) * width)  # Margem da largura da janela. Quanto menor o número mais largo a janela
        self.minpix = int((1 / 24) * width)  # Centraliza a próxima janela através da média pelo min de pixels

        # Media Central
        self.mediax = None
        self.mediay = None
        self.faixaXEsqMD = None
        self.faixaXDirMD = None
        self.anguloMD = None

        # Variavel Aila
        self.left_current = None
        self.right_current = None
        self.base_currentAila = None

        self.left_baseAux = None
        self.right_currentAux = None
        self.base_currentAuxAila = None

        self.lefty_base = None
        self.righty_base = None

        self.lefty_baseAux = None
        self.righty_baseAux = None

        self.leftyMD = None
        self.rightyMD = None

        self.anguloEsquerda = None
        self.anguloDireita = None

        self.saturation = None
        self.luminosity = None
        self.red = None


    def get_line_markings(self, frame=None, plot=False):

        if frame is None:
            frame = self.orig_frame

        # Convertendo o video em frame de BGR para HLS
        hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)

        _, sxbinary = edge.threshold(hls[:, :, 1], thresh=(self.luminosity, 255))
        sxbinary = edge.blur_gaussian(sxbinary, ksize=3)
        s_channel = hls[:, :, 2]  # Captando apenas o canal de saturação
        _, s_binary = edge.threshold(s_channel, (self.saturation, 255))
        _, r_thresh = edge.threshold(frame[:, :, 2], thresh=(self.red, 255))
        self.rs_binary = cv2.bitwise_and(s_binary, r_thresh)
        self.lane_line_markings = cv2.bitwise_or(self.rs_binary, sxbinary.astype(np.uint8))
        if plot == True:
            cv2.imshow('img', self.lane_line_markings)

    def plot_roi(self, frame=None, plotMD=False, plotAila=False):

        if frame is None:
            frameAuxiliar = self.orig_frame.copy()
            framePrincipal = self.orig_frame.copy()

        # Desenha o ROI para o Principal e o Auxiliar
        imgPrincipal = cv2.polylines(frameAuxiliar, np.int32([
            self.roi_points]), True, (147, 20, 255), 2)

        imgAuxiliar = cv2.polylines(imgPrincipal, np.int32([
            self.roi_pointsAux]), True, (150, 55, 52), 2)

        # Desenhando o ROI da Media Central
        mediaCentral = cv2.polylines(framePrincipal, np.int32([
            self.roi_pointsMD]), True, (255, 13, 0), 3)

        if plotMD == True:
            cv2.imshow('Metodo Media Central', mediaCentral)
        if (plotAila == True):
            cv2.imshow('Metodo Aila', imgAuxiliar)

    def perspective_transform(self, frame=None, plot=False):
        if frame is None:
            frame = self.lane_line_markings

        # Calculate the transformation matrix para pegar os pontos para a vista superior
        self.transformation_matrix = cv2.getPerspectiveTransform(
            self.roi_points, self.desire_roi_points)

        self.transformation_matrixAux = cv2.getPerspectiveTransform(
            self.roi_pointsAux, self.desire_roi_points)

        self.transformation_matrixMD = cv2.getPerspectiveTransform(
            self.roi_pointsMD, self.desire_roi_points
        )

        # Calculate the inverse transformation matrix para voltar a imagem original
        self.inv_transformation_matrix = cv2.getPerspectiveTransform(
            self.desire_roi_points, self.roi_points)

        self.inv_transformation_matrixAux = cv2.getPerspectiveTransform(
            self.desire_roi_points, self.roi_pointsAux)

        self.inv_transformation_matrixMD = cv2.getPerspectiveTransform(
            self.desire_roi_points, self.roi_pointsMD)

        # Perform the transform using the transformation matrix
        self.warped_frame = cv2.warpPerspective(
            frame, self.transformation_matrix, self.orig_image_size, flags=(
                cv2.INTER_LINEAR))

        self.warped_frameAux = cv2.warpPerspective(
            frame, self.transformation_matrixAux, self.orig_image_size, flags=(
                cv2.INTER_LINEAR))

        self.warped_frameMD = cv2.warpPerspective(
            frame, self.transformation_matrixMD, self.orig_image_size, flags=(
                cv2.INTER_LINEAR))

        # Convert image to binary
        (thresh, binary_warped) = cv2.threshold(
            self.warped_frame, 127, 255, cv2.THRESH_BINARY)

        (threshAux, binary_warpedAux) = cv2.threshold(
            self.warped_frameAux, 127, 255, cv2.THRESH_BINARY)

        (threshMD, binary_warpedMD) = cv2.threshold(
            self.warped_frameMD, 127, 255, cv2.THRESH_BINARY)

        self.warped_frame = binary_warped
        self.warped_frameAux = binary_warpedAux
        self.warped_frameMD = binary_warpedMD

        if plot == True:
            principalAuxiliar = cv2.hconcat([self.warped_frame, self.warped_frameAux])
            cv2.imshow('Principal Auxiliar', principalAuxiliar)
            cv2.imshow('Media Central', self.warped_frameMD)

    def calculate_histogram(self, frame=None, plot=False):
        if frame is None:
            frame = self.warped_frame
            frameAux = self.warped_frameAux
            frameMD = self.warped_frameMD

        # Gerando o histograma
        self.histogram = np.sum(frame[int(
            frame.shape[0] / 2):, :], axis=0)

        self.histogramAux = np.sum(frameAux[int(
            frameAux.shape[0] / 2):, :], axis=0)

        self.histogramMD = np.sum(frameMD[int(
            frameMD.shape[0] / 2):, :], axis=0)

        if plot == True:
            figure, (ax1, ax2) = plt.subplots(2, 1)  # 2 row, 1 columns
            figure.set_size_inches(10, 5)
            ax1.imshow(frame, cmap='gray')
            ax1.set_title("Imagem de Cima Principal")
            ax2.plot(self.histogram)
            ax2.set_title("Histograma Principal")

            figureAux, (ax1Aux, ax2Aux) = plt.subplots(2, 1)  # 2 row, 1 columns
            figureAux.set_size_inches(10, 5)
            ax1Aux.imshow(frame, cmap='gray')
            ax1Aux.set_title("Imagem de Cima Auxiliar")
            ax2Aux.plot(self.histogramAux)
            ax2Aux.set_title("Histograma Auxiliar")
            plt.show()
            '''
            figureMD, (ax1MD, ax2MD) = plt.subplots(2, 1)  # 2 row, 1 columns
            figureMD.set_size_inches(10, 5)
            ax1MD.imshow(frame, cmap='gray')
            ax1MD.set_title("Imagem de Cima Media Central")
            ax2MD.plot(self.histogramMD)
            ax2MD.set_title("Histograma Media Central")
            plt.show()
            '''

    def histogram_peak(self):

        # Pegando as posições do Método Aila
        midpoint = int(self.histogram.shape[0] / 2)
        leftx_base = np.argmax(self.histogram[:midpoint])  # Encontra o indice com maior pixel na esquerda no eixo X
        rightx_base = np.argmax(
            self.histogram[midpoint:]) + midpoint  # Encontra o indice com maior pixel da direita no eixo X

        midpointAux = int(self.histogramAux.shape[0] / 2)
        leftx_baseAux = np.argmax(self.histogramAux[:midpointAux])  # Encontra o indice com maior pixel na esquerda no
        rightx_baseAux = np.argmax(
            self.histogramAux[midpointAux:]) + midpointAux  # Encontra o indice com maior pixel da direita no eixo X

        self.lefty_base = self.histogram[leftx_base]
        self.righty_base = self.histogram[rightx_base]

        self.lefty_baseAux = self.histogramAux[leftx_baseAux]
        self.righty_baseAux = self.histogramAux[rightx_baseAux]

        # Pegando as posições pela Media Central
        midpointMD = int(self.histogramMD.shape[0] / 2)
        leftx_baseMD = np.argmax(self.histogramMD[:midpointMD])  # Encontra o indice com maior pixel na esquerda no
        rightx_baseMD = np.argmax(
            self.histogramMD[midpointMD:]) + midpointMD  # Encontra o indice com maior pixel da direita no eixo X

        return (leftx_base, rightx_base, leftx_baseAux, rightx_baseAux, leftx_baseMD, rightx_baseMD)

    def get_lane_line_indices_sliding_windowns(self, plotMD=False, plotAila=False):

        ###Aplicando o Media Central
        margin = self.margin
        frame_sliding_window = self.warped_frameMD.copy()

        # Altura das janelas
        window_height = int(self.warped_frameMD.shape[0] / self.no_of_windows)
        nonzero = self.warped_frameMD.nonzero()  # Pega as coordenadas Y e X dos pixels = a 1 (Branco)
        nonzeroy = np.array(nonzero[0])  # Coordenadas em Y
        nonzerox = np.array(nonzero[1])  # Coordenadas em X

        # Armazena as coordenadas das faixas da Esquerda e Direita
        left_lane_inds = []
        right_lane_inds = []

        # Posição atual das coordenadas dos pixels de cada janela
        # que irão continar atualizando

        posicao = self.histogram_peak()

        # Posição Esquerda e Direita p/ Media Central
        leftx_currentMD = posicao[4]
        rightx_currentMD = posicao[5]
        no_of_windows = self.no_of_windows

        ############# MEDIA CENTRAL ##################
        for window in range(no_of_windows):
            # Identificando os limites de X (direita e esquerda) e Y (Topo e Inferior)
            win_y_low = self.warped_frameMD.shape[0] - (window + 1) * window_height  # warped_frame[0] = 1080 | 972
            win_y_high = self.warped_frameMD.shape[0] - window * window_height  # 1080

            win_xleft_low = leftx_currentMD - margin  # 399
            win_xleft_high = leftx_currentMD + margin  # 719
            win_xright_low = rightx_currentMD - margin  # 1236
            win_xright_high = rightx_currentMD + margin  # 1556
            cv2.rectangle(frame_sliding_window, (win_xleft_low, win_y_low), (
                win_xleft_high, win_y_high), (255, 255, 255), 2)
            cv2.rectangle(frame_sliding_window, (win_xright_low, win_y_low), (
                win_xright_high, win_y_high), (255, 255, 255), 2)
            if window == 2:
                # Acha as coordenadas do circulo
                self.mediax = int(((rightx_currentMD - leftx_currentMD) / 2) +
                                  leftx_currentMD)
                self.mediay = int(((win_y_high - win_y_low) / 2) + win_y_low)

                # Acha as coordenadas das faixas
                self.faixaXEsqMD = int(rightx_currentMD)
                self.faixaXDirMD = int(leftx_currentMD)
                roiXOrigem = int(((self.roi_pointsMD[2][0] - self.roi_pointsMD[1][0]) / 2) + self.roi_pointsMD[1][0])

                self.leftyMD = self.histogramMD[self.faixaXEsqMD]
                self.rightyMD = self.histogramMD[self.faixaXDirMD]

                catOposto = self.mediax - roiXOrigem

                catAdjacente = self.mediay

                self.anguloMD = np.arctan(catOposto / catAdjacente)

            # Limitando os pixels brancos dentro da janela
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xleft_low)
                              & (nonzerox < win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xright_low)
                               & (nonzerox < win_xright_high)).nonzero()[0]

            # Armazenando os pixels bons dentro da janela em uma lista
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)

            # Se encontrar um número de pixels maior que o mínimo recentralizar a posição da próxima janela
            # Andando com a base (midpoint) do eixo X
            minpix = self.minpix
            if (len(good_left_inds) > minpix):
                leftx_currentMD = int(np.mean(nonzerox[good_left_inds]))
            if (len(good_right_inds) > minpix):
                rightx_currentMD = int(np.mean(nonzerox[good_right_inds]))

            if plotMD == True:
                cv2.imshow("Media Central", frame_sliding_window)
        ############# FIM MEDIA CENTRAL ##################

        ############# METODO AILA ##################
        # Posição Esquerda e Direita p/ AILA
        self.left_current = int(posicao[0])
        self.right_current = posicao[1]
        self.base_currentAila = int(self.roi_points[1][1])

        self.left_currentAux = posicao[2]
        self.right_currentAux = posicao[3]
        self.base_currentAuxAila = int(self.roi_pointsAux[1][1])

        catOpostoEsquerda = self.left_current - self.left_currentAux
        catAdjacente = self.base_currentAuxAila - self.base_currentAila
        self.anguloEsquerda = np.arctan((catOpostoEsquerda / catAdjacente))

        catOpostoDireita = self.right_current - self.right_currentAux

        self.anguloDireita = np.arctan((catOpostoDireita / catAdjacente))
        ############# FIM METODO AILA ##################
        return (self.anguloMD, self.anguloEsquerda, self.anguloDireita)

    def plotMediaCentral(self, plot=False):
        if plot == True:
            frame = self.orig_frame.copy()

            warped_frameMD = cv2.warpPerspective(
                frame, self.transformation_matrixMD, self.orig_image_size, flags=(
                    cv2.INTER_LINEAR
                )
            )

            # Pontos de origem
            roiXOrigem = int(((self.roi_points[2][0] - self.roi_points[1][0]) / 2) + self.roi_points[1][0])
            roiYOrigem = int(self.roi_points[1][1])

            # Aplicando os pontos sobre a imagem
            cv2.circle(warped_frameMD, (self.mediax, self.mediay), 5, (0, 255, 229), 2)
            cv2.circle(warped_frameMD, (roiXOrigem, roiYOrigem), 5, (255, 255, 255), 2)
            cv2.circle(warped_frameMD, (roiXOrigem, self.mediay), 5, (255, 255, 255), 2)
            cv2.line(warped_frameMD, (roiXOrigem, roiYOrigem),
                     (roiXOrigem, self.mediay), (255, 255, 255), 2)
            cv2.line(warped_frameMD, (roiXOrigem, self.mediay),
                     (self.mediax, self.mediay), (0, 255, 229), 2)
            cv2.line(warped_frameMD, (roiXOrigem, roiYOrigem),
                     (self.mediax, self.mediay), (0, 255, 229), 2)
            # cv2.ellipse(warped_frameMD, (roiXOrigem,roiYOrigem),
            #            (50,50),self.angulo*100,self.angulo*100,90,(0,255,229),2)

            # Aplicando Vista Perspectiva
            persp = cv2.warpPerspective(warped_frameMD, self.inv_transformation_matrixMD, (
                self.orig_frame.shape[1], self.orig_frame.shape[0]
            ))
            resultado = cv2.addWeighted(frame, 1, persp, 1, 0)

            # cv2.imshow("Media Central Perspectiva",resultado )

            cv2.imshow("Media Central", warped_frameMD)

    def plotAila(self, plot=False):
        frame = self.orig_frame.copy()

        imgPrincipal = cv2.polylines(frame, np.int32([
            self.roi_points]), True, (147, 20, 255), 2)

        imgAuxiliar = cv2.polylines(imgPrincipal, np.int32([
            self.roi_pointsAux]), True, (150, 55, 52), 2)

        # Aplicando os pontos
        # Lado Esquerdo
        cv2.circle(imgAuxiliar, (self.left_current, self.base_currentAila),
                   5, (255, 255, 139), 2)
        cv2.circle(imgAuxiliar, (self.left_current, self.base_currentAuxAila),
                   5, (255, 255, 139), 2)
        cv2.circle(imgAuxiliar, (self.left_currentAux, self.base_currentAuxAila),
                   5, (255, 255, 139), 2)

        # Lado Direito
        cv2.circle(imgAuxiliar, (self.right_current, self.base_currentAila),
                   5, (255, 255, 139), 2)
        cv2.circle(imgAuxiliar, (self.right_current, self.base_currentAuxAila),
                   5, (255, 255, 139), 2)
        cv2.circle(imgAuxiliar, (self.right_currentAux, self.base_currentAuxAila),
                   5, (255, 255, 139), 2)

        if plot == True:
            cv2.imshow("Aila Principal", imgAuxiliar)

    def angulo(self, frame, multi=100):
        multplicador = multi
        '''self.get_line_markings(frame, plot=True)
        self.perspective_transform(plot=False)
        self.calculate_histogram(plot=False)
        self.get_lane_line_indices_sliding_windowns(plotAila=False)
        self.plotMediaCentral(plot=True)
        '''

        if (self.lefty_base <= 55000 and self.lefty_baseAux <= 55000):
            print('Direita')
            if (int(self.anguloDireita * 100)):
                return str(int(self.anguloDireita * multplicador))
            else:
                return f'+{int(self.anguloDireita * multplicador)}'
        elif (self.righty_base <= 55000 and self.righty_baseAux <= 55000):
            print('Esquerda')
            if (int(self.anguloEsquerda * 100 <= -1)):
                return f'{int(self.anguloEsquerda * multplicador)}'
            else:
                return f'+{int(self.anguloEsquerda * multplicador)}'
        else:
            print('Meio')
            if (int(self.anguloMD * 100) <= -1):
                return str(int(self.anguloMD * multplicador))
            else:
                return f'+{(int(self.anguloMD * multplicador))}'

def nothing(x):
    pass

def main():
    vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    #Painel de Gerenciamento
    cv2.namedWindow('Controle')
    cv2.resizeWindow('Controle', 700,512)

    #Controle da Media Central
    cv2.createTrackbar('largTopoMD', 'Controle', 0, 320, nothing)
    cv2.createTrackbar('altMD_Topo', 'Controle', 0, 480, nothing)

    cv2.createTrackbar('largBaseMD', 'Controle', 0, 320, nothing)
    cv2.createTrackbar('altMD_Base', 'Controle', 0, 480, nothing)

    #Controle da Aila
    #Auxiliar
    cv2.createTrackbar('AuxTopo', 'Controle', 0, 480, nothing)
    cv2.createTrackbar('AuxBase', 'Controle', 0, 480, nothing)

    #Principal
    cv2.createTrackbar('AilaTopo', 'Controle', 0, 480, nothing)
    cv2.createTrackbar('AilaBase', 'Controle', 0, 480, nothing)

    #Controle do threshol
    cv2.createTrackbar('saturation', 'Controle', 0, 255, nothing)
    cv2.createTrackbar('luminosity', 'Controle', 0, 255, nothing)
    cv2.createTrackbar('red', 'Controle', 0, 255, nothing)


    #SWITCH
    cv2.createTrackbar('Lane Mark', 'Controle', 0, 1, nothing)


    if vid.isOpened():
        while True:
            ret, frame = vid.read()
            lane = Lane(orig_frame=frame)

            #SLIDER
            #ROI
            largBaseMD_L = 320 - cv2.getTrackbarPos('largBaseMD', 'Controle')
            largBaseMD_R = 320 + cv2.getTrackbarPos('largBaseMD', 'Controle')

            largTopoMD_L = 320 - cv2.getTrackbarPos('largTopoMD', 'Controle')
            largTopoMD_R = 320 + cv2.getTrackbarPos('largTopoMD', 'Controle')

            alturaMD_Base = 480 - cv2.getTrackbarPos('altMD_Base', 'Controle')
            alturaMD_Topo = 480 - cv2.getTrackbarPos('altMD_Topo', 'Controle')

            alturaAilaTopo = 480 - cv2.getTrackbarPos('AilaTopo', 'Controle')
            alturaAilaBase = 480 - cv2.getTrackbarPos('AilaBase', 'Controle') + alturaAilaTopo

            alturaAilaAuxTopo = 480 - cv2.getTrackbarPos('AuxTopo', 'Controle')
            alturaAilaAuxBase = 480 - cv2.getTrackbarPos('AuxBase', 'Controle') + alturaAilaAuxTopo

            print(alturaAilaTopo)
            #THRESHOL
            lane.saturation = cv2.getTrackbarPos('saturation', 'Controle')
            lane.luminosity = cv2.getTrackbarPos('luminosity', 'Controle')
            lane.red = cv2.getTrackbarPos('red', 'Controle')

            print('='*50)
            print('SATURAÇÃO')
            print('='*50)
            print(f'Luminosity: {lane.luminosity}')
            print(f'Saturação: {lane.saturation}')
            print(f'Red: {lane.red}')

            #SWITCH
            getLine = cv2.getTrackbarPos('Lane Mark', 'Controle')



            #Controle da Média Central
            lane.roi_pointsMD[1][0] = largBaseMD_L
            lane.roi_pointsMD[2][0] = largBaseMD_R

            lane.roi_pointsMD[0][0] = largTopoMD_L
            lane.roi_pointsMD[3][0] = largTopoMD_R

            lane.roi_pointsMD[1][1] = alturaMD_Base
            lane.roi_pointsMD[2][1] = alturaMD_Base

            lane.roi_pointsMD[0][1] = alturaMD_Topo
            lane.roi_pointsMD[3][1] = alturaMD_Topo

            print('='*50)
            print('MEDIA CENTRAL')
            print('='*50)
            print(
                f'''
                    ({largTopoMD_L}, {alturaMD_Topo}),
                    ({largBaseMD_L}, {alturaMD_Base}),
                    ({largBaseMD_R}, {alturaMD_Base}),
                    ({largTopoMD_R}, {alturaMD_Topo})
                '''
            )

            #Controle da Aila
            #Principal
            lane.roi_points[1][1] = alturaAilaBase
            lane.roi_points[2][1] = alturaAilaBase

            lane.roi_points[0][1] = alturaAilaTopo
            lane.roi_points[3][1] = alturaAilaTopo



            print('=' * 50)
            print('AILA BASE PRINCIPAL')
            print('=' * 50)
            print(
                f'''
                    ({0}, {alturaAilaTopo}),
                    ({0}, {alturaAilaBase}),
                    ({640}, {alturaAilaBase}),
                    ({640}, {alturaAilaTopo})
                '''
            )

            #Auxiliar
            lane.roi_pointsAux[1][1] = alturaAilaAuxBase
            lane.roi_pointsAux[2][1] = alturaAilaAuxBase

            lane.roi_pointsAux[0][1] = alturaAilaAuxTopo
            lane.roi_pointsAux[3][1] = alturaAilaAuxTopo

            print('=' * 50)
            print('AILA BASE AUXILIAR')
            print('=' * 50)
            print(
                f'''
                    ({0}, {alturaAilaAuxTopo}),
                    ({0}, {alturaAilaAuxBase}),
                    ({640}, {alturaAilaAuxBase}),
                    ({640}, {alturaAilaAuxTopo})
                '''
            )



            lane.get_line_markings(frame, plot=getLine)
            lane.plot_roi(plotMD=False, plotAila=False)
            lane.perspective_transform(plot=False)
            lane.calculate_histogram(plot=False)
            lane.get_lane_line_indices_sliding_windowns(plotAila=False)
            lane.plotMediaCentral(plot=True)
            lane.plotAila(plot=True)
            #print(lane.angulo(frame, multi=300))
            if (cv2.waitKey(1) & 0xFF == ord('q')):
                break


main()
