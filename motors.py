from Adafruit_MotorHAT import *
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

    def _run(self, motor, command):
        if motor == LEFT:
            self.left_motor.run(command)
            self.left_state = command
        elif motor == RIGHT:
            self.right_motor.run(command)
            self.right_state = command

    def _set_speed(self, motor, speed):
        if motor == LEFT:
            self.left_motor.setSpeed(abs(speed))
            self.left_speed = speed
        elif motor == RIGHT:
            self.right_motor.setSpeed(abs(speed))
            self.right_speed = speed

    def set_speed(self, motor, speed):
        if speed == 0:
            self._run(motor, Adafruit_MotorHAT.RELEASE)
        elif speed > 0:
            self._run(motor, Adafruit_MotorHAT.FORWARD)
        else:
            self._run(motor, Adafruit_MotorHAT.BACKWARD)

        self._set_speed(motor, speed)

    def get_state(self, motor):
        if motor == LEFT:
            return self.left_state
        elif motor == RIGHT:
            return self.right_state

    def get_speed(self, motor):
        if motor == LEFT:
            return self.left_speed
        elif motor == RIGHT:
            return self.right_speed

