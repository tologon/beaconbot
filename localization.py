from scipy.spatial import distance
from scipy.optimize import minimize
from numpy import asarray
from time import time

class Localizer(object):
    def __init__(self, samples=12):
        self.samples = samples
        self.state = []

    def update(self, sample):
        """Takes an ((x, y), distance) as a sample"""

	# Ensure we never go over the sample count
        if len(self.state) >= self.samples:
	    self.state = self.state[1:]
	self.state.append(sample)

    def my_location(self):
	return self.state[-1][0]

    def _error(self, test_point):
        """Takes a test point and calculates the error based on known
           distances and known points."""
        total = 0 
        for sample in self.state:
            sample_point = sample[0]
            dist = sample[1]

            total += abs(dist - distance.euclidean(test_point, sample_point))
        return total

    def _error_gradient(self, test_point):
        """Takes a test point and calculates the error function's gradient
           based on known points."""
        x_gradient = 0 
        y_gradient = 0 
        for sample in self.state:
            sample_point = sample[0]
            dist = sample[1]

            dist_error = distance.euclidean(test_point, sample_point)
	    # TODO: Fix div by zero here
            if dist_error*abs(dist - dist_error) < 0.0001:
                denominator = -1
            else:
                denominator = -1.0*(dist-dist_error)/(dist_error*abs(dist-dist_error))
                #print "denom: ", denominator
            #print "sample_point: ", sample_point
            #print "test_point: ", test_point
            x_gradient += (test_point[0] - sample_point[0])*denominator
            y_gradient += (test_point[1] - sample_point[1])*denominator

        return asarray([x_gradient, y_gradient])


    def target_location(self):
	# Specifically optimized this for this task.
	return minimize(fun=self._error,
			method='SLSQP',
			jac=self._error_gradient,
                        x0=(0,0),
                        options={'eps':1.4901e-09,'maxiter':13}
                       ).x
	

if __name__ == '__main__':
    # Run some tests
    import random as rng

    simulation_length = 100
    max_samples = 12

    min_range = -500.0
    max_range = 500.0

    target = (rng.uniform(min_range, max_range), rng.uniform(min_range, max_range))
    points = [(rng.uniform(min_range, max_range),rng.uniform(min_range, max_range)) for x in range(simulation_length)]

    samples = [(p,distance.euclidean(p, target)) for p in points]

    localizer = Localizer(samples=max_samples)

    error = 0
    timer = 0
    for sample in samples:
        localizer.update(sample)
        before = time()
        prediction = localizer.target_location()
        after = time()
        #print prediction, target
        timer += (after-before)*max_range
        error += distance.euclidean(prediction, target)
 

    print "Error (%): ", error/simulation_length/(max_range-min_range)*100
    print "Average time (ms): ", timer/simulation_length

