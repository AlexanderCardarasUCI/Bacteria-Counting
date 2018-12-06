import cv2
from PIL import Image
import numpy as np

def getAverageIntensityHSV(image, step):
    cols, rows, _ = image.shape
    counter = 0
    sum = 0
    for y in range(0, rows, step):
        for x in range(0, cols, step):
            counter += 1
            sum += image[x, y][2]  # get the intensity from the current pixel

    return sum / counter

def filterWith_HSV(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # convert to hsv

    average_intensity = getAverageIntensityHSV(hsv, 5)
    high_intensity_boundary = [0, 0, average_intensity + 15], [255, 255, 255]

    output = maskImage(image, hsv, high_intensity_boundary)

    cv2.imshow("Filter with HSV", output)

def filterWith_BLUR_HSV(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # convert to hsv
    size = 2
    hsv = cv2.blur(hsv, (size, size))
    average_intensity = getAverageIntensityHSV(hsv, 5)
    high_intensity_boundary = [0, 0, average_intensity + 15], [255, 255, 255]

    output = maskImage(image, hsv, high_intensity_boundary)

    cv2.imshow("Filter with BLUR, HSV", output)

def maskImage(dst, src, range):
    lower = np.array(range[0], dtype="uint8")
    upper = np.array(range[1], dtype="uint8")

    high_intensity_mask = cv2.inRange(src, lower, upper)
    return cv2.bitwise_and(dst, dst, mask=high_intensity_mask)


def findContourExtremes(inversed):
    return 0


def binarizeImage(morphed, int):
    return 0;

# Computes the total number of bacteria in an image by calling helper functions
def countNumberOfBacteria(image):

    structure_type = cv2.MORPH_CROSS
    morph_type = cv2.MORPH_OPEN
    element_kernel = 5
    element = cv2.getStructuringElement(structure_type,
                                        (element_kernel*2+1, element_kernel*2+1), (element_kernel, element_kernel))


    morphed = cv2.morphologyEx(image, morph_type, element)
    cv2.imshow("morphed", morphed)

    binarized = binarizeImage(morphed, 55)
    cv2.imshow("binarized", binarized)

    inversed = cv2.bitwise_not(binarized)

    top_left, bot_right = findContourExtremes(inversed)
    cv2.rectangle(image, top_left, bot_right, (255, 0, 255), 1)
    cv2.imshow("image", image)

    threshold1 = 100
    threshold2 = 50
    edges = cv2.Canny(morphed, threshold1, threshold2)

    cv2.imshow("edges", edges)

    counter = 0
    return counter