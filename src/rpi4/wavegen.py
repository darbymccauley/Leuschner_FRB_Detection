import RPi.GPIO as GPIO
import numpy as np
import os


### HOW TO CHANGE THE GPIO DRIVER STRENGTH: ###
# Initialize comms: sudo pigpiod
# Read/Get driver strength from Pad 0 (GPIOs 0-27): pigs padg 0
# Set driver strength of Pad 0 to X mA: pigs pads 0 X

# Set GPIO driver strength 
# os.system('sudo pigpiod') 
# os.system('pigs pads 0 4') # set driver strength of Pad 0 (GPIOs 0-27) to 4 mA


# GPIO pins
GPIO_DATA_PIN = 23 # data pin
GPIO_SCLK_PIN = 22 # serial clock pin
GPIO_PCLK_PIN = 24 # parallel clock pin
# GPIO_PINS = [GPIO_DATA_PIN, GPIO_SCLK_PIN, GPIO_PCLK_PIN]

# PTS model
MODEL = 'PTS3200'

# Rather than zeroing the signal (0 Hz) when a sweep is not occuring,
# we choose a random but easily recognizable frequency for the purpose
# of debugging and ensuring the system is performing as expected. This
# frequency will later be filtered out via a 250 MHz high-pass filter.
NO_SIGNAL = 7.2e6 # Hz

