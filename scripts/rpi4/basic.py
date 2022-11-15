import RPi.GPIO as GPIO
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

pts_pins_1GHz = [44, 43]
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


gpio_pins_1GHz = [26, 25]
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
# LATCH ENABLE AND REMOTE ARE NOT NEEDED ANYMORE -- HARDCODED 



def convert_to_bins(frequency):
    """ Frequency in Hz. Int input (no floats) """
    if frequency > 3199999999 or frequency < 0: # upper and lower frequency bounds 
        raise ValueError('Input frequency is outside of bounds: 0Hz to 3,199,999,999Hz')
    # VALUE ERROR / TRUNCATE / ROUND FOR FRACTIONS
    frequency = str(frequency).zfill(10)
    freq = [int(n) for n in frequency]
    # if freq[-1] != 0 or freq[-2] != 0: # frequency resolution
    #     raise ValueError('Finest frequency resolution is 800Hz.')
    binary_numbers = []
    for i, n in enumerate(freq):
        if i == 0: # MAKE SURE INVERSION ISNT A PROBLEM
            w = 2
        else:
            w = 4
        bin_num = np.binary_repr(n, width=w)
        binary_numbers.append(bin_num)
    return binary_numbers


def shift_in_new_freq(binary_numbers):
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
    
    GPIO.output(gpio_sclk_pin, GPIO.HIGH) # set serial clk to off state
    GPIO.output(gpio_pclk_pin, GPIO.HIGH) # set parallel clk to off state -- NEW VARIABLE GPIO 24
    
    bit_cnt = 0
    for i in range(10, 0):
        for j in range(len(split_binary_numbers[i]), 0): # XXX
            if split_binary_numbers[i][j] == 0:
                print('Shifting in a 0 at', bit_cnt) #, gpio_pins[i][j])
                GPIO.output(gpio_data_pin, GPIO.LOW) # NEW VARIABLE GPIO 23
            elif split_binary_numbers[i][j] == 1:
                print('Shifting in a 1 at', bit_cnt) #, gpio_pins[i][j])
                GPIO.output(gpio_data_pin, GPIO.HIGH)
            
            # User interaction for bit by bit input for debugging and probing
            GPIO.output(gpio_sclk_pin, GPIO.LOW) # NEW VARIABLE GPIO 22
            GPIO.output(gpio_sclk_pin, GPIO.HIGH) 
           
            bit_cnt += 1 


def activate_freq():
    # User interaction so we have control over change
    GPIO.output(gpio_pclk_pin, GPIO.LOW) # MAGIC: triggers send to PTS
    GPIO.output(gpio_pclk_pin, GPIO.HIGH) # return parallel clk to off (safe) state




def continous_wave(freq):
    binary_list = convert_to_bins(freq)
    shift_in_new_freq(binary_list)
    activate_freq()


def dummy_routine():
    freq1 = 1400000000
    freq2 =  985623274 
    cnt1 = 0 
    cnt2 = 0
    while True:
        continuous_wave(freq1)
        for n in range(2400): # wait about 1 ms
            cnt1 += 1
        continuous_wave(freq2) # wait about 1 ms
        for n in range(2400):
            cnt2 += 1

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
