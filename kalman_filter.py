# Kalman filter for RSSI readings

import random as rng
import time

# process variance for VOLTAGE; might be different for RSSI
Q = 1e-5
# estimate of measurement variance, change to see effect
R = 0.1**2

# initial guesses
# current estimation
xhat = 0.0
# prior error covariance
P = 1.0

# range for the possible RSSI values (in Db)
lowest, highest = -30.0, 0.0

while True:
  # time update
  xhatminus = xhat
  Pminus = P + Q

  # measurement update
  K = Pminus / ( Pminus + R )
  z = rng.uniform(lowest, highest)
  xhat = xhatminus + K * ( z - xhatminus )
  P = ( 1 - K ) * Pminus

  print 'measured value: %6.2f' % z, "| current estimation: %6.2f" % xhat

  # time interval in seconds
  time.sleep(0.1)
