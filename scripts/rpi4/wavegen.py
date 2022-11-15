import RPi.GPIO as GPIO
import numpy as np

#
### HOW TO CHANGE THE GPIO DRIVER STRENGTH: ###
# Initialize comms: sudo pigpiod
# Read/Get driver strength from Pad 0 (GPIOs 0-27): pigs padg 0
# Set driver strength of Pad 0 to X mA: pigs pads 0 X


### FORMAT OF PTS BIT SIGNIFICANCE: ###
# 2^3  2^2  2^1  2^0
#  8    4    2    1

# pts_pins_1GHz = [44, 43]
# pts_pins_100MHz = [41, 40, 16, 15]
# pts_pins_10MHz = [20, 19, 18, 17]
# pts_pins_1MHz = [27, 26, 2, 1]
# pts_pins_100kHz = [29, 28, 4, 3]
# pts_pins_10kHz = [31, 30, 6, 5]
# pts_pins_1kHz = [33, 32, 8, 7]
# pts_pins_100Hz = [35]
# pts_pins_10Hz= []
# pts_pins_1Hz = []

# pts_pins = [pts_pins_1GHz, 
#             pts_pins_100MHz, pts_pins_10MHz, pts_pins_1MHz, 
#             pts_pins_100kHz, pts_pins_10kHz, pts_pins_1kHz, 
#             pts_pins_100Hz, pts_pins_10Hz, pts_pins_1Hz]

# pts_pins_LE = [23, 24, 25, 26]
# pts_pins_remote = [42]


# gpio_pins_1GHz = [26, 25]
# gpio_pins_100MHz = [24, 23, 22, 21]
# gpio_pins_10MHz = [20, 19, 18, 17]
# gpio_pins_1MHz = [16, 15, 14, 13]
# gpio_pins_100kHz = [12, 11, 10, 9]
# gpio_pins_10kHz = [8, 7, 6, 5]
# gpio_pins_1kHz = [4, 3, 2, 1]
# gpio_pins_100Hz = [0]
# gpio_pins_10Hz = []
# gpio_pins_1Hz = []

# gpio_pins = [gpio_pins_1GHz, 
#              gpio_pins_100MHz, gpio_pins_10MHz, gpio_pins_1MHz, 
#              gpio_pins_100kHz, gpio_pins_10kHz, gpio_pins_1kHz, 
#              gpio_pins_100Hz, gpio_pins_10Hz, gpio_pins_1Hz]

# gpio_pins_LE = [26]
# gpio_pins_remote = [27]
# # LATCH ENABLE AND REMOTE ARE NOT NEEDED ANYMORE -- HARDCODED 


# GPIO pins
gpio_data_pin = 23 # data pin
gpio_sclk_pin = 22 # serial clock pin
gpio_pclk_pin = 24 # parallel clock pin
gpio_pins = [gpio_data_pin, gpio_sclk_pin, gpio_pclk_pin] # all GPIOs


def convert_to_bins(frequency):
    """
    Convert a given input into its binary counterpart.

    Inputs:
        - frequency (int)|[Hz] - Input frequency
    Returns:
        - A list of len 10 (for 10 decimal places from Hz to GHz),
          with each element in the list containing a binary nibble,
          with the exception of the GHz element, which contains a
          half-nibble (in accordance with PTS3200 frequency limits).
    """
    frequency = int(np.round(frequency)) # fractions not allowed -- round and make an integer value
    if frequency > 3199999999 or frequency < 0: # upper and lower frequency bounds 
        raise ValueError('Input frequency is outside of bounds: 0Hz to 3,199,999,999Hz')
    frequency = str(frequency).zfill(10)
    freq = [int(n) for n in frequency]
    binary_numbers = []
    for i, n in enumerate(freq):
        if i == 0: # XXX MAKE SURE INVERSION ISNT A PROBLEM
            w = 2 # PTS only has two signigicant bits for GHz
        else:
            w = 4
        bin_num = np.binary_repr(n, width=w)
        binary_numbers.append(bin_num)
    return binary_numbers


def shift_in_new_freq(binary_numbers):
    """
    Reads a set of binary converted frequency values and 
    loads the data into the appropriate GPIO pin.

    Inputs:
        - binary_numbers: list of 10 nibbles containing
          frequency information
    """
    split_binary_numbers = []
    for num in binary_numbers:
        split = [int(n) for n in num]
        split_binary_numbers.append(split)
    GPIO.output(gpio_sclk_pin, GPIO.HIGH) # set serial clk to off state
    GPIO.output(gpio_pclk_pin, GPIO.HIGH) # set parallel clk to off state
    bit_cnt = 0
    for i in range(9, -1, -1): # count from most to least significant bit
        for j in range(len(split_binary_numbers[i])-1, -1, -1):
            if split_binary_numbers[i][j] == 0:
                print('Shifting in a 0 at', bit_cnt)
                GPIO.output(gpio_data_pin, GPIO.LOW)
            elif split_binary_numbers[i][j] == 1:
                print('Shifting in a 1 at', bit_cnt)
                GPIO.output(gpio_data_pin, GPIO.HIGH)
            # XXX User interaction for bit by bit input for debugging and probing
            GPIO.output(gpio_sclk_pin, GPIO.LOW)
            GPIO.output(gpio_sclk_pin, GPIO.HIGH) # XXX needed??
            bit_cnt += 1 


def send_command():
    """
    Triggers send of frequency from RPi to PTS.
    """
    # User interaction so we have control over change -- Verbose commands
    GPIO.output(gpio_pclk_pin, GPIO.LOW) # triggers send to PTS
    GPIO.output(gpio_pclk_pin, GPIO.HIGH) # return parallel clock to off state


def continous_wave(freq):
    """
    Generates a continuous wave of a specified frequency.
    
    Inputs:
        - freq (int)|[Hz]: Desired frequency
    """
    binary_list = convert_to_bins(freq) # convert freq from decimal to binary
    shift_in_new_freq(binary_list) # load data to GPIO
    send_command() # send data to PTS


def dummy_routine():
    """
    Temporary test function.
    """
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
    """
    Initializes the RPi4 GPIOs for use.
    """
    GPIO.setmode(GPIO.BCM) # use GPIO numbers, rather than rpi pin numbers
    GPIO.setwarnings(False) # ingore internal messaging
    # define GPIO pins as outputs
    GPIO.setup(gpio_pins, GPIO.OUT)

def cleanup_gpio():
    """
    Cleanup GPIOs to ensure no damage is done to RPi.
    """
    GPIO.cleanup()
