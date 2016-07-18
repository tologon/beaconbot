# libraries
import RPi.GPIO as GPIO
import time
# set GPIO pin numbering
GPIO.setmode(GPIO.BCM)

# frequency (in seconds) = how frequently the distance should be measured
# trigger = trigger pin on GPIO
# echo = echo pin on GPIO
def distance(frequency = 2, trigger = 4, echo = 17):
    # associate given pins with trigger and echo values
    TRIG = trigger
    ECHO = echo

    print "Distance measurement in progress"

    # set trigger as gpio out
    GPIO.setup(TRIG, GPIO.OUT)
    # set echo as gpio in
    GPIO.setup(ECHO, GPIO.IN)

    # set TRIG as LOW
    GPIO.output(TRIG, False)
    print "Waiting For Sensor To Settle"
    time.sleep(frequency)

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

    # TODO: move distance printing into separate function or delete altogether
    if distance > 2 and distance < 400:
        # display distance with 0.5 cm calibration
        print "Distance:", distance - 0.5, "cm"
    elif distance >= 400:
        print "Out Of Range"
    elif distance <= 2:
        print "Too Close"
    print "\n"
    return distance - 0.5

# assuming both distance and speed use same unit of length
def time_left(distance, speed):
    return distance / speed
