import time

import cv2
import numpy as np  # Import the NumPy scientific computing library
import Edge_detection as edge  # Handles the detection of lane lines
import matplotlib.pyplot as plt  # Used for plotting and error checking

# Variaveis Globais
prev_leftx = None
prev_lefty = None
prev_rightx = None
prev_righty = None
prev_left_fit = []
prev_right_fit = []

prev_leftx2 = None
prev_lefty2 = None
prev_rightx2 = None
prev_righty2 = None
prev_left_fit2 = []
prev_right_fit2 = []


class Lane:

    def __init__(self, orig_frame):

        # Isolando apenas a faixa
        self.orig_frame = orig_frame
        self.rsbinary = None
        self.lane_line_markings = None

        # Transformações das perspectivas
        self.warped_frame = None
        self.transformation_matrix = None
        self.inv_transformaiton_matrix = None

        # Altura e largura do video
        self.orig_image_size = self.orig_frame.shape[::-1][1:]

        # Centro das faixas
        self.mediax = None
        self.mediay = None
        self.faixaXEsq = None
        self.faixaXDir = None

        # ANGULO
        self.angulo = None

        width = self.orig_image_size[0]  # 640
        height = self.orig_image_size[1]  # 480
        self.width = width
        self.height = height
        # Os pontos de região de interesse
        self.roi_points = np.float32([
            (140, 300),  # Top-left
            (0, 480),  # Bottom-left
            (640, 480),  # Borron-right
            (500, 300)  # Top-right
        ])

        self.center_lane = None

        # Posição desejada através da região de interesse
        # Após a transformação de perspectiva a nova imagem terá 600px de largura, com padding de 150
        self.padding = int(0.25 * width)
        self.desire_roi_points = np.float32([
            [self.padding, 0],  # Top-left corner
            [self.padding, self.orig_image_size[1]],  # Bottom-left corner
            [self.orig_image_size[0] - self.padding, self.orig_image_size[1]],  # Bottom-right corner
            [self.orig_image_size[0] - self.padding, 0]  # Top-right corner
        ])

        # Histograma mostrará o branco das faixas
        self.histogram = None

        # Janelas deslizantes
        self.no_of_windows = 10
        self.margin = int((1 / 12) * width)  # Margem da largura da janela. Quanto menor o número mais largo a janela
        self.minpix = int((1 / 24) * width)  # Centraliza a próxima janela através da média pelo min de pixels

        # Curvas polinominais para a faixa da direita e da esquerda
        self.left_fit = None
        self.right_fit = None
        self.left_Lane_inds = None
        self.right_Lane_inds = None
        self.ploty = None
        self.left_fitx = None
        self.right_fitx = None
        self.leftx = None
        self.rightx = None
        self.lefty = None
        self.righty = None

        # Pixel parâmetro de X e Y dimensões
        self.YM_PER_PIX = 7.0 / 400  # Metro por pixel em Y
        self.XM_PER_PIX = 3.7 / 255  # Metro por pixel em X

        # Raio da curva e offset
        self.left_curvem = None
        self.right_curvem = None
        self.center_offset = None

    def get_line_markings(self, frame=None, plot=False):

        if frame is None:
            frame = self.orig_frame

        # Convertendo o video em frame de BGR para HLS
        hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)

        # Isolando as faixas
        # Aplicando o algoritmo de sobel no canal de luminosidade ao longo dos eixos X e Y
        _, sxbinary = edge.threshold(hls[:, :, 1], thresh=(170, 255))
        sxbinary = edge.blur_gaussian(sxbinary, ksize=3)

        # sxbinary = edge.mag_thresh(sxbinary, sobel_kernel=3, thresh=(80, 255))

        # Aplicando o threshold no canal de saturação, pois quanto maior o seu valor mais pura a cor será
        s_channel = hls[:, :, 2]  # Captando apenas o canal de saturação
        _, s_binary = edge.threshold(s_channel, (160, 255))

        # Aplicando threshold no canal vermelho do frame, isso fará como que faça a captação da cor amarela
        # também, o branco no BGR é (255,255,255), o amarelo é (0,255,255), então se zerarmos o vermelho conseuimos
        # o amarelo.
        _, r_thresh = edge.threshold(frame[:, :, 2], thresh=(150, 255))

        # As faixas devem ser de cores puras com um alto valor de vermelho
        # A operação BITWISE AND reduz os pixels que não parecem bons
        self.rs_binary = cv2.bitwise_and(s_binary, r_thresh)

        # Combinando as possíveis faixas com possíveis bordas das faixas
        self.lane_line_markings = cv2.bitwise_or(self.rs_binary, sxbinary.astype(np.uint8))
        if plot == True:
            cv2.imshow('img', self.lane_line_markings)
        # cv2.waitKey()
        # cv2.destroyAllWindows()

    def plot_roi(self, frame=None, plot=False):

        if frame is None:
            frame = self.orig_frame.copy()

        # Desenha o trapézio no frame
        this_image = cv2.polylines(frame, np.int32([
            self.roi_points]), True, (147, 20, 255), 3)

        if plot == True:
            cv2.imshow('img', this_image)
        # cv2.waitKey()
        # cv2.destroyAllWindows()

    def perspective_transform(self, frame=None, plot=False):
        if frame is None:
            frame = self.lane_line_markings

        # Calculate the transformation matrix para pegar os pontos para a vista superior
        self.transformation_matrix = cv2.getPerspectiveTransform(
            self.roi_points, self.desire_roi_points)
        # Calculate the inverse transformation matrix para voltar a imagem original
        self.inv_transformation_matrix = cv2.getPerspectiveTransform(
            self.desire_roi_points, self.roi_points)

        # Perform the transform using the transformation matrix
        self.warped_frame = cv2.warpPerspective(
            frame, self.transformation_matrix, self.orig_image_size, flags=(
                cv2.INTER_LINEAR))
        # Convert image to binary
        (thresh, binary_warped) = cv2.threshold(
            self.warped_frame, 127, 255, cv2.THRESH_BINARY)
        self.warped_frame = binary_warped
        if plot == True:
            cv2.imshow('img', self.warped_frame)
        # cv2.waitKey()
        # cv2.destroyAllWindows()
        # Display the perspective transformed (i.e. warped) frame
        return self.warped_frame

    def calculate_histogram(self, frame=None, plot=False):
        # Calculando o histograma
        if frame is None:
            frame = self.warped_frame

        # Gerando o histograma
        self.histogram = np.sum(frame[int(
            frame.shape[0] / 2):, :], axis=0)

        if plot == True:
            # Draw both the image and the histogram

            figure, (ax1, ax2) = plt.subplots(2, 1)  # 2 row, 1 columns
            figure.set_size_inches(10, 5)
            ax1.imshow(frame, cmap='gray')
            ax1.set_title("Warped Binary Frame")
            ax2.plot(self.histogram)
            ax2.set_title("Histogram Peaks")
            plt.show()
        return self.histogram

    def histogram_peak(self):
        # Pega a esquerda e direita do histograma
        # Retorna a coordenada X da esquerda e direita do histograma
        # Pega os picos da esquerda e direita
        midpoint = int(self.histogram.shape[0] / 2)
        leftx_base = np.argmax(self.histogram[:midpoint])  # Encontra o indice com maior pixel na esquerda no eixo X
        rightx_base = np.argmax(
            self.histogram[midpoint:]) + midpoint  # Encontra o indice com maior pixel da direita no eixo X

        return (leftx_base, rightx_base)

    def get_lane_line_indices_sliding_windows(self, plot=False):
        # Pegando as faixas da direita e esquerda

        # Largura da janela
        margin = self.margin

        frame_sliding_window = self.warped_frame.copy()

        # Configurando a altura da janela
        window_height = int(self.warped_frame.shape[0] / self.no_of_windows)

        # Encontrando o X e Y das coordenadas nonzero
        nonzero = self.warped_frame.nonzero()  # Pega as coordenadas Y e X dos pixels = a 1 (Branco)
        nonzeroy = np.array(nonzero[0])  # Coordenadas em Y
        nonzerox = np.array(nonzero[1])  # Coordenadas em X
        # Armazena as coordenadas das faixas da esquerda e da direita
        left_lane_inds = []
        right_lane_inds = []

        # Posição atual das coordenadas dos pixel de cada janela
        # que irão continuar atualizando
        leftx_base, rightx_base = self.histogram_peak()
        leftx_current = leftx_base
        rightx_current = rightx_base
        no_of_windows = self.no_of_windows

        for window in range(no_of_windows):
            # Identificando os limites de X (direita e esquerda) e Y (Topo e Inferior)
            win_y_low = self.warped_frame.shape[0] - (window + 1) * window_height  # warped_frame[0] = 1080 | 972
            win_y_high = self.warped_frame.shape[0] - window * window_height  # 1080

            win_xleft_low = leftx_current - margin  # 399
            win_xleft_high = leftx_current + margin  # 719
            win_xright_low = rightx_current - margin  # 1236
            win_xright_high = rightx_current + margin  # 1556
            cv2.rectangle(frame_sliding_window, (win_xleft_low, win_y_low), (
                win_xleft_high, win_y_high), (255, 255, 255), 2)
            cv2.rectangle(frame_sliding_window, (win_xright_low, win_y_low), (
                win_xright_high, win_y_high), (255, 255, 255), 2)
            if window == 5:
                # Acha as coordenadas do circulo
                self.mediax = int(((rightx_current - leftx_current) / 2) +
                                  leftx_current)
                self.mediay = int(((win_y_high - win_y_low) / 2) + win_y_low)

                # Acha as coordenadas das faixas
                self.faixaXEsq = int(rightx_current)
                self.faixaXDir = int(leftx_current)

            # Identificando os indices dos pixels diferente de 0 em X e Y dentro da janela
            # As condições são referentes aos quatro cantos da janela
            # Aqui fala se aquele pixel branco está ou não dentro da janela, armazena True ou False
            # Depois aplica o filtro nonzero() que pega apenas os indices dos pixels verdadeiros
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
                leftx_current = int(np.mean(nonzerox[good_left_inds]))
            if (len(good_right_inds) > minpix):
                rightx_current = int(np.mean(nonzerox[good_right_inds]))

        # Concatenando os indices da lista
        # Nesta lista contem todas as posições dos pixels pertencentes a faixa
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
        # Extraindo as coordenadas das faixas da esquerda e da direita
        # A posição da lista é a mesma para os dois, um esta no eixo X e outro no eixo Y
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]

        # Ajustando as curvas polinomiais de 2°ordem aos pixels
        left_fit = None
        right_fit = None

        global prev_leftx
        global prev_lefty
        global prev_rightx
        global prev_righty
        global prev_left_fit
        global prev_right_fit

        # Tendo certeza que tenhamos nonzero pixels
        if len(leftx) == 0 or len(lefty) == 0 or len(rightx) == 0 or len(righty) == 0:
            leftx = prev_leftx
            lefty = prev_lefty
            rightx = prev_rightx
            righty = prev_righty

        # Adicionando os coeficientes polinomiais
        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)

        prev_left_fit.append(left_fit)
        prev_right_fit.append(right_fit)

        # Calculando a média movel
        if (len(prev_left_fit) > 10):
            prev_left_fit.pop(0)
            prev_right_fit.pop(0)
            left_fit = sum(prev_left_fit) / len(prev_left_fit)
            right_fit = sum(prev_right_fit) / len(prev_right_fit)

        self.left_fit = left_fit
        self.right_fit = right_fit

        prev_leftx = leftx
        prev_lefty = lefty
        prev_rightx = rightx
        prev_righty = righty
        if plot == True:
            ploty = np.linspace(
                0, frame_sliding_window.shape[0] - 1, frame_sliding_window.shape[0])
            left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
            right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]

            # Generate an image to visualize the result
            out_img = np.dstack((
                frame_sliding_window, frame_sliding_window, (
                    frame_sliding_window))) * 255

            # Add color to the left line pixels and right line pixels
            out_img[nonzeroy[left_lane_inds], nonzerox[left_lane_inds]] = [255, 0, 0]
            out_img[nonzeroy[right_lane_inds], nonzerox[right_lane_inds]] = [
                0, 0, 255]

            # Plot the figure with the sliding windows
            figure, (ax1, ax2, ax3) = plt.subplots(3, 1)  # 3 rows, 1 column
            figure.set_size_inches(10, 10)
            figure.tight_layout(pad=3.0)
            ax1.imshow(cv2.cvtColor(self.orig_frame, cv2.COLOR_BGR2RGB))
            ax2.imshow(frame_sliding_window, cmap='gray')
            ax3.imshow(out_img)
            ax3.plot(left_fitx, ploty, color='yellow')
            ax3.plot(right_fitx, ploty, color='yellow')
            ax1.set_title("Original Frame")
            ax2.set_title("Warped Frame with Sliding Windows")
            ax3.set_title("Detected Lane Lines with Sliding Windows")
            plt.show()

        return self.left_fit, self.right_fit

    def get_lane_line_previous_window(self, left_fit, right_fit, plot=False):

        # Pegando os parâmetros para preencher o meio entre as faixas

        margin = self.margin

        # Encontrando as coordenadas X e Y dos pixels brancos
        nonzero = self.warped_frame.nonzero()  # Lista com Y e X dos pixels
        nonzeroy = np.array(nonzero[0])  # Coordenadas Y
        nonzerox = np.array(nonzero[1])  # Coordenadas X

        # Armazenando os pixels pertencentes as faixas da direita e esquerda
        left_lane_inds = (
                    (nonzerox > (left_fit[0] * (nonzeroy ** 2) + left_fit[1] * nonzeroy + left_fit[2] - margin)) & (
                    nonzerox < (left_fit[0] * (nonzeroy ** 2) + left_fit[1] * nonzeroy + left_fit[2] + margin)))

        right_lane_inds = (
                    (nonzerox > (right_fit[0] * (nonzeroy ** 2) + right_fit[1] * nonzeroy + right_fit[2] - margin)) & (
                    nonzerox < (right_fit[0] * (nonzeroy ** 2) + right_fit[1] * nonzeroy + right_fit[2] + margin)))

        self.left_Lane_inds = left_lane_inds
        self.right_Lane_inds = right_lane_inds

        # Pegando as localizações dos pixels das faixas da direita e da esquerda
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]

        global prev_leftx2
        global prev_lefty2
        global prev_rightx2
        global prev_righty2
        global prev_left_fit2
        global prev_right_fit2

        # Make sure we have nonzero pixels
        if len(leftx) == 0 or len(lefty) == 0 or len(rightx) == 0 or len(righty) == 0:
            leftx = prev_leftx2
            lefty = prev_lefty2
            rightx = prev_rightx2
            righty = prev_righty2

        self.leftx = leftx
        self.rightx = rightx
        self.lefty = lefty
        self.righty = righty

        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)

        # Add the latest polynomial coefficients
        prev_left_fit2.append(left_fit)
        prev_right_fit2.append(right_fit)

        # Calculate the moving average
        if len(prev_left_fit2) > 10:
            prev_left_fit2.pop(0)
            prev_right_fit2.pop(0)
            left_fit = sum(prev_left_fit2) / len(prev_left_fit2)
            right_fit = sum(prev_right_fit2) / len(prev_right_fit2)

        self.left_fit = left_fit
        self.right_fit = right_fit
        prev_leftx2 = leftx
        prev_lefty2 = lefty
        prev_rightx2 = rightx
        prev_righty2 = righty

        # Calculate the moving average
        if len(prev_left_fit2) > 10:
            prev_left_fit2.pop(0)
            prev_right_fit2.pop(0)
            left_fit = sum(prev_left_fit2) / len(prev_left_fit2)
            right_fit = sum(prev_right_fit2) / len(prev_right_fit2)

        self.left_fit = left_fit
        self.right_fit = right_fit

        prev_leftx2 = leftx
        prev_lefty2 = lefty
        prev_rightx2 = rightx
        prev_righty2 = righty

        # Create the x and y values to plot on the image
        ploty = np.linspace(
            0, self.warped_frame.shape[0] - 1, self.warped_frame.shape[0])
        left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
        right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]
        self.ploty = ploty
        self.left_fitx = left_fitx
        self.right_fitx = right_fitx

        if plot == True:
            # Generate images to draw on
            out_img = np.dstack((self.warped_frame, self.warped_frame, (
                self.warped_frame))) * 255
            window_img = np.zeros_like(out_img)

            # Add color to the left and right line pixels
            out_img[nonzeroy[left_lane_inds], nonzerox[left_lane_inds]] = [255, 0, 0]
            out_img[nonzeroy[right_lane_inds], nonzerox[right_lane_inds]] = [
                0, 0, 255]
            # Create a polygon to show the search window area, and recast
            # the x and y points into a usable format for cv2.fillPoly()
            margin = self.margin
            left_line_window1 = np.array([np.transpose(np.vstack([
                left_fitx - margin, ploty]))])
            left_line_window2 = np.array([np.flipud(np.transpose(np.vstack([
                left_fitx + margin, ploty])))])
            left_line_pts = np.hstack((left_line_window1, left_line_window2))
            right_line_window1 = np.array([np.transpose(np.vstack([
                right_fitx - margin, ploty]))])
            right_line_window2 = np.array([np.flipud(np.transpose(np.vstack([
                right_fitx + margin, ploty])))])
            right_line_pts = np.hstack((right_line_window1, right_line_window2))

            # Draw the lane onto the warped blank image
            cv2.fillPoly(window_img, np.int_([left_line_pts]), (0, 255, 0))
            cv2.fillPoly(window_img, np.int_([right_line_pts]), (0, 255, 0))
            result = cv2.addWeighted(out_img, 1, window_img, 0.3, 0)

            # Plot the figures
            figure, (ax1, ax2, ax3) = plt.subplots(3, 1)  # 3 rows, 1 column
            figure.set_size_inches(10, 10)
            figure.tight_layout(pad=3.0)
            ax1.imshow(cv2.cvtColor(self.orig_frame, cv2.COLOR_BGR2RGB))
            ax2.imshow(self.warped_frame, cmap='gray')
            ax3.imshow(result)
            ax3.plot(left_fitx, ploty, color='yellow')
            ax3.plot(right_fitx, ploty, color='yellow')
            ax1.set_title("Original Frame")
            ax2.set_title("Warped Frame")
            ax3.set_title("Warped Frame With Search Window")
            plt.show()

    def overlay_lane_lines(self, plot=False, plot_Superior=False):

        meioX = int((self.roi_points[2][0]) / 2)
        meioYBaixo = int((self.roi_points[2][0] / 2))
        meioYTopo = int((self.roi_points[0][1]))
        roiXOrigem = int(((self.roi_points[2][0] - self.roi_points[1][0]) / 2) + self.roi_points[1][0])
        roiYOrigem = int(self.roi_points[1][1])

        # Desenha as linhas sobre a imagem
        # Gera uma imagem para desenhar por cima
        warp_zero = np.zeros_like(self.warped_frame).astype(np.uint8)
        color_warp = np.dstack((warp_zero, warp_zero, warp_zero))  # Cria 3 camadas

        # Reformulando os ponto de X e Y para aplicar no cv2.fillPoly()
        pts_left = np.array([np.transpose(np.vstack([self.left_fitx, self.ploty]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([self.right_fitx, self.ploty])))])
        pts = np.hstack((pts_left, pts_right))

        # Desenhando a lina pela imagem preta vazia
        cv2.fillPoly(color_warp, np.int_([pts]), (0, 255, 0))

        # Desenhando a media central

        cv2.circle(color_warp, (self.mediax, self.mediay), 10,
                   (255, 0, 0), 3)
        cv2.line(color_warp, (self.faixaXEsq, self.mediay),
                 (self.faixaXDir, self.mediay), (194, 95, 151), 3)
        # Circulo reto
        cv2.circle(color_warp, (roiXOrigem, self.mediay), 10, (230, 25, 100), 3)

        # Desenhando o ponto de origem e o perpendicular em função da vista
        # superior
        # Ponto Perpendicular
        cv2.line(color_warp, (roiXOrigem, roiYOrigem), (roiXOrigem, self.mediay), (255, 255, 0), 3)

        # Origem do circulo
        cv2.circle(color_warp, (roiXOrigem, roiYOrigem), 5, (255, 255), 3)

        # Desenhando a hipotenusa
        cv2.line(color_warp, (roiXOrigem, roiYOrigem), (self.mediax, self.mediay), (255, 50, 60), 3)

        # Calculando o cateto adjacente e o oposto
        catOposto = self.mediax - roiXOrigem
        catAdjacente = self.mediay

        self.angulo = np.arctan(catOposto / catAdjacente)

        if plot_Superior == True:
            cv2.imshow("Janele", color_warp)

        # Voltando da imagem deformada para original
        newwarp = cv2.warpPerspective(color_warp, self.inv_transformation_matrix, (
            self.orig_frame.shape[
                1], self.orig_frame.shape[0]))

        # Combinando os resultaodos como a imagem original

        result = cv2.addWeighted(self.orig_frame, 1, newwarp, 0.3, 0)

        ############################Teste############################
        # Desenha o ponto de origem no modo de perspectiva
        # cv2.line(result, (340, 400), (340, 200), (255, 255, 0), 3)
        # cv2.circle(result, (340, 400), 5, (255, 255), 3)
        #############################################################
        cv2.putText(result, 'Curve Radius: ' + str((self.left_curvem + self.right_curvem) / 2)[:7] + ' m',
                    (int((5 / 600) * self.width), int((20 / 338) * self.height)),
                    cv2.FONT_HERSHEY_SIMPLEX, (float((0.5 / 600) * self.width)), (
                        255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(result, 'Center Offset: ' + str(self.center_offset)[:7] + ' cm',
                    (int((5 / 600) * self.width), int((40 / 338) * self.height)),
                    cv2.FONT_HERSHEY_SIMPLEX, (float((0.5 / 600) * self.width)), (
                        255, 255, 255), 2, cv2.LINE_AA)
        cv2.polylines(result, np.int32([
            self.roi_points]), True, (147, 20, 255), 3)
        if plot == True:
            # Plot the figures
            cv2.imshow("Janela", cv2.cvtColor(result, cv2.COLOR_BGR2RGB))

        return result

    def calculate_curvature(self, print_terminal=False):

        # Calculando a curvatura da rua em metros
        # Retorna o raio da curva

        # Configura o y-value onde nós queremos calculara o raio da curva
        # Seleciona o maximo de y-value, que é o fundo do frame

        y_eval = np.max(self.ploty)

        # Encaixa a curva polinomial para o mundo real
        left_fit_cr = np.polyfit(self.lefty * self.YM_PER_PIX, self.leftx * (self.XM_PER_PIX), 2)
        right_fit_cr = np.polyfit(self.righty * self.YM_PER_PIX, self.rightx * (self.XM_PER_PIX), 2)

        # Calculando o raio da curvatura
        left_curvem = ((1 + (2 * left_fit_cr[0] * y_eval * self.YM_PER_PIX + left_fit_cr[
            1]) ** 2) ** 1.5) / np.absolute(2 * left_fit_cr[0])
        right_curvem = ((1 + (2 * right_fit_cr[
            0] * y_eval * self.YM_PER_PIX + right_fit_cr[
                                  1]) ** 2) ** 1.5) / np.absolute(2 * right_fit_cr[0])
        if print_terminal == True:
            print(left_curvem, 'm', right_curvem, 'm')

        self.left_curvem = left_curvem
        self.right_curvem = right_curvem
        return left_curvem, right_curvem

    def calculate_car_position(self, print_terminal=False):

        # Calculando o offset do centro

        # Assuminodo que a câmera está centralizada
        # Pegando a posição do carro em centimetros
        car_location = self.orig_frame.shape[1] / 2

        # Encontrando a coordenada X da linha de fundo
        height = self.orig_frame.shape[0]
        bottom_left = self.left_fit[0] ** height ** 2 + self.left_fit[1] * height + self.left_fit[2]
        bottom_right = self.right_fit[0] * height ** 2 + self.right_fit[1] * height + self.right_fit[2]

        # print(bottom_right, bottom_left)
        self.center_lane = (bottom_right - bottom_left) / 2 + bottom_left
        center_offset = (np.abs(car_location) - np.abs(self.center_lane)) * self.XM_PER_PIX * 100

        if print_terminal == True:
            print(f"Centro Offset: {str(center_offset)} cm")

        self.center_offset = center_offset
        return center_offset

    def display_curvature_offset(self, frame, plot=False):

        # Mostra a curvatura e o seu offset para estar centralizado

        image_copy = None
        if frame is None:
            image_copy = self.orig_frame.copy()
        else:
            image_copy = frame

        cv2.putText(image_copy, 'Curve Radius: ' + str((self.left_curvem + self.right_curvem) / 2)[:7] + ' m',
                    (int((5 / 600) * self.width), int((20 / 338) * self.height)),
                    cv2.FONT_HERSHEY_SIMPLEX, (float((0.5 / 600) * self.width)), (
                        255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image_copy, 'Center Offset: ' + str(self.center_offset)[:7] + ' cm',
                    (int((5 / 600) * self.width), int((40 / 338) * self.height)),
                    cv2.FONT_HERSHEY_SIMPLEX, (float((0.5 / 600) * self.width)), (
                        255, 255, 255), 2, cv2.LINE_AA)

        if plot == True:
            cv2.imshow("Image with Curvature and Offset", image_copy)
            cv2.waitKey()
            cv2.destroyAllWindows()

        return image_copy


def main():
    vid = cv2.VideoCapture(0)  # 640x480
    if vid.isOpened():
        while True:
            ret, frame = vid.read()
            cv2.imshow("Janela 1", frame)
            time.sleep(2)
            cv2.destroyAllWindows()
            break
        while True:
            # time.sleep(0.01)
            ret, frame = vid.read()
            img = cv2.resize(frame, (640, 480))

            ret2, frame2 = vid.read()

            lane_obj = Lane(orig_frame=img)
            lane_obj.get_line_markings(frame, plot=False)

            # Transformando em vista superior
            lane_obj.perspective_transform(plot=False)
            # lane_obj.plot_roi(frame, plot=False)
            # Calculando o histograma
            lane_obj.calculate_histogram(plot=False)

            # Exemplo da pegagem do histograma
            # lane_obj.histogram_peak()

            left_fit, right_fit = lane_obj.get_lane_line_indices_sliding_windows(
                plot=True)
            lane_obj.get_lane_line_previous_window(left_fit, right_fit, plot=False)
            # frame_with_lane_lines = lane_obj.overlay_lane_lines(True)
            lane_obj.plot_roi(frame, False)
            lane_obj.calculate_curvature(False)
            lane_obj.calculate_car_position(print_terminal=False)
            # lane_obj.display_curvature_offset(frame, True)
            lane_obj.overlay_lane_lines(True, True)

            # ANGULO PARA O SERVO MOTOR
            print(lane_obj.angulo)

            if (cv2.waitKey(1) & 0xFF == ord('q')):
                break


main()
