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
            (100,292), #Top-left
            (0,1078), #Bottom-left
            (1918,1078), #Borron-right
            (1818,292) #Top-right
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
        _, sxbinary = edge.threshold(hls[:,:,1], thresh=(120,255))
        sxbinary = edge.blur_gaussian(sxbinary, ksize=3)


        cv2.imshow('img',sxbinary)
        cv2.waitKey()
        cv2.destroyAllWindows()


    def calculate_car_position(self, print_to_terminal):
        #Calculando a posição do carro
        #Assumindo que a câmera do carro esteja no centro do veículo
        car_location = self.orig_frame.shape[1]/2

        #Encontrando a coordenada X faixa inferior
        height = self.orig_frame.shape[0]
        bottom_left = self.left_fit[0]*height**2+ self.left_fit[1]*height + self.left_fit[2]


lane_obj = Lane(orig_frame=cv2.imread(img))
lane_obj.get_line_markings()