class WaveGen():

    def __init__(self, gpio_data_pin=GPIO_DATA_PIN, gpio_sclk_pin=GPIO_SCLK_PIN, gpio_pclk_pin=GPIO_PCLK_PIN, model=MODEL, no_signal=NO_SIGNAL):
        """
        Instantiate use of PTS and RPi GPIO pins.
        """
        self.model = model
        self.gpio_data_pin = gpio_data_pin
        self.gpio_sclk_pin = gpio_sclk_pin
        self.gpio_pclk_pin = gpio_pclk_pin
        self.gpio_pins = [self.gpio_data_pin, self.gpio_sclk_pin, self.gpio_pclk_pin]
        self.no_signal = no_signal

        GPIO.setwarnings(False) # ignore RPi.GPIO internal messaging
        GPIO.setmode(GPIO.BCM) # use GPIO numbers rather than pin numbers
        # define GPIO pins as outputs
        GPIO.setup(self.gpio_pins, GPIO.OUT)
        # set initial level of GPIO pins
        GPIO.output(self.gpio_data_pin, GPIO.LOW)
        GPIO.output(self.gpio_sclk_pin, GPIO.HIGH)
        GPIO.output(self.gpio_pclk_pin, GPIO.HIGH)


    def _convert_to_bins(self, frequency, model='PTS3200'):
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
        min_freq = 1e6
        if self.model == 'PTS3200':
            max_freq = 3199999999
        elif self.model == 'PTS500': 
            max_freq = 500e6
        else: # assume PTS300
            max_freq = 300e6
        rounded_frequency = int(np.round(frequency)) # fractions not allowed
        if rounded_frequency > max_freq or rounded_frequency < min_freq: # upper and lower frequency bounds 
            print('WARNING: Input frequency {0} is out of range for model {1} ({2} - {3} Hz).'.format(frequency, model, max_freq, min_freq))
            if rounded_frequency > max_freq:
                rounded_frequency = max_freq # set to upper limit
            elif rounded_frequency < min_freq:
                rounded_frequency = min_freq # set to lower limit
        Frequency = str(rounded_frequency).zfill(10)
        freq = [int(n) for n in Frequency]
        binary_numbers = []
        for i, n in enumerate(freq):
            bin_num = np.binary_repr(n, width=4)
            binary_numbers.append(bin_num)
        return binary_numbers


    def _load_frequency(self, binary_numbers):
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
        GPIO.output(self.gpio_sclk_pin, GPIO.HIGH) # set serial clk to off state
        GPIO.output(self.gpio_pclk_pin, GPIO.HIGH) # set parallel clk to off state
        bit_cnt = 0
        for i in range(9, -1, -1): # count from most to least significant bit
            for j in range(len(split_binary_numbers[i])-1, -1, -1):
                if split_binary_numbers[i][j] == 0:
                    # print('Shifting in a 0 at', bit_cnt)
                    GPIO.output(self.gpio_data_pin, GPIO.LOW)
                elif split_binary_numbers[i][j] == 1:
                    # print('Shifting in a 1 at', bit_cnt)
                    GPIO.output(self.gpio_data_pin, GPIO.HIGH)
                # XXX User interaction for bit by bit input for debugging and probing
                self._usleep(2) # let the data settle before pulsing clk

                GPIO.output(self.gpio_sclk_pin, GPIO.LOW)
                self._usleep(5) # stretch out clk pulse to be conservative
                GPIO.output(self.gpio_sclk_pin, GPIO.HIGH) 
                bit_cnt += 1
        

    def _send_command(self):
        """
        Triggers send of frequency from RPi to PTS.
        """
        # User interaction so we have control over change -- Verbose commands XXX
        GPIO.output(self.gpio_pclk_pin, GPIO.LOW) # triggers send to PTS
        GPIO.output(self.gpio_pclk_pin, GPIO.HIGH) # return parallel clock to off state


    def continuous_wave(self, freq):
        """
        Generates a continuous wave of a specified frequency.
        
        Inputs:
            - freq (int)|[Hz]: Desired frequency in decimal representation
        """
        self._make_wave(freq, decimal=True)


    def _convert_freq_list(self, freqs, model='PTS3200'):
        """
        Convert an entire list of frequencies into binary
        in preparation for sweep functions.

        Inputs:
            - freqs [Hz]: list of frequencies (in decimal form)
            - model (str): PTS model used. Default is PTS3200.
              Accepts PTS3200, PTS500, PTS300.
        """
        bin_freqs = [self._convert_to_bins(f, model) for f in freqs]
        return bin_freqs


    def _make_wave(self, freq, decimal=False):
        """
        Load and generate a wave at the specified frequency.

        Inputs:
            - freq [Hz]: Desired frequency
            - decimal (bool): is input freq given in decimal 
              or binary form?
        """
        if decimal: # if frequency is given in decimal form:
            binary_list = self._convert_to_bins(freq) # convert freq from decimal to binary
        else:
            binary_list = freq # already in binary form
        self._load_frequency(binary_list) # load binary data to GPIO
        self._usleep(2) # conservative wait after data has been serially shifted before doing parallel load
        self._send_command() # send data to PTS


    def cleanup_gpio(self):
        """
        Cleanup GPIOs to ensure no damage is done to RPi.
        """
        GPIO.cleanup()


    def _usleep(self, time):
        """
        Sleep for a given number of microseconds.
        WARNING: Needs to be calibrated according to used hardware.
        (Current estimate for RPi4 + PTS3200: 2400 cnts = 1 ms)

        Inputs:
            - time [us]: time of delay
        """
        # Convert time to count number, N
        const = 2400/1e3
        N = int(np.round(const*time))
        cnt = 0
        for i in range(N):
            cnt += 1


    def blank(self):
        """
        Clear signal and reset clocks.
        """
        N = 50
        GPIO.output(self.gpio_sclk_pin, GPIO.HIGH) # set off
        for j in range(2):
            for i in range(N):
                GPIO.output(self.gpio_sclk_pin, GPIO.LOW)
                GPIO.output(self.gpio_sclk_pin, GPIO.HIGH)
            self._send_command()
       


    def linear_sweep(self, f_min=1150e6, f_max=1650e6, nchans= 2048, dt=1000, model='PTS3200', continuous=False):
        """
        Generate a continuous linear (simple) sweep.

        Inputs:
            - f_min (float)|[Hz]: minimum frequency of sweep
            - f_max (float)|[Hz]: maximum frequency of sweep
            - nchans (int): number of frequency channels
            - dt (float)|[us]: time until next frequncy change
            - continuous (bool): single or repeating sweep?
        """
        freqs = np.linspace(f_min, f_max, nchans)
        bin_freqs = self._convert_freq_list(freqs, model)
        while continuous:
            for f in bin_freqs:
                self._make_wave(f)
                self._usleep(dt)
        for f in bin_freqs:
            self._make_wave(f)
            self._usleep(dt)


    def _dm_delay(self, DM, freq):
        """
        Computes the frequency-dependent dispersion measure
        time delay.
        
        Inputs:
            - DM (float)|[pc*cm^-3]: dispersion measure
            - freq (float)|[Hz]: frequency
        Returns: pulse time delay in [us]
        """
        const = 4140
        A = DM*const*1e6 # 1e6 for conversion to us
        return A/((freq/1e6)**2)


    def dm_sweep(self, DM=332.72, f_min=1150e6, f_max=1650e6, dt=1000, model='PTS3200', continuous=False):
        """
        Generates a frequency sweep that mirrors that caused
        by dispersion measure influence.

        Inputs:
            - DM (float)|[pc*cm^-3]: dispersion measure (default 
              is DM for SGR1935+2154)
            - f_min (float)|[Hz]: minimum frequency of sweep
            - f_max (float)|[Hz]: maximum frequency of sweep
            - dt (float)|[us]: sweep update interval
            - model (str): PTS model used. Default is PTS3200.
              Accepts PTS3200, PTS500, PTS300.
            - continuous (bool): single or repeating sweep?
        """
        const = 4140e6
        A = const*DM
        t0 = self._dm_delay(DM, f_max)
        tf = self._dm_delay(DM, f_min)
        ts = np.arange(t0, tf+dt, dt)
        freqs = np.sqrt(A/ts)*1e6 # 1e6 for proper conversion of freqs into Hz -- these frequencies will be sent to the PTS
        bin_freqs = self._convert_freq_list(freqs, model) # convert frequencies into binary form
        while continuous:
            for f in bin_freqs:
                self._make_wave(f)
                self._usleep(dt)
        for f in bin_freqs:
            self._make_wave(f)
            self._usleep(dt)


    def mock_obs(self, wait_time, DM=332.72, f_min=1150e6, f_max=1650e6, dt=1000, model='PTS3200'):
        """
        Simulate an FRB observation in collected time-dependent voltage data.

        Inputs:
            - wait_time (float)|[s]: time until FRB pulse/sweep begins
            - DM (float)|[pc*cm^-3]: dispersion measure (default 
              is DM for SGR1935+2154)
            - f_min (float)|[Hz]: minimum frequency of sweep
            - f_max (float)|[Hz]: maximum frequency of sweep
            - dt (float)|[us]: sweep update interval
            - model (str): PTS model used. Default is PTS3200.
              Accepts PTS3200, PTS500, PTS300.
            - save (bool): save mock observation to file?

        Returns:
            - If save, file containing voltage-time data.
        """
        wait_time_us = wait_time*1e6 # convert to microseconds
        self.continuous_wave(self.no_signal) # "no signal" signal
        self._usleep(wait_time_us)
        self.dm_sweep(DM, f_min, f_max, dt, model, continuous=False) # FRB sweep
        self.continuous_wave(self.no_signal) # go back to "no signal" signal
        # XXX Add saving ability

    # def reset_gpios(self):




        




