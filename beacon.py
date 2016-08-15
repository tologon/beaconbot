# bluetooth classes
from bluepy.btle import Scanner, DefaultDelegate
# noise reduction filter
from kalman_filter import KalmanFilter
from numpy import pi as PI
from math import log

# mathematical constant / Euler's number
e = 2.718281

# Object that handles bluetooth packets
class KalmanDelegate(DefaultDelegate):
    def __init__(self, filter, ssid):
        DefaultDelegate.__init__(self)
        self.kalman_filter = filter
        self.ssid = ssid

    def handleDiscovery(self, dev, isNewDev, isNewData):
        # If we see the bluetooth beacon's address
        # Update the kalman filter with the rssi
        if dev.addr == self.ssid:
            rssi = float(dev.rssi)
            self.kalman_filter.measurement_update(rssi)

class BeaconSensor(object):
    def __init__(self, ssid):
        self.kalman_filter = KalmanFilter()
        self.scanner = Scanner().withDelegate(KalmanDelegate(self.kalman_filter, ssid))
    def scan(self, time):
        self.scanner.scan(time)
    def reset(self):
        self.kalman_filter.reset()
    def get_distance(self):
        rssi = self.kalman_filter.estimation()
        print "rssi: %f" % rssi
        distance = 10**( (rssi + 64.5) / (-2.8 * 10) )
        return distance*100
        #return distance*100

if __name__ == '__main__':
    sensor = BeaconSensor('0c:f3:ee:04:22:3d')
    while True:
        sensor.scan(0.25)
        print sensor.get_distance()
