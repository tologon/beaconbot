from WheelEncoder import WheelEncoder
from Adafruit_MotorHAT import *
from PID import PID
from custom_motors import *
import atexit
import time

def drive_straight(distance_to_travel):
    motor_hat = Adafruit_MotorHAT(addr=0x60)

    left_motor  = motor_hat.getMotor(2)
    right_motor = motor_hat.getMotor(1)

    initial_power = 100
    master_power = initial_power + 3  # left encoder
    slave_power  = initial_power - 5   # right encoder

    left_encoder = WheelEncoder(20, 20, 1.625) # 3.25
    right_encoder = WheelEncoder(21, 20, 1.625)

    motors = Motors(right_motor, right_encoder, left_motor, left_encoder)

    time_delay = 0.25
    onetick_power_change = 4

    distance_travelled = 0
    distance_to_travel = 100 # cm
	
    while distance_travelled < distance_to_travel:
        signed_error = (left_encoder.getTicks() - right_encoder.getTicks()) * onetick_power_change
	
	master_power -= signed_error / 2.0
 	slave_power += signed_error / 2.0	

	motors._set_power_directional(LEFT, int(master_power))
        motors._set_power_directional(RIGHT, int(slave_power))
	
	#print "l: %3.0f r: %3.0f lt: %2.0f rt: %2.0f d: %2.0f dst: %3.0fcm?" % (master_power, slave_power, left_encoder.getTicks(), right_encoder.getTicks(), signed_error, distance_travelled)
	distance_travelled += (left_encoder.getCurrentDistance() + right_encoder.getCurrentDistance()) / 2.0
	
        left_encoder.resetTicks()
	right_encoder.resetTicks()

	time.sleep(time_delay)
