import cv2
import ImageHelper
import BacteriaManager
import numpy as np

gif_path = 'bacteria-animation.gif'
start_frame = 0
current_frame = start_frame
total_frames = 40
bacteria_manager = BacteriaManager.BacteriaManager()


def processFrame(frame_number):
    # print("Frame number = ", frame_number)
    bacteria_manager.setFrameNumber(frame_number)
    # Grab a single frame from a gif
    original = ImageHelper.openGifOnFrame(gif_path, frame_number)

    # Split the frame horizontally into two separate images
    left, right = ImageHelper.splitImageVertically(original)

    # Calculate number of bacteria
    #number_of_bacteria_left = str(ImageHelper.countNumberOfBacteria(left))
    number_of_bacteria_right = str(ImageHelper.countNumberOfBacteria(left, right, bacteria_manager))

    # Write 'number of bacteria' onto frame
    #cv2.putText(original, number_of_bacteria_left, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
    cv2.putText(original, number_of_bacteria_right, (330, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)

    # write 'current frame number' onto frame
    cv2.putText(original, str(frame_number), (270, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
    cv2.putText(original, str(frame_number), (590, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)

    cv2.putText(left, "Frame[" + str(frame_number) + "]", (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
    cv2.putText(left, "Count[" + str(number_of_bacteria_right) + "]", (0, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)

    vis = np.concatenate((left, right), axis=1)
    cv2.imshow("Finished", vis)
    print("Frame Number = ", frame_number, " || Num Bacteria = ", number_of_bacteria_right)
    return number_of_bacteria_right

def manualInput(current_frame):
    key = cv2.waitKey()

    if key == 27:
        print("break")
    elif key == 44:
        current_frame -= 1
    elif key == 46:
        current_frame += 1

    return current_frame


write_to_file = False
if write_to_file:
    text_file = open("Output.txt", "w")

while True:
    num_of_bacteria = processFrame(current_frame)

    is_manual_input = True


    if is_manual_input:
        current_frame = manualInput(current_frame)
    else:
        current_frame += 1

    if current_frame < 0:
        current_frame = total_frames - 1
    if current_frame >= total_frames:
        current_frame = 0
        if is_manual_input is not True:
            if write_to_file:
                text_file.write("%s" % num_of_bacteria)
                text_file.close()

            print("Finished")
            break

    else:
        if write_to_file:
            text_file.write("%s\n" % num_of_bacteria)




