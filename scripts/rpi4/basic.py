import RPi.GPIO as GPIO
from time import sleep
import numpy as np

### HOW TO CHANGE THE GPIO DRIVER STRENGTH: ###
# Initialize comms: sudo pigpiod
# Read/Get driver strength from Pad 0 (GPIOs 0-27): pigs padg 0
# Set driver strength of Pad 0 to X mA: pigs pads 0 X


# binary_numbers[0] --> GHz
# binary_numbers[1] --> 100 MHz
# binary_numbers[2] --> 10 MHz
# binary_numbers[3] --> 1 MHz
# binary_numbers[4] --> 100 kHz
# binary_numbers[5] --> 10 kHz
# binary_numbers[6] --> 1 kHz
# binary_numbers[7] --> 100 Hz


### FORMAT OF PTS/GPIO PINS: ###
# 2^3  2^2  2^1  2^0
#  8    4    2    1

pts_pins_1GHz = [43]
pts_pins_100MHz = [41, 40, 16, 15]
pts_pins_10MHz = [20, 19, 18, 17]
pts_pins_1MHz = [27, 26, 2, 1]
pts_pins_100kHz = [29, 28, 4, 3]
pts_pins_10kHz = [31, 30, 6, 5]
pts_pins_1kHz = [33, 32, 8, 7]
pts_pins_100Hz = [35]
pts_pins_10Hz= []
pts_pins_1Hz = []

pts_pins = [pts_pins_1GHz, 
            pts_pins_100MHz, pts_pins_10MHz, pts_pins_1MHz, 
            pts_pins_100kHz, pts_pins_10kHz, pts_pins_1kHz, 
            pts_pins_100Hz, pts_pins_10Hz, pts_pins_1Hz]

pts_pins_LE = [23, 24, 25, 26]
pts_pins_remote = [42]


gpio_pins_1GHz = [25]
gpio_pins_100MHz = [24, 23, 22, 21]
gpio_pins_10MHz = [20, 19, 18, 17]
gpio_pins_1MHz = [16, 15, 14, 13]
gpio_pins_100kHz = [12, 11, 10, 9]
gpio_pins_10kHz = [8, 7, 6, 5]
gpio_pins_1kHz = [4, 3, 2, 1]
gpio_pins_100Hz = [0]
gpio_pins_10Hz = []
gpio_pins_1Hz = []

gpio_pins = [gpio_pins_1GHz, 
             gpio_pins_100MHz, gpio_pins_10MHz, gpio_pins_1MHz, 
             gpio_pins_100kHz, gpio_pins_10kHz, gpio_pins_1kHz, 
             gpio_pins_100Hz, gpio_pins_10Hz, gpio_pins_1Hz]

gpio_pins_LE = [26]
gpio_pins_remote = [27]



def convert_to_bins(frequency):
    """ Frequency in Hz. Int input (no floats) """
    if frequency > 1999999800 or frequency < 0: # upper and lower frequency bounds 
        raise ValueError('Input frequency is outside of bounds: 0Hz to 1,999,999,800Hz')
    frequency = str(frequency).zfill(10)
    freq = [int(n) for n in frequency]
    if freq[-1] != 0 or freq[-2] != 0: # frequency resolution
        raise ValueError('Finest frequency resolution is 800Hz.')
    binary_numbers = []
    for i, n in enumerate(freq):
        if i == 0 or i == 7:
            w = 1
        else:
            w = 4
        bin_num = np.binary_repr(n, width=w)
        binary_numbers.append(bin_num)
    return binary_numbers


def toggle_gpios(binary_numbers):
    # A GPIO pin designated as an output pin can be set to HIGH (3.3V) 
    # or LOW (0V). A GPIO pin that is designated as an input will allow
    # a signal to be received by the RPi. The threshold between a high 
    # and a low signal is around 1.8V. A voltage between 1.8V and 3.3V 
    # will be read as high; anything lower than 1.8V will be read as low.
    # Do not allow an input voltage above 3.3V, or else you will fry your
    # RPi.
    split_binary_numbers = []
    for num in binary_numbers:
        split = [int(n) for n in num]
        split_binary_numbers.append(split)
        
    for i in range(0, 8):
        for j in range(len(split_binary_numbers[i])):
            if split_binary_numbers[i][j] == 0:
                print('DISabling GPIO pin', gpio_pins[i][j])
                GPIO.output(gpio_pins[i][j], GPIO.LOW)
            elif split_binary_numbers[i][j] == 1:
                print('ENabling GPIO pin', gpio_pins[i][j])
                GPIO.output(gpio_pins[i][j], GPIO.HIGH)
    
def continous_wave(freq):
    binary_list = convert_to_bins(freq)
    toggle_gpios(binary_list)


def initialize_gpio():
    GPIO.setmode(GPIO.BCM) # uses GPIO numbers, rather than rpi pin numbers
    GPIO.setwarnings(False)
    # set all 0-25 GPIO as output pins
    GPIO.setup([i for i in range(0, 26)], GPIO.OUT)
    # set up remote control to PTS3200
    GPIO.setup(gpio_pins_remote, GPIO.OUT)
    GPIO.output(gpio_pins_remote, GPIO.HIGH)

def cleanup_gpio():
    GPIO.cleanup()
