import cv2

file = cv2.imread("Data/Image/Lane/Pista030.png")
cv2.imshow("Imagem", file)
cv2.waitKey()
cv2.destroyAllWindows()

