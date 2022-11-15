####################################################
# Simple script to create a continuous square wave # 
####################################################

import RPi.GPIO as GPIO
import argparse

parser = argparse.ArgumentParser(description='Make a simple continuous square wave using the GPIO pins of an RPi4.')
parser.add_argument('N', help='Count to N (can be thought of as time/half-period of wave).')
parser.add_argument('gpio_pin', help='GPIO pin on RPi4 to be toggled.')

args = parser.parse_args()
CNT = args.N
GPIO_PIN = args.gpio_pin 
# In testing, GPIO 25 was used, and N=2400 gave approximatly 
# a wave with a period of 1 ms.


# Initialize use of GPIOs
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(GPIO_PIN, GPIO.OUT) # set the pin to be an output

while True:
    GPIO.output(GPIO_PIN, GPIO.HIGH)
    # print('Changed HIGH') # Useful for testing of N
    cnt = 0
    for n in range(N):
        cnt += 1
    GPIO.output(GPIO_PIN, GPIO.LOW)
    # print('Changed LOW') # Useful for testing of N
    cnt = 0
    for n in range(CNT):
        cnt += 1
