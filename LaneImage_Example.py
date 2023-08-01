import cv2 as cv
import numpy as np
import Edge_detection as edge
import matplotlib.pyplot as plt

img = cv.imread("./Data/Image/Lane/Video-50.png")

hls = cv.cvtColor(img, cv.COLOR_BGR2HLS)


#Aplicação de Trashold no canal HLS na iluminação e saturação, também aplicado ao canal vermelho
_, sxbinary = edge.threshold(hls[:, :, 1], thresh=(120, 255))

sxbinary = edge.blur_gaussian(sxbinary, ksize=3)  # Reduce noise

sxbinary = edge.mag_thresh(sxbinary, sobel_kernel=3, thresh=(110, 255))
s_channel = hls[:,:,2]
_,s_binary = edge.threshold(s_channel,(80,255))

_,r_thresh = edge.threshold(img[:,:,2], thresh=(120,255))
rs_binary = cv.bitwise_and(s_binary,r_thresh)
lane_line_markings = cv.bitwise_or(rs_binary, sxbinary.astype(
            np.uint8))

#Aplicado a regiao de interesse
roi_points = np.float32([
    (269, 196),  # Top-left corner
    (0, 1075),  # Bottom-left corner
    (1839, 1075),  # Bottom-right corner
    (1656, 196)  # Top-right corner
        ])
def plot_roi(frame=None, plot=False):
    """
    Plot the region of interest on an image.
    :param: frame The current image frame
    :param: plot Plot the roi image if True
    """
    if plot == False:
        return

    if frame is None:
        frame = img.copy()

    # Overlay trapezoid on the frame
    this_image = cv.polylines(frame, np.int32([
        roi_points]), True, (147, 20, 255), 10)

    # Display the image
    while (1):
        cv.imshow('ROI Image', this_image)

        # Press any key to stop
        if cv.waitKey(0):
            break

    cv.destroyAllWindows()

#Aplicando a transformaçao da perspectiva em vista superior
orig_image_size = img.shape[::-1][1:]
width = orig_image_size[0]
height = orig_image_size[1]

padding = int(0.25 * width)  # padding from side of the image in pixels
desired_roi_points = np.float32([
    [padding, 0],  # Top-left corner
    [padding, orig_image_size[1]],  # Bottom-left corner
    [orig_image_size[
         0] - padding, orig_image_size[1]],  # Bottom-right corner
    [orig_image_size[0] - padding, 0]  # Top-right corner
])
def perspective_transform(frame=None, plot=False):
    """
    Perform the perspective transform.
    :param: frame Current frame
    :param:  Plot the warped image if True
    :return: Bird's eye view of the current lane
    """
    if frame is None:
        frame = rs_binary #lane_line_markings

    # Calculate the transformation matrix
    transformation_matrix = cv.getPerspectiveTransform(
        roi_points, desired_roi_points)

    # Calculate the inverse transformation matrix
    inv_transformation_matrix = cv.getPerspectiveTransform(
        desired_roi_points, roi_points)

    # Perform the transform using the transformation matrix
    warped_frame = cv.warpPerspective(
        frame, transformation_matrix, orig_image_size, flags=(
            cv.INTER_LINEAR))

    # Convert image to binary
    (thresh, binary_warped) = cv.threshold(
        warped_frame, 127, 255, cv.THRESH_BINARY)
    warped_frame = binary_warped

    # Display the perspective transformed (i.e. warped) frame
    if plot == True:
        warped_copy = warped_frame.copy()
        warped_plot = cv.polylines(warped_copy, np.int32([
            desired_roi_points]), True, (166, 94, 94), 20)

        # Display the image
        while (1):
            cv.imshow('Warped Image', warped_plot)

            # Press any key to stop
            if cv.waitKey(0):
                break

        cv.destroyAllWindows()

    return warped_frame


