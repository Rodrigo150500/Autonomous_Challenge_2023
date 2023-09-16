import time
import cv2
import numpy as np
import Edge_detection as edge
import matplotlib.pyplot as plt

class Lane:
    def __init__(self, orig_frame):

        self.orig_frame = orig_frame
        self.rs_binary = None
        self.lane_line_markings = None
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

        width = self.orig_image_size[0] #640
        height = self.orig_image_size[1] #480
        self.width = width
        self.height = height

        self.transformation_matrix = None
        self.warped_frame = None
        self.padding = int(0.25*width)
        self.orig_image_size = self.orig_frame.shape[::-1][1:]


        self.desire_roi_points = np.float32([
            [self.padding, 0],  # Top-left corner
            [self.padding, self.orig_image_size[1]],  # Bottom-left corner
            [self.orig_image_size[0] - self.padding, self.orig_image_size[1]],  # Bottom-right corner
            [self.orig_image_size[0] - self.padding, 0]  # Top-right corner
        ])

    def get_line_markings(self, frame = None, plot=False):

        if frame is None:
            frame = self.orig_frame

        #Convertendo o video em frame de BGR para HLS
        hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)

        _, sxbinary = edge.threshold(hls[:,:,1], thresh=(210,255))
        sxbinary = edge.blur_gaussian(sxbinary, ksize=3)
        s_channel = hls[:,:,2] #Captando apenas o canal de saturação
        _, s_binary = edge.threshold(s_channel,(200,255))
        _,r_thresh = edge.threshold(frame[:,:,2], thresh=(150,255))
        self.rs_binary = cv2.bitwise_and(s_binary, r_thresh)
        self.lane_line_markings = cv2.bitwise_or(self.rs_binary, sxbinary.astype(np.uint8))
        if plot == True:
            cv2.imshow('img',self.lane_line_markings)
    def plot_roi(self, frame = None, plot = False):

        if frame is None:
            frame = self.orig_frame.copy()

        #Desenha o trapézio no frame
        this_image = cv2.polylines(frame, np.int32([
            self.roi_points]), True, (147,20,255),3)

        thisImage = cv2.polylines(this_image, np.int32([
            self.roi_pointsAux]), True, (150,55,52),3)


        if plot == True:
            cv2.imshow('img', thisImage)
    def perspective_transform(self, frame = None, plot = False):
        
def main():
    vid = cv2.VideoCapture(0)
    if vid.isOpened():
        while True:
            ret, frame = vid.read()
            cv2.imshow("Ajuste", frame)
            time.sleep(2)
            cv2.destroyAllWindows()
            break
        while True:
            ret, frame = vid.read()

            lane = Lane(orig_frame=frame)
            lane.get_line_markings(frame, plot=False)
            lane.plot_roi(plot=False)



            if(cv2.waitKey(1) & 0xFF == ord('q')):
                break



main()