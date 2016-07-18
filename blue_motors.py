# time functions
import time
# clean-up functions
import atexit
# bluetooth classes
from bluepy.btle import Scanner, DefaultDelegate
# element-wise addition
from numpy import add
# Adafruit-related hardware
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
# noise reduction filter
from kalman_filter import KalmanFilter
# encoders
from WheelEncoder import WheelEncoder
# localization / mapping
from localization import Localizer
# wheel drive controller
from twdd_controller import TWDDController

# mathematical constant / Euler's number
e = 2.71828182845904523536028747135266249775724709369995
# create a default object, no changes to I2C address or frequency
motor_hat = Adafruit_MotorHAT(addr=0x60)

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    # disable 4 motors
    for motor in range(1, 5):
        motor_hat.getMotor(motor).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

# motor objects
right_motor = motor_hat.getMotor(1)
left_motor  = motor_hat.getMotor(2)

LEFT  = 'LEFT'
RIGHT = 'RIGHT'

class Motors(object):
    def __init__(self, right_motor, left_motor):
        self.right_motor = right_motor 
        self.left_motor  = left_motor
        self.right_state = Adafruit_MotorHAT.RELEASE
        self.left_state  = Adafruit_MotorHAT.RELEASE
        self.right_speed = 0
        self.left_speed  = 0

    def run(self, motor, command):
        if motor == LEFT:
            self.left_motor.run(command)
            self.left_state = command
        elif motor == RIGHT:
            self.right_motor.run(command)
            self.right_state = command

    def set_speed(self, motor, speed):
        if motor == LEFT:
            self.left_motor.setSpeed(speed)
            self.left_speed = speed
        elif motor == RIGHT:
            self.right_motor.setSpeed(speed)
            self.right_speed = speed

    def get_state(self, motor):
        if motor == LEFT:
            return self.left_state
        elif motor == RIGHT:
            return self.right_state

       
# Object that handles bluetooth packets
class KalmanDelegate(DefaultDelegate):
    def __init__(self, filter):
        DefaultDelegate.__init__(self)
        self.filter = filter

    def handleDiscovery(self, dev, isNewDev, isNewData):
        # If we see the bluetooth beacon's address
        # Update the kalman filter with the rssi
        if dev.addr == '0c:f3:ee:04:22:3d':
            rssi = float(dev.rssi)
            self.filter.measurement_update(rssi)
            #self.filter.print_result()

       
motors = Motors(right_motor, left_motor)
left_encoder = WheelEncoder(20, 32, 3)
right_encoder = WheelEncoder(21, 32, 3)
filter = KalmanFilter()
localizer = Localizer()
twdd_controller = TWDDController(20)

scanner = Scanner().withDelegate(KalmanDelegate(filter))

# scan for BLE devices (i.e. bluetooth beacon)
# scan every 0.1 second for total of 1 second
for x in range(10):
	scanner.scan(0.1)

last_position = (0,0)

while True:
    start_time = time.time()

    # Calculate encoder velocities
    ldist1 = left_encoder.getTotalDistance()
    rdist1 = right_encoder.getTotalDistance()

    scanner.scan(0.1)
    rssi = filter.estimation()
    current_distance = e**((rssi + 72) / (-2.0*10))

    ldist2 = left_encoder.getTotalDistance()
    rdist2 = right_encoder.getTotalDistance()

    end_time = time.time()
    elapsed_time = end_time - start_time

    vl = (ldist2-ldist1) / (1.0 / elapsed_time)
    vr = (rdist2-rdist1) / (1.0 / elapsed_time)

    new_position = twdd_controller.dead_reckon(vl, vr, (elapsed_time) * 1000.0)
    new_position = add(new_position[0], last_position)
    last_position = new_position
    if (vl + vr) / 2 > 0.01:
        localizer.update( (new_position, current_distance) )
        print "new position: ", new_position
        print "target location: ", localizer.target_location()
