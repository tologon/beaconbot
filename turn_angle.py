from WheelEncoder import WheelEncoder
from Adafruit_MotorHAT import *
from PID import PID
from custom_motors import *
import atexit
import time

motor_hat = Adafruit_MotorHAT(addr=0x60)

def turnOffMotors():
    # diable 4 motors
    for motor in range(1, 5):
        motor_hat.getMotor(motor).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

if __name__ == '__main__':
    left_motor  = motor_hat.getMotor(2)
    right_motor = motor_hat.getMotor(1)

    initial_power = 75
    master_power = initial_power + 3  # left encoder
    slave_power  = initial_power - 5   # right encoder

    left_encoder = WheelEncoder(20, 20, 1.75) # 3.25
    right_encoder = WheelEncoder(21, 20, 1.75)

    motors = Motors(right_motor, right_encoder, left_motor, left_encoder)

    time_delay = 0.01
    ticks_turned = 0
    ticks_to_turn = 0
	
    angle_to_turn = 90.0
    inter_wheel_distance = 14.5 # cm

    circumference = inter_wheel_distance * 3.1415926

    ticks_to_turn = right_encoder.getTicksPerDistance(circumference)
	
    ticks_to_turn *= angle_to_turn / 360.0
	
    if angle_to_turn > 0:
        slave_power *= -1
    else:
	master_power *= -1

    motors._set_power_directional(LEFT, int(master_power))
    motors._set_power_directional(RIGHT, int(slave_power))
	
    while right_encoder.getTicks() < ticks_to_turn:
	time.sleep(time_delay)

    print "kill"
