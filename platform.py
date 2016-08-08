import atexit
import sys

from Adafruit_MotorHAT import *
from beacon import *
from distance_sensor import *
from math import pi as PI
from numpy import sign,arctan2,sqrt
from position_tracker import *
from time import sleep
from wheel_encoder import WheelEncoder

LEFT = 'LEFT'
RIGHT = 'RIGHT'

class Platform(object):
    def __init__(self, right_motor_pin=1, right_encoder_pin=21, left_motor_pin=2, left_encoder_pin=20, beacon_ssid='0c:f3:ee:04:22:3d', delay=0.05):
        self.motor_hat = Adafruit_MotorHAT(addr=0x60)

        # DO NOT CHANGE THOSE VALUES
        # REQUIRED VALUES FOR CORRECT TURNING (WITH UP TO 5 DEGREE ACCURACY):
        # self.left_trim    = -7
        # self.right_trim   = 6
        self.left_trim = -6
        self.right_trim = 8
        self.obstacle_minimum_dist = 40

        self.inter_wheel_distance = 14.67

        self.right_motor = self.motor_hat.getMotor(right_motor_pin)
        self.right_encoder = WheelEncoder(right_encoder_pin, 20, 1.625)

        self.left_motor = self.motor_hat.getMotor(left_motor_pin)
        self.left_encoder = WheelEncoder(left_encoder_pin, 20, 1.625)

        self.right_state = Adafruit_MotorHAT.RELEASE
        self.left_state  = Adafruit_MotorHAT.RELEASE

        self.position_tracker= PositionTracker(self.inter_wheel_distance)
        self.beacon_sensor = BeaconSensor(beacon_ssid)

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

    def get_beacon_distance(self, time):
        self.beacon_sensor.scan(time)
        return self.beacon_sensor.get_distance()

    def reset_beacon_sensor(self):
        self.beacon_sensor.reset()

    def get_forward_distance(self):
        return ultrasonic_distance(delay=0.001)

    def go_to_point(self, x, y):
        my_x, my_y, my_theta = self.get_state()
        print "Going to %f, %f" % (x, y)
        delta_x = x-my_x
        delta_y = y-my_y

        to_turn = arctan2(delta_y, delta_x) - my_theta

        while to_turn > PI:
            to_turn -= 2*PI
        while to_turn < -1*PI:
            to_turn += 2*PI

        to_drive = sqrt((delta_x)**2+(delta_y)**2)

        self.turn(to_turn)

        sleep(0.3)

        self.drive_straight(to_drive)

    def drive_straight(self, distance_to_travel):
        initial_power = 130
        master_power = initial_power-8  # left encoder
        slave_power  = initial_power+3   # right encoder

        left_distance = 0
        right_distance = 0

        self.left_encoder.resetTicks()
        self.right_encoder.resetTicks()
        last_beacon_dist = self.get_beacon_distance(self.delay)
        while ((self.left_encoder.getCurrentDistance() + self.right_encoder.getCurrentDistance()) / 2.0) < distance_to_travel:
            self._set_power_directional(LEFT, int(master_power))
            self._set_power_directional(RIGHT, int(slave_power))

            #print "lpower: %3.0f rpower: %3.0f ldist: %2.0f rdist: %2.0f dst: %3.0fcm?" % (master_power, slave_power, self.left_encoder.getCurrentDistance(), self.right_encoder.getCurrentDistance(), distance_travelled)
            #print "platform.drive_straight: left=%f, right=%f" % (left_distance,right_distance)
            # Break if we encounter an obstacle
            forward_dist = self.get_forward_distance()
            if forward_dist >=6 and forward_dist <= self.obstacle_minimum_dist:
                print "Forward distance: %f" % forward_dist
                break

            # Break if we're moving away from the beacon
            beacon_dist = self.get_beacon_distance(0.01)
            if beacon_dist > last_beacon_dist*1.1:
                print "Stopping, beacon dist increased by %f" % (beacon_dist - last_beacon_dist)
                break
            last_beacon_dist = beacon_dist

        left_distance = self.left_encoder.getCurrentDistance()
        right_distance = self.right_encoder.getCurrentDistance()
        self.position_tracker.update(left_distance, right_distance)
        self.shutdown()

    def turn(self, radians):
        # multiplier is a correction multiplier for angle;
        # the bigger the turn, the more ticks needs to happen (hence multiplier presence)
        if abs(radians) <= PI/2:
            multiplier = 1.0
        elif abs(radians) > PI/2 and abs(radians) <= PI:
            multiplier = 1.1112
        else:
            multiplier = 1.115

        # Need a custom time delay to ensure # of encoders' ticks counted correctly
        custom_time_delay   = 0.0005
        # Values obtained via experiments, might be changed if needed
        left_tick_ratio     = (16.5/1.518)*multiplier
        right_tick_ratio    = (17.4/1.518)*multiplier

        left_tick_goal      = abs(left_tick_ratio * radians)
        right_tick_goal     = abs(right_tick_ratio * radians)
        left_ticks_to_goal  = left_tick_goal
        right_ticks_to_goal = right_tick_goal

        self.left_encoder.resetTicks()
        self.right_encoder.resetTicks()

        # Set the powers to motors based off radians' value
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

        # Debug code
        # angle (in radians)
        #angle = 0
        while left_ticks_to_goal > 0 or right_ticks_to_goal > 0:
            sleep(custom_time_delay)
            
            left_ticks = self.left_encoder.getTicks()
            left_ticks_to_goal = left_tick_goal - left_ticks

            right_ticks = self.right_encoder.getTicks()
            right_ticks_to_goal = right_tick_goal - right_ticks

            # Inverse of the while loop clause in case goal is reached
            # and the beaconbot needs to stop turning
            if not (left_ticks_to_goal > 0 or right_ticks_to_goal > 0):
                break

            ticks_to_goal_diff = left_ticks_to_goal - right_ticks_to_goal
            if ticks_to_goal_diff > 1:
                left_ticks_to_goal -= 1
                right_ticks_to_goal += 1
            elif ticks_to_goal_diff < -1:
                left_ticks_to_goal += 1
                right_ticks_to_goal -= 1
            
            # Debug code
            #angle = ((self.right_encoder.getCurrentDistance() - self.left_encoder.getCurrentDistance())/self.inter_wheel_distance)
            #print "angle: %4.2f radians" % (angle)
            #print "left encoder ticks: %3d, right encoder ticks: %3d" % (self.left_encoder.getTicks(), self.right_encoder.getTicks())
        
        # Debug code
        #print "left tick   goal:  %5.2f, right tick   goal:  %5.2f" % (left_tick_goal, right_tick_goal)
        #print "left actual ticks: %5.2f, right actual ticks: %5.2f" % (self.left_encoder.getTicks(), self.right_encoder.getTicks())

        left_distance = self.left_encoder.getCurrentDistance() * sign(radians)
        right_distance = self.right_encoder.getCurrentDistance() * sign(radians) * -1
        # Debug code
        #print "platform.turn: updating PositionTracker with left=%3.2fcm, right=%3.2fcm" % (left_distance, right_distance)
        self.position_tracker.update(left_distance, right_distance)

        self.shutdown()

if __name__ == '__main__':
    print "Motor Testing"

    platform = Platform()
    atexit.register(platform.shutdown)
    
    #if len(sys.argv) == 1:
    #    degrees = 90
    #else:
    x = int(sys.argv[1])
    y = int(sys.argv[2])

    #radians = math.radians(degrees)
    #print "degrees: %3d, radians: %3.2f" % (degrees, radians)

    #print "platform state BEFORE:\t", platform.get_state()
    platform.drive_straight(x)
    #sleep(0.5)
    #print "platform state AFTER:\t", platform.get_state()
