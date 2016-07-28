from numpy import cos, sin, deg2rad

PI = 3.1415
# A simple two-wheel differential drive controller
class PositionTracker(object):
    def __init__(self, wheel_distance):
        """Initialize the controller with the inter-wheel distance"""
        self.wheel_distance = wheel_distance
        self.x = 0
        self.y = 0
        self.theta = 0

    def update(self, left_distance, right_distance):
        """Returns the (x, y) of the platform given the distances 
           travelled by each wheel."""
        if left_distance + right_distance == 0:
            return

        # ignore one wheel if the percent difference is low
        if right_distance == left_distance:
            self.x += left_distance * cos(self.theta)
            self.y += left_distance * sin(self.theta)
        else:
	    expr = self.wheel_distance * (right_distance + left_distance) / 2.0 / (right_distance - left_distance)

            rminusl = right_distance - left_distance


            self.x += expr * (sin((rminusl / self.wheel_distance) + self.theta) - sin(self.theta))
            self.y -= expr * (cos((rminusl / self.wheel_distance) + self.theta) - cos(self.theta))

            self.theta -= (rminusl / self.wheel_distance)

            while self.theta > 2*PI:
                self.theta -= (2*PI)
            while self.theta < -2*PI:
                self.theta += (2*PI)

            print "Updated PositionTracker: at x=%f, y=%f, theta=%f" % (self.x, self.y, self.theta * 180.0/3.1415)

    def getState(self):
        return (self.x, self.y, self.theta)

