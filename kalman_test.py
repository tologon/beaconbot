from time import sleep
from kalman_filter import KalmanFilter
import random as rng

kalman_filter = KalmanFilter()


while True:
    kalman_filter.measurement_update(rng.normalvariate(-40.0, 10))
    kalman_filter.print_result()
    sleep(0.2)

