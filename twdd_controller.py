from numpy import cos, sin

# A simple two-wheel differential drive controller
class TWDDController(object):
    def __init__(self, wheel_distance):
        """Initialize the controller with the inter-wheel distance"""
        self.wheel_distance = wheel_distance

    def base_velocity(self, left_velocity, right_velocity):
        return 0.5 * (left_velocity + right_velocity)

    def ang_velocity(self, left_velocity, right_velocity):
        return 1.0 / self.b * (right_velocity - left_velocity)

    def dead_reckon(self, left_velocity, right_velocity, time):
        """Returns the (x, y) of the platform given the wheel velocities
        and the time step."""
        # assumes orientation along x axis

        # ignore one wheel if the percent difference is low
        if (left_velocity + right_velocity < 0.01 or
            abs(2.0 * (left_velocity - right_velocity) / (left_velocity + right_velocity)) < 0.01):
            return ( (time * left_velocity, 0), 0)

        theta = time / self.wheel_distance * (right_velocity - left_velocity)
        radius = self.wheel_distance / 2.0 * ((left_velocity + right_velocity) / (right_velocity - left_velocity))

        x = cos(theta / 2.0) * (2.0 * radius * sin(theta / 2.0))
        y = sin(theta / 2.0) * (2.0 * radius * sin(theta / 2.0))

        return ((x, y), theta)
