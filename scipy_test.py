import scipy.optimize as sciopt
import time
from scipy.spatial import distance
import random as rng
import numpy as np
# d = list of measured distances to beacon
# p = list of known positions

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap

@timing
def _minimize(fun, gradient, x0):
    return sciopt.minimize(fun=fun, jac=gradient, x0=x0).x


for sample_size in range(3,100):
    error = 0
    for iteration in range(1):
        p = [(rng.uniform(-1, 1),rng.uniform(-1, 1)) for x in range(sample_size)]
        target = (rng.uniform(-1, 1), rng.uniform(-1, 1))

        d = [distance.euclidean(target,i) for i in p]
        #print "Points: ", p
        #print "Target:", target
        #print "Distances from points to target: ", d

        def dist(x):
            sum = 0
            for i in range(len(d)):
                #print "Distance: ", x, p[i]
                sum += abs(d[i] - distance.euclidean(x, p[i]))
            return sum
	
	def gradient(x):
	    a = 0
	    b = 0
            for j in range(len(d)):
		#print x, p[j]
                eucl = distance.euclidean(x, p[j])
                a += (x[0]-p[j][0])/eucl
                b += (x[1]-p[j][1])/eucl
	    #print "Gradient: ", a, b
	    return np.asarray([a, b])

        predicted = _minimize(dist, gradient, (0,0))
        print predicted
        print "Error: ", distance.euclidean(predicted,target)
        error += distance.euclidean(predicted, target)
    print "Samples: ", sample_size
    print "Error  : ", error/sample_size
    print


