from WheelEncoder import WheelEncoder
from Adafruit_MotorHAT import *
from custom_motors import *
import atexit

motor_hat = Adafruit_MotorHAT(addrx=0x60)

def turnOffMotors():
    # diable 4 motors
    for motor in range(1, 5):
        motor_hat.getMotor(motor).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

if __name__ == '__main__':
    left_motor  = motor_hat.getMotor(2)
    right_motor = motor_hat.getMotor(1)

    master_power = 200   # left encoder
    slave_power  = 200   # right encoder

    error = 0
    # Constant of Proportionality
    # needs tuning (until the value is just right)
    kp = 0.2

    left_encoder = WheelEncoder(20, 20, 3.25)
    right_encoder = WheelEncoder(21, 20, 3.25)

    left_encoder.setTicksPerTurn(0)
    right_encoder.setTicksPerTurn(0)

    motors = Motors(right_motor, right_encoder, left_motor, left_encoder)

    while 1:
        motors._set_power_directional(LEFT, master_power)
        motors._set_power_directional(RIGHT, slave_power)

        error = left_encoder.getTicksPerTurn() - right_encoder.getTicksPerTurn()

        slave_power += (error * kp)

        left_encoder.setTicksPerTurn(0)
        right_encoder.setTicksPerTurn(0)

        # repeat loop every 0.01 seconds
        time.sleep(0.01)
