from scipy.spatial import distance
from scipy.optimize import minimize
from numpy import asarray
from time import time

class Localizer(object):
    def __init__(self, samples=16):
        self.samples = samples
        self.worst_sample = ()
        self.state = []

    def update(self, sample):
        """Takes an ((x, y), distance) as a sample"""
        self.state.append(sample)

        # Ensure we never go over the sample count
        if len(self.state) >= self.samples:
            #self.state = self.state[1:]
            best_error = float('inf')
            for i, sample in enumerate(self.state):
                samples_excluding_this = asarray(self.state[:i] + self.state[i+1:])
                
                error_func = lambda test_point: self._error(test_point, samples_excluding_this)
                error_gradient_func = lambda test_point: self._error_gradient(test_point, samples_excluding_this)

                result = minimize(fun=error_func,
                            method='SLSQP',
                            jac=error_gradient_func,
                            x0=(15,0),
                            options={'eps':1.4901e-09,'maxiter':18}
                            )

                if result.fun < best_error:
                    best_error = result.fun
                    #print "Removing ", sample
                    self.state.remove(sample)

    def reset(self):
        self.state = []

    def _error(self, test_point, samples):
        """Takes a test point and calculates the error based on known
           distances and known points."""
        total = 0 
        for sample in samples:
            sample_point = sample[0]
            dist = sample[1]
            total += abs(dist - distance.euclidean(test_point, sample_point))
        return total

    def _error_gradient(self, test_point, samples):
        """Takes a test point and calculates the error function's gradient
           based on known points."""
        x_gradient = 0
        y_gradient = 0
        for sample in samples:
            sample_point = sample[0]
            dist = sample[1]
            dist_error = distance.euclidean(test_point, sample_point)
            # TODO: update this approach for division by zero
            if dist_error * abs(dist - dist_error) < 0.0001:
                denominator = -1.0
            else:
                denominator = -1.0 * (dist - dist_error) / (dist_error * abs(dist - dist_error))
            x_gradient += (test_point[0] - sample_point[0]) * denominator
            y_gradient += (test_point[1] - sample_point[1]) * denominator
        return asarray([x_gradient, y_gradient])

    def target_location(self):
        error_func = lambda test_point: self._error(test_point, self.state)
        error_gradient_func = lambda test_point: self._error_gradient(test_point, self.state)

        result = minimize(fun=error_func,
                    method='SLSQP',
                    jac=error_gradient_func,
                    x0=(15,0),
                    options={'eps':1.4901e-09,'maxiter':12}
                    )
        return result.x


# test Localizer class
if __name__ == '__main__':
    # Run some tests
    import random as rng
    rng.seed(0)

    simulation_length = 1000
    max_samples = 8

    min_range = -500.0
    max_range = 500.0

    target = (rng.uniform(min_range, max_range), rng.uniform(min_range, max_range))
    points = [(rng.uniform(min_range, max_range),rng.uniform(min_range, max_range)) for x in range(simulation_length)]

    samples = [(p,distance.euclidean(p, target)+rng.uniform(-25.0, 25.0)) for p in points]

    localizer = Localizer(samples=max_samples)

    error = 0
    timer = 0
    for i, sample in enumerate(samples):
        localizer.update(sample)
        prev_time = time()
        prediction = localizer.target_location()
        next_time = time()
        print i,": prediction: ", prediction, "target: ", target
        timer += (next_time - prev_time) * max_range
        error += distance.euclidean(prediction, target)

    print "Error (%): ", error / simulation_length / (max_range - min_range) * 100
    print "Average time (ms): ", timer / simulation_length
