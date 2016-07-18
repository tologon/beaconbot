#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
from WheelEncoder import WheelEncoder
from numpy import sign
import motors

import time
import atexit

# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
	mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

m1 = mh.getMotor(1)
m2 = mh.getMotor(2)

def pid_controller(y, yc, h=1, Ti=1, Td=1, Kp=1, u0=0, e0=0):
	"""Calculate System Input using a PID Controller

	Arguments:
	y  .. Measured Output of the System
	yc .. Desired Output of the System
	h  .. Sampling Time
	Kp .. Controller Gain Constant
	Ti .. Controller Integration Constant
	Td .. Controller Derivation Constant
	u0 .. Initial state of the integrator
	e0 .. Initial error

	Make sure this function gets called every h seconds!
	"""
	
	# Step variable
	k = 0

	# Initialization
	ui_prev = u0
	e_prev = e0

	while 1:

		# Error between the desired and actual output
		e = yc - y

		# Integration Input
		ui = ui_prev + 1/Ti * h*e
		# Derivation Input
		ud = 1/Td * (e - e_prev)/h

		# Adjust previous values
		e_prev = e
		ui_prev = ui

		# Calculate input for the system
		u = Kp * (e + ui + ud)
		
		k += 1

		return u	

le = WheelEncoder(20, 32, 3)
re = WheelEncoder(21, 32, 3)
m1.run(Adafruit_MotorHAT.FORWARD)
m2.run(Adafruit_MotorHAT.FORWARD)
motor_controller = motors.Motors(m1, m2)

rdist = 0
ldist = 0
adist = 0

pid_length = 0.1

p = 0.000017
i = 0.001
d = 0.0001

while True:
    rdist1 = re.getCurrentDistance()
    ldist1 = le.getCurrentDistance()
    
    time.sleep(pid_length)

    adist = (rdist+ldist)/2

    rmotor_out = pid_controller(rdist, 200, h=pid_length, Kp=p, Ti=i, Td=d)
    lmotor_out = pid_controller(ldist, 200, h=pid_length, Kp=p, Ti=i, Td=d)

    motor_controller.set_speed('RIGHT', int(rmotor_out))
    motor_controller.set_speed('LEFT', int(lmotor_out))
    print "Total Distance travelled: ",adist,"cm"
    print "Left Distance: ",100*ldist/200.0,"%"
    print "Right Distance: ",100*rdist/200.0,"%"
    print "Left output: ",lmotor_out,"/255"
    print "Right output: ",rmotor_out,"/255"
    print

    rdist2 = re.getCurrentDistance()
    ldist2 = le.getCurrentDistance()

    rdist += (rdist2-rdist1)*sign(motor_controller.get_speed('RIGHT'))
    ldist += (ldist2-ldist1)*sign(motor_controller.get_speed('LEFT'))

print "Done"
motor_controller.set_speed('RIGHT', 0)
motor_controller.set_speed('LEFT', 0)
