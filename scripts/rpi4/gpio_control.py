import RPi.GPIO as GPIO
# import time


# Set input mode:
# GPIO.BCM uses GPIO numbers, not pin numbers
# GPIO.BOARD uses pin numbers, not GPIO numbers
GPIO.setmode(GPIO.BOARD) # set mode
mode = GPIO.getmode()
print('GPIO mode in use:'+ str(mode))

GPIO.setwarnings(False) # ignore warnings caused by board revisions

input_chan_list = [] # Add pins/GPIO numbers here that will be input channels
output_chan_list = [] # Add pins/GPIO numbers here that will be output channels

# Set input channels
GPIO.setup(input_chan_list, GPIO.IN)
# Set output channels
GPIO.setup(output_chan_list, GPIO.OUT)

### To read the value of a GPIO pin: GPIO.input(channel)
### This will return either 0/GPIO.LOW/False or 1/GPIO.HIGH/True

# Set the output state of a GPIO pin:
GPIO.output(channel, state)
# where state can be either 0/GPIO.LOW/False or 1/GPIO.HIGH/True

# Cleanup channels so no damage occurs to rpi
GPIO.cleanup()

