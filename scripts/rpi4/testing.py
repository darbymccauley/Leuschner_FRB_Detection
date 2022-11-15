# import numpy as np
import RPi.GPIO as GPIO
# import sys
# from time import sleep


# Set up pin to be used
gpio_pin = 25

# Count to N
N = 2400

# Initialize use of GPIOs
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(gpio_pin, GPIO.OUT) # set the pin to be an output

while True:
    GPIO.output(gpio_pin, GPIO.HIGH)
    # print('Changed low')
    cnt = 0
    for n in range(N):
        cnt += 1
    GPIO.output(gpio_pin, GPIO.LOW)
    # print('Changed high')
    cnt = 0
    for n in range(N):
        cnt += 1
