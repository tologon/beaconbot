# A simple two-wheel differential drive controller

class TWDDController(object):
    def __init__(self, b):
        """Initialize the controller with the inter-wheel distance, b"""
	self.b = b

    def base_velocity(self, vl, vr):
        return 0.5*(vl+vr)

    def ang_velocity(self, vl, vr):
        return 1.0/self.b*(vr-vl)

    def dead_reckon(self, vl, vr, t):
        """Returns the (x, y) of the platform given the wheel velocities
	    and the time step."""
	from numpy import cos, sin
	# assumes orientation along x axis

	# Ignore one wheel if the percent difference is low
	if abs(2.0*(vl-vr)/(vl+vr)) < 0.01:
	    return (t*vl, 0)

	theta = t/self.b*(vr-vl)
	radius = self.b/2.0*((vl+vr)/(vr-vl))

	x = cos(theta/2.0)*(2.0*radius*sin(theta/2.0))
	y = sin(theta/2.0)*(2.0*radius*sin(theta/2.0))

 
 	return ((x, y), theta)