#Identificando as linhas
def calculate_histogram(frame=None, plot=False):
    """
    Calculate the image histogram to find peaks in white pixel count

    :param frame: The warped image
    :param plot: Create a plot if True
    """
    if frame is None:
        frame = perspective_transform(plot=False)

    # Generate the histogram
    histogram = np.sum(frame[int(
        frame.shape[0] / 2):, :], axis=0)
    if plot == True:
        # Draw both the image and the histogram
        figure, (ax2) = plt.subplots(1, 1)  # 2 row, 1 columns
        figure.set_size_inches(10, 5)
        #ax1.imshow(frame, cmap='gray')
        #ax1.set_title("Vista superior")
        ax2.plot(histogram)
        ax2.set_title("Picos do histograma")
        plt.show()

    return histogram


#Aplicando a janela deslizadora para identificar a posição das faixas
def get_lane_line_indices_sliding_windows(plot=False,warped_frame=perspective_transform(plot=False)):
    """
    Get the indices of the lane line pixels using the
    sliding windows technique.

    :param: plot Show plot or not
    :return: Best fit lines for the left and right lines of the current lane
    """
    # Sliding window width is +/- margin - Definição da largura da janela
    margin = int((1 / 12) * width)

    # Set the height of the sliding windows - Define a altura da janela
    window_height = np.int32(warped_frame.shape[0] / 10)
    frame_sliding_window = warped_frame.copy()

    # Find the x and y coordinates of all the nonzero
    # (i.e. white) pixels in the frame.
    nonzero = warped_frame.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])

    # Store the pixel indices for the left and right lane lines
    left_lane_inds = []
    right_lane_inds = []

    # Current positions for pixel indices for each window,
    # which we will continue to update
    leftx_base, rightx_base = histogram_peak()
    leftx_current = leftx_base
    rightx_current = rightx_base


    # Go through one window at a time - Número de janelas que serão colocadas para identificar a linha
    no_of_windows = 10

    for window in range(no_of_windows):
        # Identify window boundaries in x and y (and right and left) - Faz a caixa de seleção da janela deslizante
        win_y_low = warped_frame.shape[0] - (window + 1) * window_height
        win_y_high = warped_frame.shape[0] - window * window_height

        win_xleft_low = leftx_current - margin
        win_xleft_high = leftx_current + margin
        win_xright_low = rightx_current - margin
        win_xright_high = rightx_current + margin
        cv.rectangle(frame_sliding_window, (win_xleft_low, win_y_low), (
            win_xleft_high, win_y_high), (255, 255, 255), 10)
        cv.rectangle(frame_sliding_window, (win_xright_low, win_y_low), (
            win_xright_high, win_y_high), (255, 255, 255), 10)

        # Identify the nonzero pixels in x and y within the window
        good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                          (nonzerox >= win_xleft_low) & (
                                  nonzerox < win_xleft_high)).nonzero()[0]
        good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                           (nonzerox >= win_xright_low) & (
                                   nonzerox < win_xright_high)).nonzero()[0]

        # Append these indices to the lists
        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)


        # If you found > minpix pixels, recenter next window on mean position
        minpix = int((1 / 24) * width)
        if len(good_left_inds) > minpix:
            leftx_current = np.int32(np.mean(nonzerox[good_left_inds]))
        if len(good_right_inds) > minpix:
            rightx_current = np.int32(np.mean(nonzerox[good_right_inds]))
            print(good_left_inds , good_right_inds)

    # Concatenate the arrays of indices
    left_lane_inds = np.concatenate(left_lane_inds)
    right_lane_inds = np.concatenate(right_lane_inds)
    envio = [left_lane_inds,right_lane_inds]
    # Extract the pixel coordinates for the left and right lane lines
    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]

    # Fit a second order polynomial curve to the pixel coordinates for
    # the left and right lane lines
    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)

    left_fit = left_fit
    right_fit = right_fit

    if plot == True:
        # Create the x and y values to plot on the image
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
        ax1.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
        ax2.imshow(frame_sliding_window, cmap='gray')
        ax3.imshow(out_img)
        ax3.plot(left_fitx, ploty, color='yellow')
        ax3.plot(right_fitx, ploty, color='yellow')
        ax1.set_title("Imagem Original")
        ax2.set_title("Imagem em vista superior com as janelas deslizantes")
        ax3.set_title("Detectanto as faixas")
        plt.show()

    return left_fit, right_fit, envio
