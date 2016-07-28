from Adafruit_MotorHAT import *

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

    def set_speed(self, left, right):
        self.left_speed = left
        self.right_speed = right

    def get_speed(self, motor):
        if motor == LEFT:
            return self.left_speed
        elif motor == RIGHT:
            return self.right_speed
