import cv2
import numpy as np  # Import the NumPy scientific computing library
import Edge_detection as edge  # Handles the detection of lane lines
import matplotlib.pyplot as plt  # Used for plotting and error checking

filename = './Data/Video/Lane/Pista_13.mp4'
img = 'Data/Image/Lane/Pista030.png'

file_size = (1920,1080)
scale_ratio = 1
output_file = 'Pista-13_Output.mp4'
output_frames_per_second = 20.0
imagem = cv2.imread(img)

#Variaveis Globais
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

        #Isolando apenas a faixa
        self.orig_frame = orig_frame
        self.rsbinary = None
        self.lane_line_markings = None

        #Transformações das perspectivas
        self.warped_frame = None
        self.transformation_matrix = None
        self.inv_transformaiton_matrix = None

        #Altura e largura do video
        self.orig_image_size = self.orig_frame.shape[::-1][1:]

        width = self.orig_image_size[0] #1920
        height = self.orig_image_size[1] #1080
        self.width = width
        self.height = height
        #Os pontos de região de interesse
        self.roi_points = np.float32([
            (100, 292),  # Top-left
            (0, 1078),  # Bottom-left
            (1918, 1078),  # Borron-right
            (1818, 292)  # Top-right
        ])

        #Posição desejada através da região de interesse
        #Após a transformação de perspectiva a nova imagem terá 600px de largura, com padding de 150
        self.padding = int(0.25*width)
        self.desire_roi_points = np.float32([
            [self.padding, 0],  # Top-left corner
            [self.padding, self.orig_image_size[1]],  # Bottom-left corner
            [self.orig_image_size[0] - self.padding, self.orig_image_size[1]],  # Bottom-right corner
            [self.orig_image_size[0] - self.padding, 0]  # Top-right corner
        ])

        #Histograma mostrará o branco das faixas
        self.histogram = None

        #Janelas deslizantes
        self.no_of_windows = 10
        self.margin = int((1/12)*width) #Margem da largura da janela. Quanto menor o número mais largo a janela
        self.minpix = int((1/24)*width) #Centraliza a próxima janela através da média pelo min de pixels

        #Curvas polinominais para a faixa da direita e da esquerda
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

        #Pixel parâmetro de X e Y dimensões
        self.YM_PER_PIX = 7.0/400 #Metro por pixel em Y
        self.XM_PER_PIX = 3.7/255 #Metro por pixel em X

        #Raio da curva e offset
        self.left_curvem = None
        self.right_curvem = None
        self.center_offset = None

    def get_line_markings(self, frame = None):

        if frame is None:
            frame = self.orig_frame

        #Convertendo o video em frame de BGR para HLS
        hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)

        # Isolando as faixas
        #Aplicando o algoritmo de sobel no canal de luminosidade ao longo dos eixos X e Y
        _, sxbinary = edge.threshold(hls[:,:,1], thresh=(150,255))
        sxbinary = edge.blur_gaussian(sxbinary, ksize=3)

        #Aplicando o threshold no canal de saturação, pois quanto maior o seu valor mais pura a cor será
        s_channel = hls[:,:,2] #Captando apenas o canal de saturação
        _, s_binary = edge.threshold(s_channel,(130,255))

        #Aplicando threshold no canal vermelho do frame, isso fará como que faça a captação da cor amarela
        #também, o branco no BGR é (255,255,255), o amarelo é (0,255,255), então se zerarmos o vermelho conseuimos
        #o amarelo.
        _,r_thresh = edge.threshold(frame[:,:,2], thresh=(150,255))

        #As faixas devem ser de cores puras com um alto valor de vermelho
        #A operação BITWISE AND reduz os pixels que não parecem bons
        self.rs_binary = cv2.bitwise_and(s_binary, r_thresh)

        #Combinando as possíveis faixas com possíveis bordas das faixas
        self.lane_line_markings = cv2.bitwise_or(self.rs_binary, sxbinary.astype(np.uint8))

        #cv2.imshow('img',self.lane_line_markings)
        #cv2.waitKey()
        #cv2.destroyAllWindows()

    def plot_roi(self, frame = None):

        if frame is None:
            frame = self.orig_frame.copy()

        #Desenha o trapézio no frame
        this_image = cv2.polylines(frame, np.int32([
            self.roi_points]), True, (147,20,255),3)

        #cv2.imshow('img', this_image)
        #cv2.waitKey()
        #cv2.destroyAllWindows()

    def perspective_transform(self, frame = None, plot=False):
        if frame is None:
            frame = self.lane_line_markings#self.rs_binary

            # Calculate the transformation matrix para pegar os pontos para a vista superior
        self.transformation_matrix = cv2.getPerspectiveTransform(
            self.roi_points, self.desire_roi_points)
        #print(self.roi_points)
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
        #cv2.imshow('img', self.warped_frame)
        #cv2.waitKey()
        #cv2.destroyAllWindows()
        # Display the perspective transformed (i.e. warped) frame
        return self.warped_frame

    def calculate_histogram(self, frame = None):
        #Calculando o histograma
        if frame is None:
            frame = self.warped_frame

        #Gerando o histograma
        self.histogram = np.sum(frame[int(
            frame.shape[0]/2):,:], axis=0)

        # Draw both the image and the histogram
        #figure, (ax1, ax2) = plt.subplots(2, 1)  # 2 row, 1 columns
        #figure.set_size_inches(10, 5)
        #ax1.imshow(frame, cmap='gray')
        #ax1.set_title("Warped Binary Frame")
        #ax2.plot(self.histogram)
        #ax2.set_title("Histogram Peaks")
        #plt.show()

        return self.histogram

    def histogram_peak(self):
        #Pega a esquerda e direita do histograma
        #Retorna a coordenada X da esquerda e direita do histograma
        #Pega os picos da esquerda e direita
        midpoint = int(self.histogram.shape[0]/2)
        leftx_base = np.argmax(self.histogram[:midpoint])
        rightx_base = np.argmax(self.histogram[midpoint:]) + midpoint
        return (leftx_base, rightx_base)
    def get_lane_line_indices_sliding_windows(self):
        #Pegando as faixas da direita e esquerda

        #Largura da janela
        margin = self.margin

        frame_sliding_window = self.warped_frame.copy()

        #Configurando a altura da janela
        window_height = int(self.warped_frame.shape[0]/self.no_of_windows)

        #Encontrando o X e Y das coordenadas nonzero
        nonzero = self.warped_frame.nonzero() #Pega as coordenadas Y e X dos pixels = a 1 (Branco)
        nonzeroy = np.array(nonzero[0]) #Coordenadas em Y
        nonzerox = np.array(nonzero[1]) #Coordenadas em X

        #Armazena as coordenadas das faixas da esquerda e da direita
        left_lane_inds = []
        right_lane_inds = []

        #Posição atual das coordenadas dos pixel de cada janela
        #que irão continuar atualizando
        leftx_base, right_base = self.histogram_peak()
        leftx_current = leftx_base
        rightx_current = right_base

        no_of_windows = self.no_of_windows

        for window in range(no_of_windows):
            #Identificando os limites de X e Y (direita e esquerda)
            win_y_low = self.warped_frame.shape[0] - (window + 1) * window_height #warped_frame[0] = 1080 | 972
            win_y_high = self.warped_frame.shape[0]- window * window_height#1080
            win_xleft_low = leftx_current - margin #399
            win_xleft_high = leftx_current + margin #719
            win_xright_low = rightx_current - margin #1236
            win_xright_high = rightx_current + margin #1556
            cv2.rectangle(frame_sliding_window, (win_xleft_low, win_y_low),(
                win_xright_high, win_y_high),(255,255,255),2)
            cv2.rectangle(frame_sliding_window, (win_xright_high, win_y_low), (
                win_xleft_high, win_y_high), (255,255,255), 2)

            #Identificando pixels diferente de 0 em X e Y dentro da janela
            #As condições são referentes aos quatro cantos da janela
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xleft_low)
                              & (nonzerox <= win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xright_low)
                              & (nonzerox <= win_xright_high)).nonzero()[0]

            #Armazenando os pixels bons dentro da janela em uma lista
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)


            print(nonzeroy)
            print(win_y_low)
            print((nonzeroy >= win_y_low))


            print(f"{11*'='} {window} {11*'='}")
            print(f"Altura das janelas: {win_y_low},{win_y_high}")
            print(f"Esq e Dir: Esq: {win_xleft_low}, {win_xleft_high}")
            print(f"Esq e Dir: Dir: {win_xright_low}, {win_xright_high}")
            print("*-"*20)





#Criando o objeto
lane_obj = Lane(orig_frame=cv2.imread(img))

#Criando isolando as faixas
lane_obj.get_line_markings()

#Desenhando o trapézio no frame
lane_obj.plot_roi()

#Transformando em vista superior
lane_obj.perspective_transform()

#Calculando o histograma
lane_obj.calculate_histogram()

#Exemplo da pegagem do histograma
lane_obj.histogram_peak()

#Encontrando as faixas da esquerda e direita
lane_obj.get_lane_line_indices_sliding_windows()

