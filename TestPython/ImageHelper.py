import cv2
from PIL import Image
import numpy as np
import random
import Bacteria



# Convert a gif frame to OpenCV mat
def openGifOnFrame(gif_path, frame_number):
    im = Image.open(gif_path)
    for x in range(frame_number):
        im.seek(im.tell() + 1)

    img = np.array(im.convert('RGB'))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img


# Split the OpenCv mat into two separate images by cutting vertically through the center
def splitImageVertically(image):
    image = image.copy()

    height = np.size(image, 0)
    width = np.size(image, 1)

    left = image[0:height, 0:int(width/2)]
    right = image[0:height, int(width/2):width]

    return left, right


# finds and masks the red outline of the bacterias
# NOTE: I cannot use a bounding set of bgr values to mask the two shades of red in the image, must use two separate
# values of red
def maskImage(image):
    lower_boundary = [0, 0, 127]        # bgr value for first of red
    upper_boundary = [127, 127, 255]    # bgr value for second shade of red

    lower = np.array(lower_boundary, dtype="uint8")     # convert to np type array
    upper = np.array(upper_boundary, dtype="uint8")     # convert to np type array

    lower_mask = cv2.inRange(image, lower, lower)       # find pixels with bgr = lower_boundary
    upper_mask = cv2.inRange(image, upper, upper)       # find pixels with bgr = lower_boundary
    full_mask = cv2.inRange(image, lower, upper)        # find pixels with lower_boundary <= bgr <= upper_boundary

    lower_output = cv2.bitwise_and(image, image, mask=lower_mask)   # mask the first set of red pixels
    upper_output = cv2.bitwise_and(image, image, mask=upper_mask)   # mask the second set of red pixels

    return cv2.bitwise_or(lower_output, upper_output, mask=full_mask)   # combined mask of both sets of red pixels


# converts all non-black pixels of an image to white (returns bgr form)
def binarizeImage(image, thresh=0):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)     # convert to gray scale
    ret, thresh = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY)   # apply binary threshold to image
    thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    return thresh

# oops, spilled a paint bucket
def floodFill(image, x, y, color):
    h, w = image.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(image, mask, (x, y), color)
    return image


# fills counts the number of contours and fills them in
def findBacteria(image, area_threshold):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img2, contours, hierarchy = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    counter = 0
    all_bacteria = []
    total_contours = len(contours)
    for i in range(0, total_contours):
        contour_area = cv2.contourArea(contours[i])
        if (contour_area > area_threshold[0]) and (contour_area < area_threshold[1]+area_threshold[2]):

            color = (random.randrange(100, 255), random.randrange(100, 255), random.randrange(100, 255))
            M = cv2.moments(contours[i])
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            if contour_area > area_threshold[1]:
                floodFill(image, cx, cy, (255, 255, 0))
            else:
                floodFill(image, cx, cy, color)

            cv2.rectangle(image, (cx, cy), (cx+1, cy+1), (255, 0, 255))

            Top, Bot, Left, Right = findExtremes(contours[i])
            bact = Bacteria.Bacteria((cx, cy), (Top, Bot, Left, Right))
            all_bacteria.append(bact)
            counter += 1

    return image, all_bacteria

def findExtremes(c):

        Left = tuple(c[c[:, :, 0].argmin()][0])
        Right = tuple(c[c[:, :, 0].argmax()][0])
        Top = tuple(c[c[:, :, 1].argmin()][0])
        Bot = tuple(c[c[:, :, 1].argmax()][0])

        return Top, Bot, Left, Right

def shiftImage(image, x, y):
    rows, cols, _ = image.shape
    M = np.float32([[1, 0, x], [0, 1, y]])
    return cv2.warpAffine(image, M, (cols, rows))

