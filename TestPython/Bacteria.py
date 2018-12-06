import cv2
import random
import math
import  copy

# Caution: After a bacteria splits, the center location will not be the same. This could be problamatic if the divide
# function is called due to projected growth & the bacteria was not visible in the frame to confirm this. The result may
# be that the next frame, the bacteria is seen again, but it is still not 'splittitng' size and it checks for previous
# bacteria with a center that is near its current center but donesnt find any. Because the bacteria was split during the
# previous frame and the center has now become two centers with drastically different locations.

class Bacteria(object):
    split_threshold = 32 # 32, 35, *33 works*
    center = []
    Left = []
    Right = []
    Top = []
    Bot = []
    color = (0, 0, 0)
    area = 0
    life = 0

    last_bacteria_copy = None
    parent_bacteria = None

    #deltas
    velocity = []
    growth_rate = []

    def __init__(self, center, extremes):
        self.center = list(center)

        self.Left = list(extremes[0])
        self.Right = list(extremes[1])
        self.Top = list(extremes[2])
        self.Bot = list(extremes[3])
        self.color = (random.randrange(100, 255), random.randrange(100, 255), random.randrange(100, 255))

    def setParent(self, parent_bacteria):
        self.parent_bacteria = parent_bacteria

    def divide(self):
        div_1_center = []
        div_1_extremes = []

        div_2_center = []
        div_2_extremes = []

        div_1_v = copy.deepcopy(self.velocity)
        div_2_v = copy.deepcopy(self.velocity)

        scalar = 10


        if math.hypot(self.Right[0] - self.Left[0], self.Right[1] - self.Left[1])\
                > math.hypot(self.Top[0] - self.Bot[0], self.Top[1] - self.Bot[1]):
            div_1_extremes = [self.center, self.Left, self.center, self.Left]
            div_1_center = list((int((self.Left[0] + self.center[0]) / 2), int(((self.Left[1] + self.center[1]) / 2))))

            div_2_extremes = [self.center, self.Right, self.center, self.Right]
            div_2_center = list((int((self.Right[0] + self.center[0]) / 2), int(((self.Right[1] + self.center[1]) / 2))))

            num_1 = self.center[0] - self.Right[0]
            den_1 = self.center[1] - self.Right[1]

            num_2 = self.center[0] - self.Left[0]
            den_2 = self.center[1] - self.Left[1]

            mag_1 = math.sqrt(num_1*num_1 + den_1*den_1)
            mag_2 = math.sqrt(num_2*num_2 + den_2*den_2)



            unit_1 = []
            unit_1.append(num_1 / mag_1 * scalar)
            unit_1.append(den_1 / mag_1 * scalar)

            unit_2 = []
            unit_2.append(num_2 / mag_2 * scalar)
            unit_2.append(den_2 / mag_2 * scalar)

            div_1_v.append(unit_1)
            div_2_v.append(unit_2)
            # check to see which corner(top or bot) is closest to the left
            # cv2.line(image, tuple(self.Left), tuple(self.Right), color=self.color, thickness=3)

        else:
            div_1_extremes = [self.center, self.Top, self.center, self.Top]
            div_1_center = list((int((self.Top[0] + self.center[0]) / 2), int(((self.Top[1] + self.center[1]) / 2))))

            div_2_extremes = [self.center, self.Bot, self.center, self.Bot]
            div_2_center = list((int((self.Bot[0] + self.center[0]) / 2), int(((self.Bot[1] + self.center[1]) / 2))))

            num_1 = self.center[0] - self.Bot[0]
            den_1 = self.center[1] - self.Bot[1]

            num_2 = self.center[0] - self.Top[0]
            den_2 = self.center[1] - self.Top[1]

            mag_1 = math.sqrt(num_1 * num_1 + den_1 * den_1)
            mag_2 = math.sqrt(num_2 * num_2 + den_2 * den_2)

            unit_1 = []
            unit_1.append(num_1 / mag_1 * scalar * 0)
            unit_1.append(den_1 / mag_1 * scalar * 0)

            unit_2 = []
            unit_2.append(num_2 / mag_2 * scalar * 0)
            unit_2.append(den_2 / mag_2 * scalar * 0)

            div_1_v.append(unit_1*scalar)
            div_2_v.append(unit_2*scalar)
            # check to see which corner(top or bot) is closest to the left
            # cv2.line(image, tuple(self.Top), tuple(self.Bot), color=self.color, thickness=3)

        div_1 = Bacteria(div_1_center, div_1_extremes)
        div_2 = Bacteria(div_2_center, div_2_extremes)

        div_1.setParent(self)
        div_2.setParent(self)

        div_1.velocity = div_1_v
        div_2.velocity = div_2_v

        diff = 3

        div_1.color = (self.color[0]-0, self.color[1]-diff, self.color[2]-diff)
        div_2.color = (self.color[0]+diff, self.color[1]+0, self.color[2]+diff)

        return div_1, div_2

    def needsDivide(self):
        if self.getBacteriaLength(self.Left, self.Right, self.Top, self.Bot) > self.split_threshold:
            return True
        return False

    def getBacteriaLength(self, Left, Right, Top, Bot):
        return max(math.hypot(Right[0] - Left[0], Right[1] - Left[1]), math.hypot(Top[0] - Bot[0], Top[1] - Bot[1]))

    def updateBacteria(self, bacteria, old_copy):

        self.last_bacteria_copy = old_copy

        self.velocity.append([bacteria.center[0] - self.center[0], bacteria.center[1] - self.center[1]])
        self.center = bacteria.center

        # self.growth_rate = self.getBacteriaLength(extremes[0], extremes[1], extremes[2], extremes[3]) - \
        #                    self.getBacteriaLength(self.Left, self.Right, self.Top, self.Bot)

        old_length = self.getBacteriaLength(self.Left, self.Right, self.Top, self.Bot)
        new_length = bacteria.getBacteriaLength(bacteria.Left, bacteria.Right, bacteria.Top, bacteria.Bot)
        diff = new_length - old_length

        self.growth_rate.append(diff)
        # print("Difference in size = ", diff)

        self.Left = bacteria.Left
        self.Right = bacteria.Right
        self.Top = bacteria.Top
        self.Bot = bacteria.Bot
        self.life = self.life + 1

    def compareLastBacteriaCopy(self, bacteria):
        return bacteria == self.last_bacteria_copy

    def predictiveUpdate(self):

        # Velocity / center
        average_velocity = []
        total_x = 0
        total_y = 0

        num_of_samples = 3
        for x in range(max(0, len(self.velocity)-num_of_samples), len(self.velocity)):
            total_x += self.velocity[x][0]
            total_y += self.velocity[x][1]

        # using a max of 2 to give some resistance to the initial velocities
        average_velocity.append(total_x / num_of_samples)
        average_velocity.append(total_y / num_of_samples)

        self.center[0] = self.center[0] + average_velocity[0]
        self.center[1] = self.center[1] + average_velocity[1]

        # print("Predicitive Update ", average_velocity)


        #TODO: Add predicitve growth
        # Growth / extremes
        # average_growth = []
        #
        self.Left[0] = self.Left[0] + average_velocity[0]
        self.Left[1] = self.Left[1] + average_velocity[1]

        self.Right[0] = self.Right[0] + average_velocity[0]
        self.Right[1] = self.Right[1] + average_velocity[1]

        self.Top[0] = self.Top[0] + average_velocity[0]
        self.Top[1] = self.Top[1] + average_velocity[1]

        self.Bot[0] = self.Bot[0] + average_velocity[0]
        self.Bot[1] = self.Bot[1] + average_velocity[1]

        self.life = self.life + 1


    def drawBacteria(self, image):
        # cv2.line(image,
        #          (int((self.ext_TL[0]+self.ext_TR[0])/2), int((self.ext_TL[1]+self.ext_TR[1])/2)),
        #          (int((self.ext_BL[0]+self.ext_BR[0])/2), int((self.ext_BL[1]+self.ext_BR[1])/2)),
        #          color=self.color, thickness=3)

        # cv2.line(image, self.Left, self.Right, color=self.color, thickness=3)
        # cv2.line(image, self.Top, self.Bot, color=self.color, thickness=3)

        if self.needsDivide():
            self.color = (0, 0, 255)

        if math.hypot(self.Right[0] - self.Left[0], self.Right[1] - self.Left[1])\
                > math.hypot(self.Top[0] - self.Bot[0], self.Top[1] - self.Bot[1]):
            cv2.line(image, tuple(self.roundList(self.Left)), tuple(self.roundList(self.Right)), color=self.color, thickness=3)
        else:
            cv2.line(image, tuple(self.roundList(self.Top)), tuple(self.roundList(self.Bot)), color=self.color, thickness=3)

        cv2.line(image, tuple(self.roundList(self.center)), tuple(self.roundList(self.center)), color=(255, 255, 255), thickness=5)
        cv2.line(image, tuple(self.center), tuple(self.center), color=(255, 0, 255), thickness=3)

        return image

    def roundList(self, l):
        temp = l
        for x in range(0, len(l)):
            temp[x] = int(round(l[x]))

        return temp

    def getDistanceBetween(self, bacteria):
        if bacteria is None:
            return 100000
        return math.hypot(bacteria.center[0] - self.center[0], bacteria.center[1] - self.center[1])

    def getOlderBacteria(self, bacteria):
        if self.life > bacteria.life:
            return bacteria, self
        return self, bacteria





