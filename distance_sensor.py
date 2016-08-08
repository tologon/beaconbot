# libraries
import RPi.GPIO as GPIO
import time
# set GPIO pin numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# delay (in seconds) = how frequently the distance should be measured
# trigger = trigger pin on GPIO
# echo = echo pin on GPIO
def ultrasonic_distance(delay = 2, trigger = 16, echo = 19):
    # associate given pins with trigger and echo values
    TRIG = trigger
    ECHO = echo

    # set trigger as gpio out
    GPIO.setup(TRIG, GPIO.OUT)
    # set echo as gpio in
    GPIO.setup(ECHO, GPIO.IN)

    # set TRIG as LOW
    GPIO.output(TRIG, False)
    time.sleep(delay)

    # set TRIG as HIGH
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    # set TRIG as LOW
    GPIO.output(TRIG, False)

    # initialize start of the pulse to 0
    pulse_start = 0
    # initialize end of the pulse to 0
    pulse_end = 0

    # check whether the ECHO is LOW
    while GPIO.input(ECHO) == 0:
        # save the last known time of LOW pulse
        pulse_start = time.time()

    # check whether the ECHO is HIGH
    while GPIO.input(ECHO) == 1:
        # save the last known time of HIGH pulse
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start

    MULTIPLIER = 17150
    # multiply pulse duration by multiplier to get distance
    distance = pulse_duration * MULTIPLIER
    distance = round(distance, 2)

    return distance - 0.5

# assuming both distance and speed use same unit of length
def time_left(distance, speed):
    return distance / speed

if __name__ == '__main__':
    while True:
        print ultrasonic_distance(delay=0.0001)