def histogram_peak():
    """
    Get the left and right peak of the histogram

    Return the x coordinate of the left histogram peak and the right histogram
    peak.
    """
    histogram= calculate_histogram(plot=False)
    midpoint = np.int32(histogram.shape[0] / 2)
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    # (x coordinate of left peak, x coordinate of right peak)
    return leftx_base, rightx_base


#Preenche a faixa
def get_lane_line_previous_window(left_fit, right_fit, plot=False,warped_frame=perspective_transform()):
    """
    Use the lane line from the previous sliding window to get the parameters
    for the polynomial line for filling in the lane line
    :param: left_fit Polynomial function of the left lane line
    :param: right_fit Polynomial function of the right lane line
    :param: plot To display an image or not
    """
    # margin is a sliding window parameter
    margin = int((1 / 12) * width)

    # Find the x and y coordinates of all the nonzero
    # (i.e. white) pixels in the frame.
    nonzero = warped_frame.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])

    # Store left and right lane pixel indices
    left_lane_inds = ((nonzerox > (left_fit[0] * (
            nonzeroy ** 2) + left_fit[1] * nonzeroy + left_fit[2] - margin)) & (
                              nonzerox < (left_fit[0] * (
                              nonzeroy ** 2) + left_fit[1] * nonzeroy + left_fit[2] + margin)))
    right_lane_inds = ((nonzerox > (right_fit[0] * (
            nonzeroy ** 2) + right_fit[1] * nonzeroy + right_fit[2] - margin)) & (
                               nonzerox < (right_fit[0] * (
                               nonzeroy ** 2) + right_fit[1] * nonzeroy + right_fit[2] + margin)))
    left_lane_inds = left_lane_inds
    right_lane_inds = right_lane_inds

    # Get the left and right lane line pixel locations
    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]

    leftx = leftx
    rightx = rightx
    lefty = lefty
    righty = righty

    # Fit a second order polynomial curve to each lane line
    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)
    left_fit = left_fit
    right_fit = right_fit

    # Create the x and y values to plot on the image
    ploty = np.linspace(
        0, warped_frame.shape[0] - 1, warped_frame.shape[0])
    left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
    right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]
    ploty = ploty
    left_fitx = left_fitx
    right_fitx = right_fitx

    if plot == True:
        # Generate images to draw on
        out_img = np.dstack((warped_frame, warped_frame, (
            warped_frame))) * 255
        window_img = np.zeros_like(out_img)

        # Add color to the left and right line pixels
        out_img[nonzeroy[left_lane_inds], nonzerox[left_lane_inds]] = [255, 0, 0]
        out_img[nonzeroy[right_lane_inds], nonzerox[right_lane_inds]] = [
            0, 0, 255]
        # Create a polygon to show the search window area, and recast
        # the x and y points into a usable format for cv2.fillPoly()
        margin = margin
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
        cv.fillPoly(window_img, np.int32([left_line_pts]), (0, 255, 0))
        cv.fillPoly(window_img, np.int32([right_line_pts]), (0, 255, 0))
        result = cv.addWeighted(out_img, 1, window_img, 0.3, 0)

        # Plot the figures
        figure, (ax1, ax2, ax3) = plt.subplots(3, 1)  # 3 rows, 1 column
        figure.set_size_inches(10, 10)
        figure.tight_layout(pad=3.0)
        ax1.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
        ax2.imshow(warped_frame, cmap='gray')
        ax3.imshow(result)
        ax3.plot(left_fitx, ploty, color='yellow')
        ax3.plot(right_fitx, ploty, color='yellow')
        ax1.set_title("Original Frame")
        ax2.set_title("Warped Frame")
        ax3.set_title("Warped Frame With Search Window")
        plt.show()


