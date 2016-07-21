import threading
import atexit
from Adafruit_MotorHAT import *
from PID import PID
from time import time,sleep
from numpy import sign
import random as rng
LEFT  = 'LEFT'
RIGHT = 'RIGHT'

class Motors(object):
    def __init__(self, right_motor, right_encoder, left_motor, left_encoder, delay=0.01):
        self.right_motor = right_motor
        self.right_encoder = right_encoder

        self.left_motor  = left_motor
        self.left_encoder  = left_encoder

        self.right_state = Adafruit_MotorHAT.RELEASE
        self.left_state  = Adafruit_MotorHAT.RELEASE
        self.right_speed = 0
        self.left_speed  = 0

        self.delay = delay

        self.thread = threading.Thread(target = self.run)
        self.thread.start()

    def _run_command(self, motor, command):
        if motor == LEFT:
            self.left_motor.run(command)
            self.left_state = command
        elif motor == RIGHT:
            self.right_motor.run(command)
            self.right_state = command

    def _set_power(self, motor, power):
        if motor == LEFT:
            self.left_motor.setSpeed(abs(power))
        elif motor == RIGHT:
            self.right_motor.setSpeed(abs(power))

    def _set_power_directional(self, motor, power):
        if power == 0:
            self._run_command(motor, Adafruit_MotorHAT.RELEASE)
        elif power > 0:
            self._run_command(motor, Adafruit_MotorHAT.FORWARD)
        else:
            self._run_command(motor, Adafruit_MotorHAT.BACKWARD)

        self._set_power(motor, power)

    def run(self):
        left_PID = PID(P=3.0, I=2.0, D=0.3)
        left_PID.setSampleTime(self.delay)
        left_PID.SetPoint=self.left_speed

        right_PID = PID(P=3.0, I=2.0, D=0.3)
        right_PID.setSampleTime(self.delay)
        right_PID.SetPoint=self.right_speed

        rdist = 0
        rdist_prev = 0
        ldist = 0
        ldist_prev = 0
        current_time = time()
        last_time = time()

        while True:
            right_PID.SetPoint=self.right_speed
            left_PID.SetPoint=self.left_speed

            sleep(self.delay)

            current_time = time()
            rdist = self.right_encoder.getTotalDistance()
            ldist = self.left_encoder.getTotalDistance()


            print "Desired velocities (l/r): (%f, %f)" % (self.left_speed, self.right_speed)

            rvel = (rdist-rdist_prev)/(current_time-last_time)*sign(self.right_speed)
            lvel = (ldist-ldist_prev)/(current_time-last_time)*sign(self.left_speed)
            print "Current velocities (l/r): (%f, %f)" % (lvel, rvel)

            right_PID.update(rvel)
            left_PID.update(lvel)

            right_motor_output = right_PID.output
            left_motor_output  = left_PID.output

            print "Updating output to (l/r): (%f, %f)" % (left_motor_output, right_motor_output)
            print

            self._set_power_directional('RIGHT', int(right_motor_output))
            self._set_power_directional('LEFT', int(left_motor_output))

            rdist_prev = rdist
            ldist_prev = ldist
            last_time = current_time


    def set_speed(self, left, right):
        self.left_speed = left
        self.right_speed = right

    def get_speed(self, motor):
        if motor == LEFT:
            return self.left_speed
        elif motor == RIGHT:
            return self.right_speed

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

    wheel_dist = 14.6

    # motor objects
    right_motor = motor_hat.getMotor(1)
    left_motor  = motor_hat.getMotor(2)

    left_encoder = WheelEncoder(20, 20, 3.25)
    right_encoder = WheelEncoder(21, 20, 3.25)

    motors = Motors(right_motor, right_encoder, left_motor, left_encoder)
    motors.set_speed(200, 200)
