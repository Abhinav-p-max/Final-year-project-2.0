import math
from enum import IntEnum

class Gest(IntEnum):
    FIST = 0
    PINKY = 1
    MID = 4
    INDEX = 8
    FIRST2 = 12
    PALM = 31
    V_GEST = 33
    ROCK_GEST = 34

class HLabel(IntEnum):
    MINOR = 0
    MAJOR = 1

class HandRecog:
    def __init__(self, hand_label):
        self.finger = 0
        self.ori_gesture = Gest.PALM
        self.prev_gesture = Gest.PALM
        self.frame_count = 0
        self.hand_result = None
        self.hand_label = hand_label

    def update_hand_result(self, hand_result):
        self.hand_result = hand_result

    def get_signed_dist(self, point):
        sign = -1
        if self.hand_result.landmark[point[0]].y < self.hand_result.landmark[point[1]].y:
            sign = 1
        dist = (self.hand_result.landmark[point[0]].x - self.hand_result.landmark[point[1]].x) ** 2
        dist += (self.hand_result.landmark[point[0]].y - self.hand_result.landmark[point[1]].y) ** 2
        return math.sqrt(dist) * sign

    def get_dist(self, point):
        dist = (self.hand_result.landmark[point[0]].x - self.hand_result.landmark[point[1]].x) ** 2
        dist += (self.hand_result.landmark[point[0]].y - self.hand_result.landmark[point[1]].y) ** 2
        return math.sqrt(dist)

    def set_finger_state(self):
        if self.hand_result is None:
            return

        points = [[8, 5, 0], [12, 9, 0], [16, 13, 0], [20, 17, 0]]
        self.finger = 0

        for point in points:
            dist = self.get_signed_dist(point[:2])
            dist2 = self.get_signed_dist(point[1:])
            ratio = round(dist / dist2, 1) if dist2 != 0 else 0

            self.finger = self.finger << 1
            if ratio > 0.5:
                self.finger |= 1

    def get_gesture(self):
        if self.hand_result is None:
            return Gest.PALM

        current_gesture = Gest.PALM

        if self.finger == Gest.FIST:
            current_gesture = Gest.FIST
        elif self.finger == Gest.INDEX:
            current_gesture = Gest.INDEX
        elif self.finger == Gest.FIRST2:
            current_gesture = Gest.V_GEST
        elif self.finger == Gest.PINKY:
            current_gesture = Gest.PINKY
        elif self.finger == 9: # Index (8) + Pinky (1)
            current_gesture = Gest.ROCK_GEST
        elif self.finger == Gest.PALM:
            current_gesture = Gest.PALM
        
        # Debounce
        if current_gesture == self.prev_gesture:
            self.frame_count += 1
        else:
            self.frame_count = 0

        self.prev_gesture = current_gesture

        if self.frame_count > 4:
            self.ori_gesture = current_gesture

        return self.ori_gesture