#Desenha sobre a imgem original a informação do caminho
def overlay_lane_lines(plot=False, warped_frame=perspective_transform(plot=False), left_fit = get_lane_line_indices_sliding_windows(plot=False)[0],right_fit=get_lane_line_indices_sliding_windows(plot=False)[1]):
    """
    Overlay lane lines on the original frame
    :param: Plot the lane lines if True
    :return: Lane with overlay
    """
    # Generate an image to draw the lane lines on
    warp_zero = np.zeros_like(warped_frame).astype(np.uint8)
    color_warp = np.dstack((warp_zero, warp_zero, warp_zero))

    ploty = np.linspace(
        0, warped_frame.shape[0] - 1, warped_frame.shape[0])
    left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
    right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]

    # Recast the x and y points into usable format for cv2.fillPoly()
    pts_left = np.array([np.transpose(np.vstack([
        left_fitx, ploty]))])
    pts_right = np.array([np.flipud(np.transpose(np.vstack([
        right_fitx, ploty])))])
    pts = np.hstack((pts_left, pts_right))

    inv_transformation_matrix = cv.getPerspectiveTransform(
        desired_roi_points, roi_points)
    # Draw lane on the warped blank image
    cv.fillPoly(color_warp, np.int32([pts]), (0, 255, 0))

    # Warp the blank back to original image space using inverse perspective
    # matrix (Minv)
    newwarp = cv.warpPerspective(color_warp, inv_transformation_matrix, (
        img.shape[
            1], img.shape[0]))

    # Combine the result with the original image
    result = cv.addWeighted(img, 1, newwarp, 0.3, 0)

    if plot == True:
        # Plot the figures
        figure, (ax1, ax2) = plt.subplots(2, 1)  # 2 rows, 1 column
        figure.set_size_inches(10, 10)
        figure.tight_layout(pad=3.0)
        ax1.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
        ax2.imshow(cv.cvtColor(result, cv.COLOR_BGR2RGB))
        ax1.set_title("Original Frame")
        ax2.set_title("Original Frame With Lane Overlay")
        plt.show()

    return result

#Calculando a curvatura da pista
def calculate_curvature(print_to_terminal=False, warped_frame = perspective_transform(plot=False), left_lane_inds=get_lane_line_indices_sliding_windows(plot=False)[2][0],right_lane_inds =get_lane_line_indices_sliding_windows(plot=False)[2][1]):
    """
    Calculate the road curvature in meters.

    :param: print_to_terminal Display data to console if True
    :return: Radii of curvature
    """

    # Set the y-value where we want to calculate the road curvature.
    # Select the maximum y-value, which is the bottom of the frame.
    nonzero = warped_frame.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])


    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]
    frame_sliding_window = warped_frame.copy()
    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)
    ploty = np.linspace(
        0, frame_sliding_window.shape[0] - 1, frame_sliding_window.shape[0])
    left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
    right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]
    y_eval = np.max(ploty)
    YM_PER_PIX = 10.0 / 1000  # meters per pixel in y dimension
    XM_PER_PIX = 3.7 / 781
    # Fit polynomial curves to the real world environment
    left_fit_cr = np.polyfit(lefty * YM_PER_PIX, leftx * (
        XM_PER_PIX), 2)
    right_fit_cr = np.polyfit(righty * YM_PER_PIX, rightx * (
        XM_PER_PIX), 2)

    # Calculate the radii of curvature
    left_curvem = ((1 + (2 * left_fit_cr[0] * y_eval * YM_PER_PIX + left_fit_cr[
        1]) ** 2) ** 1.5) / np.absolute(2 * left_fit_cr[0])
    right_curvem = ((1 + (2 * right_fit_cr[
        0] * y_eval * YM_PER_PIX + right_fit_cr[
                              1]) ** 2) ** 1.5) / np.absolute(2 * right_fit_cr[0])

    # Display on terminal window
    if print_to_terminal == True:
        print(left_curvem, 'm', right_curvem, 'm')

    left_curvem = left_curvem
    right_curvem = right_curvem

    return left_curvem, right_curvem


