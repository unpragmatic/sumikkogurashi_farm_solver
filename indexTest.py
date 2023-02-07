import cv2 as cv
import numpy as np



tileSize = 141
maskMat = np.zeros((tileSize, tileSize), dtype=np.uint8)
cv.circle(maskMat, (70, 70), 60, (255, 255, 255), -1)
cv.imshow("test", maskMat)

cv.waitKey(0)
cv.destroyAllWindows()