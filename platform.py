from Adafruit_MotorHAT import *
from WheelEncoder import WheelEncoder
from position_tracker import *
from numpy import sign
from time import sleep
import atexit

LEFT = 'LEFT'
RIGHT = 'RIGHT'


class Platform(object):
    def __init__(self, right_motor_pin=1, right_encoder_pin=21, left_motor_pin=2, left_encoder_pin=20, delay=0.05):
        self.motor_hat = Adafruit_MotorHAT(addr=0x60)

        # DO NOT CHANGE THOSE VALUES
        # REQUIRED VALUES FOR CORRECT TURNING (WITH UP TO 5 DEGREE ACCURACY):
        # self.left_trim    = -7
        # self.right_trim   = 6
        self.left_trim = -7
        self.right_trim = 6

        self.inter_wheel_distance = 15

        self.right_motor = self.motor_hat.getMotor(right_motor_pin)
        self.right_encoder = WheelEncoder(right_encoder_pin, 20, 1.625)

        self.left_motor = self.motor_hat.getMotor(left_motor_pin)
        self.left_encoder = WheelEncoder(left_encoder_pin, 20, 1.625)

        self.right_state = Adafruit_MotorHAT.RELEASE
        self.left_state  = Adafruit_MotorHAT.RELEASE

        self.position_tracker= PositionTracker(self.inter_wheel_distance)#-1.40)

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

    def get_state(self):
        return self.position_tracker.getState()

    def shutdown(self):
        for motor in range(1, 5):
            self.motor_hat.getMotor(motor).run(Adafruit_MotorHAT.RELEASE)

    def drive_straight(self, distance_to_travel):
        initial_power = 110
	master_power = initial_power  # left encoder
	slave_power  = initial_power   # right encoder
	onetick_power_change = 4

        left_distance = 0
        right_distance = 0

	distance_travelled = 0

	while distance_travelled < distance_to_travel:
	    signed_error = (self.left_encoder.getTicks() - self.right_encoder.getTicks()) * onetick_power_change
	    
	    master_power -= signed_error / 2.0
	    slave_power += signed_error / 2.0	

	    self._set_power_directional(LEFT, int(master_power))
	    self._set_power_directional(RIGHT, int(slave_power))
	    
	    #print "l: %3.0f r: %3.0f lt: %2.0f rt: %2.0f d: %2.0f dst: %3.0fcm?" % (master_power, slave_power, self.left_encoder.getTicks(), self.right_encoder.getTicks(), signed_error, distance_travelled)
	    distance_travelled += (self.left_encoder.getCurrentDistance() + self.right_encoder.getCurrentDistance()) / 2.0

            left_distance += self.left_encoder.getCurrentDistance()
            right_distance += self.right_encoder.getCurrentDistance()
            print "platform.drive_straight: left=%f, right=%f" % (left_distance,right_distance)
	    
	    self.left_encoder.resetTicks()
	    self.right_encoder.resetTicks()

	    sleep(self.delay)

        self.position_tracker.update(left_distance, right_distance)

        self.shutdown()

    def turn(self, theta):
        CUSTOM_TIME_DELAY   = 0.005
        LEFT_TICK_RATIO     = 16.5/87.0
        RIGHT_TICK_RATIO    = 17.25/87.0

        left_tick_goal      = abs(LEFT_TICK_RATIO * theta)
        right_tick_goal     = abs(RIGHT_TICK_RATIO * theta)
        left_ticks_to_goal  = left_tick_goal
        right_ticks_to_goal = right_tick_goal

        self.left_encoder.resetTicks()
        self.right_encoder.resetTicks()

        if theta > 0:
            left_power  = 70
            right_power = -80
        elif theta < 0:
            left_power  = -80
            right_power = 70
        else:
            return

        self._set_power_directional(LEFT, int(left_power))
        self._set_power_directional(RIGHT, int(right_power))

        while left_ticks_to_goal > 0 or right_ticks_to_goal > 0:
            left_ticks = self.left_encoder.getTicks()
            left_ticks_to_goal = left_tick_goal - left_ticks

            right_ticks = self.right_encoder.getTicks()
            right_ticks_to_goal = right_tick_goal - right_ticks

            ticks_to_goal_diff = left_ticks_to_goal - right_ticks_to_goal
            if ticks_to_goal_diff > 1:
                left_ticks_to_goal -= 1
                right_ticks_to_goal += 1
            elif ticks_to_goal_diff < -1:
                left_ticks_to_goal += 1
                right_ticks_to_goal -= 1
            
            #print "left encoder ticks: %3d, right encoder ticks: %3d" % (self.left_encoder.getTicks(), self.right_encoder.getTicks())
            sleep(CUSTOM_TIME_DELAY)

        
        print "left tick   goal:  %5.2f, right tick   goal:  %5.2f" % (left_tick_goal, right_tick_goal)
        print "left actual ticks: %5.2f, right actual ticks: %5.2f" % (self.left_encoder.getTicks(), self.right_encoder.getTicks())
        self.shutdown()

        '''
        left_tick_goal = 0.2 * abs(theta)
        right_tick_goal = 0.22 * abs(theta)

        self.left_encoder.resetTicks()
        self.right_encoder.resetTicks()

        if theta >= 0:
            left_power, right_power = 100, -100
        else:
            left_power, right_power = -100, 100
        
        self._set_power_directional(LEFT, int(left_power))
        self._set_power_directional(RIGHT, int(right_power))
        
        while self.left_encoder.getTicks() < left_tick_goal or self.right_encoder.getTicks() < right_tick_goal:
            print "ticks diff: %2d - %2d = %2d" % (self.left_encoder.getTicks(), self.right_encoder.getTicks(), self.left_encoder.getTicks() - self.right_encoder.getTicks())
            sleep(self.delay)

        left_distance = self.left_encoder.getCurrentDistance() * sign(theta)
        right_distance = self.right_encoder.getCurrentDistance() * sign(theta) * -1
        #print "platform.turn: updating PositionTracker with left=%f, right=%f" % (left_distance, right_distance)
        self.position_tracker.update(left_distance, right_distance)

        print "left encoder ticks: %3d, right encoder ticks: %3d" % (self.left_encoder.getTicks(), self.right_encoder.getTicks())
        self.shutdown()
        '''

if __name__ == '__main__':
    print "Motor Testing"

    platform = Platform()
    atexit.register(platform.shutdown)

    #print "platform state BEFORE:\t", platform.get_state()
    #platform.turn(90)
    platform.turn(-90)
    #platform.turn(180)
    #platform.turn(360)
    sleep(0.5)
    #print "platform state AFTER:\t", platform.get_state()
