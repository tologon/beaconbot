# Kalman filter for RSSI readings
class KalmanFilter:
    def __init__(self):
        # process variance for VOLTAGE; might be different for RSSI
        self.Q = 0.00001
        #self.Q = 0.05
        # estimate of measurement variance, change to see effect
        self.R = 0.1**2
        # initial guesses
        # current estimation
        self.xhat = 0.0
        # prior error covariance
        self.P = 1.0
        # range for the possible RSSI values (in Db)
        # self.lowest, self.highest = -30.0, 0.0
        self.z = 0

    def time_update(self):
        self.xhatminus = self.xhat
        self.Pminus = self.P + self.Q

    def measurement_update(self, measured_value):
        self.time_update()

        self.z = measured_value

        self.K = self.Pminus / ( self.Pminus + self.R )
        self.xhat = self.xhatminus + self.K * ( self.z - self.xhatminus )
        self.P = ( 1 - self.K ) * self.Pminus

    def estimation(self):
        return self.xhat

    def reset(self):
        # initial guesses
        # current estimation
        self.xhat = 0.0
        # prior error covariance
        self.P = 1.0
        # range for the possible RSSI values (in Db)
        # self.lowest, self.highest = -30.0, 0.0
        self.z = 0

    def print_result(self):
        print 'measured value: %6.2f' % self.z, "| current estimation: %6.2f" % self.xhat

if __name__ == "__main__":
    from time import sleep
    import random as rng

    kalman_filter = KalmanFilter()

    while True:
        kalman_filter.measurement_update(rng.normalvariate(-40.0, 10))
        kalman_filter.print_result()
        sleep(0.2)
