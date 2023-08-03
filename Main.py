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
        self.orig_image_size = self.orig_frame.shape[::1][1:]

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
            [self.padding,0], #Top-left
            [self.padding, self.orig_image_size[1]], #Bottom-left
            [self.orig_image_size[0]-self.padding, self.orig_image_size[1]], #Borron-right
            [self.orig_image_size[0]-self.padding,0] #Top-right
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
        _, sxbinary = edge.threshold(hls[:,:,1], thresh=(170,255))
        sxbinary = edge.blur_gaussian(sxbinary, ksize=3)

        #Aplicando o threshold no canal de saturação, pois quanto maior o seu valor mais pura a cor será
        s_channel = hls[:,:,2] #Captando apenas o canal de saturação
        _, s_binary = edge.threshold(s_channel,(130,255))

        #Aplicando threshold no canal vermelho do frame, isso fará como que faça a captação da cor amarela
        #também, o branco no BGR é (255,255,255), o amarelo é (0,255,255), então se zerarmos o vermelho conseuimos
        #o amarelo.
        _,r_thresh = edge.threshold(frame[:,:,2], thresh=(120,255))

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

    def perspective_transform(self, frame = None):
        if frame is None:
            frame = self.rs_binary  # self.lane_line_markings

            # Calculate the transformation matrix para pegar os pontos para a vista superior
        self.transformation_matrix = cv2.getPerspectiveTransform(
            self.roi_points, self.desire_roi_points)
        print(self.roi_points)
        #print(self.desire_roi_points)
        #print(self.transformation_matrix)
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




#Criando o objeto
lane_obj = Lane(orig_frame=cv2.imread(img))

#Criando isolando as faixas
lane_obj.get_line_markings()

#Desenhando o trapézio no frame
lane_obj.plot_roi()

#Transformando em vista superior
lane_obj.perspective_transform()