#Calculando o quão longe o carro esta longe do centro da faixa
def calculate_car_position(print_to_terminal=False,warped_frame = perspective_transform(plot=False), left_lane_inds=get_lane_line_indices_sliding_windows(plot=False)[2][0],right_lane_inds =get_lane_line_indices_sliding_windows(plot=False)[2][1]):
    """
    Calculate the position of the car relative to the center

    :param: print_to_terminal Display data to console if True
    :return: Offset from the center of the lane
    """
    # Assume the camera is centered in the image.
    # Get position of car in centimeters
    car_location = img.shape[1] / 2


    nonzero = warped_frame.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]
    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)

    # Fine the x coordinate of the lane line bottom
    height = img.shape[0]
    bottom_left = left_fit[0] * height ** 2 + left_fit[
        1] * height + left_fit[2]
    bottom_right = right_fit[0] * height ** 2 + right_fit[
        1] * height + right_fit[2]
    XM_PER_PIX = 3.7 / 781

    center_lane = (bottom_right - bottom_left) / 2 + bottom_left
    center_offset = (np.abs(car_location) - np.abs(
        center_lane)) * XM_PER_PIX * 100

    if print_to_terminal == True:
        print(str(center_offset) + 'cm')

    center_offset = center_offset

    return center_offset


def display_curvature_offset(frame=None, plot=False,left_curvem=calculate_curvature()[0],right_curvem = calculate_curvature()[1],center_offset=calculate_car_position()):
    """
    Display curvature and offset statistics on the image

    :param: plot Display the plot if True
    :return: Image with lane lines and curvature
    """
    image_copy = None
    if frame is None:
        image_copy = img.copy()
    else:
        image_copy = frame

    cv.putText(image_copy, 'Curve Radius: ' + str((
                                                           left_curvem + right_curvem) / 2)[:7] + ' m',
                (int((
                             5 / 600) * width), int((
                                                                 20 / 338) * height)),
                cv.FONT_HERSHEY_SIMPLEX, (float((
                                                         0.5 / 600) * width)), (
                    255, 255, 255), 2, cv.LINE_AA)
    cv.putText(image_copy, 'Center Offset: ' + str(
        center_offset)[:7] + ' cm', (int((
                                                      5 / 600) * width), int((
                                                                                          40 / 338) * height)),
                cv.FONT_HERSHEY_SIMPLEX, (float((
                                                         0.5 / 600) * width)), (
                    255, 255, 255), 2, cv.LINE_AA)

    if plot == True:
        cv.imshow("Image with Curvature and Offset", image_copy)

    return image_copy


#display_curvature_offset(frame=overlay_lane_lines(plot=False), plot=True)
#calculate_car_position(print_to_terminal=True)
#calculate_curvature(print_to_terminal=True)
#overlay_lane_lines(plot=True)
#get_lane_line_previous_window(left_fit=get_lane_line_indices_sliding_windows()[0],right_fit=get_lane_line_indices_sliding_windows()[1],plot=True)
get_lane_line_indices_sliding_windows(plot=True)
#calculate_histogram(plot=True) #Na linha 77 trocar por "rs_binary" para testar
#perspective_transform(plot=True)
#plot_roi(plot=True)
#cv.imshow("txt",s_binary)

#cv.imshow("txt",rs_binary)
#cv.imshow("txt",img)
cv.waitKey(0)
cv.destroyAllWindows()

