from numpy import cos, sin, deg2rad
import math
from math import pi as PI

# A simple two-wheel differential drive controller
class PositionTracker(object):
    def __init__(self, wheel_distance):
        """Initialize the controller with the inter-wheel distance"""
        self.wheel_distance = wheel_distance
        self.x = 0
        self.y = 0
        self.theta = 0

    def reset(self):
        self.x = 0
        self.y = 0
        self.theta = 0

    def update(self, left_distance, right_distance):
        """Returns the (x, y) of the platform given the distances 
           travelled by each wheel."""
        if left_distance + right_distance == 0:
            return

        # ignore one wheel if the percent difference is low
        #if right_distance == left_distance:

        total_distance = (left_distance + right_distance) / 2.0
        self.theta -= (right_distance - left_distance) / self.wheel_distance
        self.x += total_distance * cos(self.theta)
        self.y += total_distance * sin(self.theta)
        #else:
	#    expr = self.wheel_distance * (right_distance + left_distance) / 2.0 / (right_distance - left_distance)
        #
        #    rminusl = right_distance - left_distance
        #

        #    self.x += expr * (sin((rminusl / self.wheel_distance) + self.theta) - sin(self.theta))
        #    self.y -= expr * (cos((rminusl / self.wheel_distance) + self.theta) - cos(self.theta))

        #self.theta -= (rminusl / self.wheel_distance)

        while self.theta > PI:
            self.theta -= 2*PI
        while self.theta < -1*PI:
            self.theta += 2*PI

        print "Updated PositionTracker: at x=%6.2fcm, y=%6.2fcm, theta=%6.2f radians, theta=%6.2f degrees" % (self.x, self.y, self.theta, math.degrees(self.theta))

    def reset(self):
        self.__init__(self.wheel_distance)
    def getState(self):
        return (self.x, self.y, self.theta)

