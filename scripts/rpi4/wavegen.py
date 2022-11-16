import RPi.GPIO as GPIO
import numpy as np


### HOW TO CHANGE THE GPIO DRIVER STRENGTH: ###
# Initialize comms: sudo pigpiod
# Read/Get driver strength from Pad 0 (GPIOs 0-27): pigs padg 0
# Set driver strength of Pad 0 to X mA: pigs pads 0 X



# GPIO pins
gpio_data_pin = 23 # data pin
gpio_sclk_pin = 22 # serial clock pin
gpio_pclk_pin = 24 # parallel clock pin
gpio_pins = [gpio_data_pin, gpio_sclk_pin, gpio_pclk_pin] # all GPIOs


def convert_to_bins(frequency, model='PTS3200'):
    """
    Convert a given input into its binary counterpart.

    Inputs:
        - frequency (int)|[Hz]: Input frequency
        - model (str): PTS model used. Default is PTS3200.
          Accepts PTS3200, PTS500, PTS300.
    Returns:
        - A list of len 10 (for 10 decimal places from GHz to Hz),
          with each element in the list containing a binary nibble.
          This corresponds to a 40-bit total. The nibbles read from
          most to least significant bit.
    """
    frequency = int(np.round(frequency)) # fractions not allowed -- round and make an integer value
    if model == 'PTS3200':
        max_freq = 3199999999
        min_freq = 0
    elif model == 'PTS500': 
        max_freq = 500000000
        min_freq = 0
    else: # assume PTS300
        max_freq = 300000000
        min_freq = 0
    if frequency > max_freq or frequency < min_freq: # upper and lower frequency bounds 
        raise ValueError('Input frequency is outside of bounds') # XXX add bounds+model to this print statement
    frequency = str(frequency).zfill(10)
    freq = [int(n) for n in frequency]
    binary_numbers = []
    for i, n in enumerate(freq):
        bin_num = np.binary_repr(n, width=4)
        binary_numbers.append(bin_num)
    return binary_numbers


def load_frequency(binary_numbers):
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
            usleep(2) # let the data settle before pulsing clk

            GPIO.output(gpio_sclk_pin, GPIO.LOW)
            usleep(2) # stretch out clk pulse to be conservative
            GPIO.output(gpio_sclk_pin, GPIO.HIGH) 
            bit_cnt += 1
    

def send_command():
    """
    Triggers send of frequency from RPi to PTS.
    """
    # User interaction so we have control over change -- Verbose commands
    GPIO.output(gpio_pclk_pin, GPIO.LOW) # triggers send to PTS
    GPIO.output(gpio_pclk_pin, GPIO.HIGH) # return parallel clock to off state


def continuous_wave(freq):
    """
    Generates a continuous wave of a specified frequency.
    
    Inputs:
        - freq (int)|[Hz]: Desired frequency
    """
    binary_list = convert_to_bins(freq) # convert freq from decimal to binary
    load_frequency(binary_list) # load data to GPIO
    usleep(2) # conservative wait after data as been serially shifted before doing parallel load
    send_command() # send data to PTS


def test_frequency_switches():
    """
    Temporary test function.
    """
    freq1 = 1400000000
    freq2 =  985623274 
    cnt1 = 0 
    cnt2 = 0
    while True:
        continuous_wave(freq1)
        usleep(1000) # wait 1ms
        continuous_wave(freq2) 
        usleep(1000) # wait 1ms


def initialize_gpio():
    """
    Initializes the RPi4 GPIOs for use.
    """
    GPIO.setmode(GPIO.BCM) # use GPIO numbers, rather than rpi pin numbers
    GPIO.setwarnings(False) # ingore internal messaging
    # define GPIO pins as outputs
    GPIO.setup(gpio_pins, GPIO.OUT)
    # set initial level of GPIO pins
    GPIO.output(gpio_data_pin, GPIO.LOW)
    GPIO.output(gpio_sclk_pin, GPIO.HIGH)
    GPIO.output(gpio_pclk_pin, GPIO.HIGH)


def cleanup_gpio():
    """
    Cleanup GPIOs to ensure no damage is done to RPi.
    """
    GPIO.cleanup()


def usleep(time):
    """
    Sleep for a given number of microseconds.
    WARNING: Needs to be calibrated according to used hardware.
    (Current rough estimate for RPi4 + PTS3200: 2400 cnts = 1 ms)

    Inputs:
        - time [us]: time of delay
    """
    # Convert time to count number, N
    const = 2400/1e3
    N = int(np.round(const*time))
    cnt = 0
    for i in range(N):
        cnt += 1


def blank():
    """
    Clear signal, reset to 0 Hz, and reset clocks.
    """
    N = 50
    GPIO.output(gpio_sclk_pin, GPIO.HIGH) # set off
    for j in range(2):
        for i in range(N):
            GPIO.output(gpio_sclk_pin, GPIO.LOW)
            GPIO.output(gpio_sclk_pin, GPIO.HIGH)
        send_command()
    
