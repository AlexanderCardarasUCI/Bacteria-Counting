import numpy as np
import copy

class BacteriaManager(object):

    current_bacteria = []   # All Bacteria in the current frame
    current_frame = -1      # Current Frame Number
    last_frame = -1         # Last Frame Number

    same_bact_dist_thresh = 5
    #                   Frame, Bacteria
    all_bacteria_seen = [None] * (39 + 1)   # Every Bacteria seen over all viewed frames (total frames + 1)
    # split_bacteria = [None] * (39 + 1)      # All Bacteria that have been split on a frame

    def __init__(self):
        print("Bacteria Manager Initialized")

    # Returns the estimated number of bacteria in the current frame
    def getNumberOfBacteria(self):
        return len(self.current_bacteria)

    # Updates the current/previous frame number and resets current_bacteria array
    def setFrameNumber(self, frame_number):
        self.current_bacteria = []
        self.last_frame = self.current_frame
        self.current_frame = frame_number

    def removeDuplicates(self):
        filtered = copy.copy(self.current_bacteria)

        for i in range(0, len(self.current_bacteria)):
            for x in range(i+1, len(self.current_bacteria)):
                if self.current_bacteria[i].getDistanceBetween(self.current_bacteria[x]) < self.same_bact_dist_thresh+2:
                    younger, older = self.current_bacteria[i].getOlderBacteria(self.current_bacteria[x])
                    older.updateBacteria(younger, older)
                    filtered.remove(younger)

        # print((len(self.current_bacteria)-len(filtered)), " dup bacteria removed")
        self.current_bacteria = filtered

    def filterSplitBacteria(self):

        filtered = copy.copy(self.current_bacteria)

        last_bacteria = self.all_bacteria_seen[self.last_frame]

        # loop through all bacteria in previous frame
        for i in range(0, len(last_bacteria)):
            for x in range(0, len(self.current_bacteria)):
                # compare aall current bacteria to make sure they are not related to previous frame bacteria
                # check all current bacteria to see if their position is near the position of last frames bacteria's parents position
                # if they are neare the position of last frames bacteria's parents, dont count it
                if self.current_bacteria[x].getDistanceBetween(last_bacteria[i].parent_bacteria) < self.same_bact_dist_thresh:
                    if filtered.__contains__(self.current_bacteria[x]):
                        break
                        # print("Found split copy")
                        # last_bacteria[i].setParent(self.current_bacteria[x])
                        # filtered.remove(self.current_bacteria[x])

        self.current_bacteria = filtered

    def splitBacteria(self):

        # List of all current bacteria + bacteria that split due to size
        current_and_split = []

        # Loop through all bacteria on current frame, including bacteria that were not explicitly seen on this frame
        # meaning, it takes into consideration bacteria seen on the previous frame
        for i in range(0, len(self.current_bacteria)):
            if self.current_bacteria[i].needsDivide():
                div_1, div_2 = self.current_bacteria[i].divide()
                current_and_split.append(div_1)
                current_and_split.append(div_2)

            else:
                current_and_split.append(self.current_bacteria[i])

        self.current_bacteria = current_and_split

    # filter out double counted bacteria from the frame.
    # Double counted bacteria can take the form of seeing the center of a bacteria
    # different from previously divided bacteria's center.
    def addNonVisibleBacteria(self):

        # only search match to previous bacteria when you have already observed a frame before
        assert self.last_frame != -1

        # Get list of all bacteria from previous frame
        last_bacteria = self.all_bacteria_seen[self.last_frame]

        # print("Len of last frame = ", len(last_bacteria))
        # print("Len of current frame = ", len(self.current_bacteria))
        # for all bacteria in the last frame
        for i in range(0, len(last_bacteria)):
            match = True

            # loop through all bacteria in current frame
            for x in range(0, len(self.current_bacteria)):

                # if a bacteria in the last frame does not match a bacteria in the current frame, add it
                if self.current_bacteria[x].compareLastBacteriaCopy(last_bacteria[i]):
                    # print("Match")
                    match = False
                    break

            if match is True:
                last_bacteria[i].predictiveUpdate()
                self.current_bacteria.append(last_bacteria[i])

    # Overwrite bacteria that were added this frame with bacteria that were seen in the previous frame
    def matchCurrentWithPreviousBacteria(self):

        # only search match to previous bacteria when you have already observed a frame before
        assert self.last_frame != -1

        # Get list of all bacteria from previous frame
        last_bacteria = self.all_bacteria_seen[self.last_frame]

        # Loop through all bacteria in current frame
        for i in range(0, len(self.current_bacteria)):

            # placeholder shortest distance
            shortest_distance = 100
            nearest_bacteria = None

            # Loop through all bacteria in previous frame
            for x in range(0, len(last_bacteria)):

                # Get the distance between a current bacteria and a bacteria from the last frame
                distance = self.current_bacteria[i].getDistanceBetween(last_bacteria[x])

                # find smallest distance between current frame bacteria and previous frame bacteria
                if distance < shortest_distance:
                    shortest_distance = distance
                    nearest_bacteria = last_bacteria[x]

            # if there is a bacteria from the previous frame that is near(within 5 px of) current bacteria,
            # replace new bacteria with old
            if (nearest_bacteria is not None) and shortest_distance < self.same_bact_dist_thresh:

                # Update position of old bacteria
                nearest_bacteria_copy = copy.deepcopy(nearest_bacteria)

                nearest_bacteria_copy.updateBacteria(self.current_bacteria[i], nearest_bacteria)
                self.current_bacteria[i] = nearest_bacteria_copy

    # Add bacteria to current frame
    def addBacteria(self, bacteria):
        self.current_bacteria.append(bacteria)

    def total(self):
        if self.last_frame != -1:
            self.matchCurrentWithPreviousBacteria()
            self.addNonVisibleBacteria()
            self.filterSplitBacteria()
            self.splitBacteria()
            self.removeDuplicates()

        self.all_bacteria_seen[self.current_frame] = self.current_bacteria

    def drawBacteria(self, image):
        for x in range(0, len(self.current_bacteria)):
            self.current_bacteria[x].drawBacteria(image)

    def getMinIndex(self, distances):
        index = 0
        smallest = distances[0]
        for x in range(1, len(distances)):
            if distances[x] < smallest:
                smallest = distances[x]
                index = x

        return index
