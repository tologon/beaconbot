from Adafruit_MotorHAT import *
from WheelEncoder import WheelEncoder
from position_tracker import *
from numpy import sign,arctan2,sqrt
from time import sleep
import atexit
import sys
from math import pi as PI

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

        # TEST VALUE
        #self.inter_wheel_distance = 5.75
        self.inter_wheel_distance = 14.67

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

    def reset(self):
        self.position_tracker.reset()

    def x(self):
        return self.get_state()[0]

    def y(self):
        return self.get_state()[1]

    def theta(self):
        return self.get_state()[2]

    def get_state(self):
        return self.position_tracker.getState()

    def shutdown(self):
        for motor in range(1, 5):
            self.motor_hat.getMotor(motor).run(Adafruit_MotorHAT.RELEASE)
        self._set_power_directional(LEFT, 0)
        self._set_power_directional(RIGHT, 0)

    def go_to_point(self, x, y):
        my_x, my_y, my_theta = self.get_state()
        delta_x = x-my_x
        delta_y = y-my_y

        to_turn = arctan2(delta_y, delta_x) - my_theta

        while to_turn > PI:
            to_turn -= 2*PI
        while to_turn < -1*PI:
            to_turn += 2*PI

        to_drive = sqrt((delta_x)**2+(delta_y)**2)

        self.turn(to_turn)
        sleep(1)
        self.drive_straight(to_drive)

    def drive_straight(self, distance_to_travel):
        initial_power = 130
	master_power = initial_power#-15  # left encoder
	slave_power  = initial_power#+4   # right encoder
	onetick_power_change = 4

        left_distance = 0
        right_distance = 0

	distance_travelled = 0

	while distance_travelled < distance_to_travel:
#	    signed_error = (self.left_encoder.getTicks() - self.right_encoder.getTicks()) * onetick_power_change
             
	    
#	    master_power -= signed_error / 2.0
#	    slave_power += signed_error / 2.0	

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

    def turn(self, radians):
        if abs(radians) <= PI/2:
            MULTIPLIER = 1.0
        elif abs(radians) > PI/2 and abs(radians) <= PI:
            MULTIPLIER = 1.1112
        else:
            MULTIPLIER = 1.115

        CUSTOM_TIME_DELAY   = 0.0005
        LEFT_TICK_RATIO     = (16.5/1.518)*MULTIPLIER
        RIGHT_TICK_RATIO    = (17.4/1.518)*MULTIPLIER

        left_tick_goal      = abs(LEFT_TICK_RATIO * radians)
        right_tick_goal     = abs(RIGHT_TICK_RATIO * radians)
        left_ticks_to_goal  = left_tick_goal
        right_ticks_to_goal = right_tick_goal

        self.left_encoder.resetTicks()
        self.right_encoder.resetTicks()

        if radians > 0:
            left_power  = -90
            right_power = 100
        elif radians < 0:
            left_power  = 90
            right_power = -100
        else:
            return

        self._set_power_directional(LEFT, int(left_power))
        self._set_power_directional(RIGHT, int(right_power))

        # in radians
        #angle = 0
        while left_ticks_to_goal > 0 or right_ticks_to_goal > 0:
            sleep(CUSTOM_TIME_DELAY)
            
            left_ticks = self.left_encoder.getTicks()
            left_ticks_to_goal = left_tick_goal - left_ticks

            right_ticks = self.right_encoder.getTicks()
            right_ticks_to_goal = right_tick_goal - right_ticks

            if not (left_ticks_to_goal > 0 or right_ticks_to_goal > 0):
                break

            ticks_to_goal_diff = left_ticks_to_goal - right_ticks_to_goal
            if ticks_to_goal_diff > 1:
                left_ticks_to_goal -= 1
                right_ticks_to_goal += 1
            elif ticks_to_goal_diff < -1:
                left_ticks_to_goal += 1
                right_ticks_to_goal -= 1
            
            #angle = ((self.right_encoder.getCurrentDistance() - self.left_encoder.getCurrentDistance())/self.inter_wheel_distance)
            #print "angle: %4.2f radians" % (angle)
            #print "left encoder ticks: %3d, right encoder ticks: %3d" % (self.left_encoder.getTicks(), self.right_encoder.getTicks())
            self._set_power_directional(LEFT, int(left_power))
            self._set_power_directional(RIGHT, int(right_power))
        
        print "left tick   goal:  %5.2f, right tick   goal:  %5.2f" % (left_tick_goal, right_tick_goal)
        print "left actual ticks: %5.2f, right actual ticks: %5.2f" % (self.left_encoder.getTicks(), self.right_encoder.getTicks())

        left_distance = self.left_encoder.getCurrentDistance() * sign(radians)
        right_distance = self.right_encoder.getCurrentDistance() * sign(radians) * -1
        print "platform.turn: updating PositionTracker with left=%3.2fcm, right=%3.2fcm" % (left_distance, right_distance)
        self.position_tracker.update(left_distance, right_distance)

        self.shutdown()

if __name__ == '__main__':
    print "Motor Testing"

    platform = Platform()
    atexit.register(platform.shutdown)
    
    if len(sys.argv) == 1:
        degrees = 90
    else:
        degrees = int(sys.argv[1])

    radians = math.radians(degrees)
    print "degrees: %3d, radians: %3.2f" % (degrees, radians)

    print "platform state BEFORE:\t", platform.get_state()
    platform.turn(radians)
    sleep(0.5)
    print "platform state AFTER:\t", platform.get_state()