def findContourExtremes(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img2, contours, hierarchy = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    c = contours[0]
    extLeft = tuple(c[c[:, :, 0].argmin()][0])
    extRight = tuple(c[c[:, :, 0].argmax()][0])
    extTop = tuple(c[c[:, :, 1].argmin()][0])
    extBot = tuple(c[c[:, :, 1].argmax()][0])

    number_of_contours = len(contours)

    largest_index = 0
    largest_area = 0
    for i in range(0, number_of_contours):
        area = cv2.contourArea(contours[i])
        if area > largest_area:
            largest_area = area
            largest_index = i

    for x in range(largest_index, largest_index+1):
        c = contours[x]
        Left = tuple(c[c[:, :, 0].argmin()][0])
        Right = tuple(c[c[:, :, 0].argmax()][0])
        Top = tuple(c[c[:, :, 1].argmin()][0])
        Bot = tuple(c[c[:, :, 1].argmax()][0])

        if Left[0] < extLeft[0]:
            extLeft = Left

        if Right[0] > extRight[0]:
            extRight = Right

        if Top[1] < extTop[1]:
            extTop = Top

        if Bot[1] > extBot[1]:
            extBot = Bot

    topLeft = (extLeft[0], extTop[1])
    botRight = (extRight[0], extBot[1])

    return topLeft, botRight


def skeletonize(img):
    """ OpenCV function to return a skeletonized version of img, a Mat object"""

    #  hat tip to http://felix.abecassis.me/2011/09/opencv-morphological-skeleton/

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # don't clobber original
    skel = img.copy()

    skel[:,:] = 0
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))

    while True:
        eroded = cv2.morphologyEx(img, cv2.MORPH_ERODE, kernel)
        temp = cv2.morphologyEx(eroded, cv2.MORPH_DILATE, kernel)
        temp = cv2.subtract(img, temp)
        skel = cv2.bitwise_or(skel, temp)
        img[:,:] = eroded[:,:]
        if cv2.countNonZero(img) == 0:
            break

    return cv2.cvtColor(skel, cv2.COLOR_GRAY2BGR)


def filterImage(left, right):
    # cv2.imshow("right", right)
    red_mask = maskImage(right)  # find all red pixels in image
    # cv2.imshow("red_mask", red_mask)

    binarized = binarizeImage(red_mask)  # convert all red pixels to white, leaving the background black
    # cv2.imshow("binarized", binarized)

    dilated = cv2.dilate(binarized, (3, 3), iterations=1)
    # cv2.imshow("dilated", dilated)

    skel = skeletonize(dilated)
    # cv2.imshow("skel", skel)

    combined = cv2.bitwise_or(skel, binarized)
    # cv2.imshow("combined", combined)


    inversed = cv2.bitwise_not(combined)  # swap all black and white pixels
    # cv2.imshow("inversed", inversed)

    flood_filled = floodFill(inversed, 0, 0, 0)  # 'paint bucket' fill the screen
    # flood_filled = floodFill(inversed, 165, 129, (127, 127, 255))  # 'paint bucket' fill the screen
    # cv2.imshow("flood_filled", flood_filled)

    #Fill all contours within the area x to y with rand colors and y to z with a set color
    filled_contours, bacteria = findBacteria(flood_filled, (40, 120, 70))
    #cv2.imshow("filled_contours", filled_contours)

    # bact = Bacteria.Bacteria((0, 0), ((50, 50), (60, 50), (40, 90), (50, 90)))
    # bact.draw_bacteria(left)
    #
    # bact2 = Bacteria.Bacteria((0, 0), ((150, 150), (160, 150), (140, 190), (150, 190)))
    # bact2.draw_bacteria(left)

    # cv2.imshow("left(bact drawn)", left)

    #cv2.rectangle(image, topLeft, botRight, (0, 0, 255))
    return filled_contours, bacteria

# Computes the total number of bacteria in an image by calling helper functions
def countNumberOfBacteria(left, right, bacteria_manager):
    filteredImage, bacteria = filterImage(left, right)

    # draw bacteria
    for x in range(0, len(bacteria)):
        bacteria_manager.addBacteria(bacteria[x])

    bacteria_manager.total()
    bacteria_manager.drawBacteria(left)

    number_of_bacteria = bacteria_manager.getNumberOfBacteria()

    # cv2.putText(left, "Frame["+str(bacteria_manager.current_frame)+"]", (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
    # cv2.putText(left, "Count["+str(number_of_bacteria)+"]", (0, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
    # cv2.imshow("left(bact drawn)", left)


    # print("Image Helper: Found ", bacteria_manager.getNumberOfBacteria(), " bacteria")
    return number_of_bacteria
