import atexit
from Adafruit_MotorHAT import *
from WheelEncoder import WheelEncoder
from time import time,sleep
from numpy import sign
LEFT  = 'LEFT'
RIGHT = 'RIGHT'

class Motors(object):
    def __init__(self, right_motor, right_encoder, left_motor, left_encoder, delay=0.3):
        self.left_trim = 1
        self.right_trim = 2

        self.right_motor = right_motor
        self.right_encoder = right_encoder

        self.left_motor  = left_motor
        self.left_encoder  = left_encoder

        self.right_state = Adafruit_MotorHAT.RELEASE
        self.left_state  = Adafruit_MotorHAT.RELEASE

        self.delay = delay

    def _run_command(self, motor, command):
        if motor == LEFT:
            self.left_motor.run(command)
            self.left_state = command
        elif motor == RIGHT:
            self.right_motor.run(command)
            self.right_state = command

    def _set_power(self, motor, power):
        if motor == LEFT:
            self.left_motor.setSpeed(abs(power)-self.left_trim)
        elif motor == RIGHT:
            self.right_motor.setSpeed(abs(power)-self.right_trim)

    def _set_power_directional(self, motor, power):
        if power == 0:
            self._run_command(motor, Adafruit_MotorHAT.RELEASE)
        elif power > 0:
            self._run_command(motor, Adafruit_MotorHAT.FORWARD)
        else:
            self._run_command(motor, Adafruit_MotorHAT.BACKWARD)

        self._set_power(motor, power)

    def drive_straight(self, distance_to_travel):
        initial_power = 100
	master_power = initial_power  # left encoder
	slave_power  = initial_power   # right encoder
	onetick_power_change = 4

	distance_travelled = 0

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

	    sleep(self.delay)

if __name__ == '__main__':
    print "Motor Testing"
    # encoders
    from WheelEncoder import WheelEncoder

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

    left_encoder = WheelEncoder(20, 20, 1.625)
    right_encoder = WheelEncoder(21, 20, 1.625)

    sleep(3)

    motors = Motors(right_motor, right_encoder, left_motor, left_encoder)
    motors.drive_straight(300)
