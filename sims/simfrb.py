#################################
# Computer generated FRB signal #
#################################

import numpy as np
import matplotlib.pyplot as plt
import argparse

class SimFRB:
    def __init__(self):
        self.CONST = 4140e12 # s Hz^2 / (pc / cm^3)

    def DM_delay(self, DM, freq):
        """
        Computes the frequency-dependent dispersion measure
        time delay.
        Inputs:
            - DM [pc*cm^-3]: dispersion measure
            - freq [Hz]: frequency
        Returns:
            - Pulse time delay in [s] 
        """
        return np.float32(DM * self.CONST) / freq**2

    def make_frb(self, ntimes=4096, nfreqs=2048, f_min=1150e6, f_max=1650e6, DM=332.72, pulse_width=2.12e-3, pulse_amp=2, 
                 t0=2e-3, dtype='float32', cdtype='complex64'):
        """
        Simulates a fast radio burst (FRB) observation given a 
        certain set of parameters.
        Inputs:
            - ntimes (int): number of integration times
            - freqs (int): number of spectral frequency channels
            - f_min (float)|[Hz]: minimum frequency of band
            - f_max (float)|[Hz]: maximum frequency of band
            - DM (float)|[pc*cm^-3]: dispersion measure
            - pulse_width (float)|[s]: width of FRB pulse
            - pulse_amp (float): amplitude of FRB pulse
            - t0 (float)|[s]: offset the pulse start time
        Returns:
            - Power matrix of shape (ntimes, nfreqs)
        """
        times = np.arange(ntimes)*(1.048e-3) # [s]
        freqs = np.linspace(f_min, f_max, nfreqs)
        dt = times[1] - times[0]
        tmid = times[times.size // 2]
        delays = self.DM_delay(DM, freqs)
        delays -= tmid + delays[-1] - t0  # center lowest delay at t0

        # assume same inherent profile for all freqs
        pulse = pulse_amp * np.exp(-(times - tmid)**2 / (2 * pulse_width**2)) # Gaussian pulse shape
        _pulse = np.fft.rfft(pulse).astype(cdtype)
        _ffreq = np.fft.rfftfreq(pulse.size, dt)
        phs = np.exp(-2j * np.pi * np.outer(_ffreq.astype(dtype), delays.astype(dtype)))
        _pulse_dly = np.einsum('i,ij->ij', _pulse, phs)
        profile = np.fft.irfft(_pulse_dly, axis=0).astype(dtype)
        profile += np.random.normal(size=profile.shape, loc=10) # add noise
        # profile[:,::137] = 0  # blank out rfi
        # profile[:,300:500] = 0  # blank out rfi
        # profile[::519] = 100  # rfi
        profile -= np.mean(profile, axis=0, keepdims=True)
        return profile

    def dedisperse(self, pulse, ntimes=4096, nfreqs=2048, f_min=1150e6, f_max=1650e6, DM=332.72, pulse_width=2.12e-3, pulse_amp=2, t0=2e-3, dtype='float32', cdtype='complex64'):
        times = np.arange(ntimes)*(1.048e-3) # [s]
        freqs = np.linspace(f_min, f_max, nfreqs)
        dt = times[1] - times[0]
        tmid = times[times.size // 2]
        delays = self.DM_delay(DM, freqs)
        delays -= tmid + delays[-1] - t0  # center lowest delay at t0

        # assume same inherent profile for all freqs
        _pulse = np.fft.rfft(pulse, axis=0).astype(cdtype)
        _ffreq = np.fft.rfftfreq(pulse.shape[0], dt)
        phs = np.exp(2j * np.pi * np.outer(_ffreq.astype(dtype), delays.astype(dtype)))
        _pulse_dly = _pulse * phs.conj()
        profile = np.fft.irfft(_pulse_dly, axis=0).astype(dtype)
        # profile += np.random.normal(size=profile.shape, loc=10) # add noise
        # profile[:,::137] = 0  # blank out rfi
        # profile[:,300:500] = 0  # blank out rfi
        # profile[::519] = 100  # rfi
        # profile -= np.mean(profile, axis=0, keepdims=True)
        return profile

    def pts_frb(self, ntimes=4096, nfreqs=2048, f_min=1150e6, f_max=1650e6, DM=332.72, pulse_width=2.12e-3, pulse_amp=2, 
                t0=2e-3, dtype='float32', cdtype='complex64'):
        """
        Simulates the RPi+PTS FRB generator (see wavegen.py) output given a 
        certain set of input parameters. This function essentially converts 
        a smooth computer generated sweep signal into a more step-like signal.
        Inputs:
            - ntimes (int): number of integration times
            - freqs (int): number of spectral frequency channels
            - f_min (float)|[Hz]: minimum frequency of band
            - f_max (float)|[Hz]: maximum frequency of band
            - DM [pc*cm^-3]: dispersion measure
            - pulse_width [s]: width of FRB pulse
            - pulse_amp: amplitude of FRB pulse
            - t0 [s]: offset the pulse start time
        Returns:
            - Power matrix of shape (ntimes, nfreqs)
        """
        times = np.arange(ntimes)*1e-4 # [s]
        freqs = np.linspace(f_min, f_max, nfreqs)
        dt = times[1] - times[0] # 0.1ms
        tmid = times[times.size // 2]
        delays = self.DM_delay(DM, freqs)
        delays -= tmid + delays[-1] - t0  # center lowest delay at t0

        # assume same inherent profile for all freqs
        pulse = pulse_amp * np.exp(-(times - tmid)**2 / (2 * pulse_width**2)) # Gaussian pulse shape
        _pulse = np.fft.rfft(pulse).astype(cdtype)
        _ffreq = np.fft.rfftfreq(pulse.size, dt)
        phs = np.exp(-2j * np.pi * np.outer(_ffreq.astype(dtype), delays.astype(dtype))) 
        _pulse_dly = np.einsum('i,ij->ij', _pulse, phs)
        profile = np.fft.irfft(_pulse_dly, axis=0).astype(dtype) 
        # blank out some signal so it mirrors the step behavior of RPi+PTS setup
        profile.shape = (-1, 4, ntimes)
        profile[0:, 0:3] = 0
        profile.shape = (-1, ntimes)
        
        profile += np.random.normal(size=profile.shape, loc=10) # add noise
        profile -= np.mean(profile, axis=0, keepdims=True)
        return profile
    
####################################################################################################################

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Generate a simulated FRB pulse with given characteristics.')
    parser.add_argument('ntimes', type=int, help='Number of spectra/integration times')
    parser.add_argument('nfreqs', type=int, help='Number of frequency channels')
    parser.add_argument('f_min', type=float, help='Minimum frequency of base-band [MHz]')
    parser.add_argument('f_max', type=float, help='Maximum frequency of base-band [MHz]')
    parser.add_argument('dm', type=float, help='Dispersion measure [pc*cm^-3]')
    parser.add_argument('pulse_width', type=float, help='Width of pulse [ms]')
    parser.add_argument('pulse_amp', type=float, help='Amplitude of pulse')
    parser.add_argument('t0', type=float, help='Offset of pulse start time [s]')

    args = parser.parse_args()
    NTIMES = args.ntimes
    NFREQS = args.nfreqs
    FMIN = args.f_min
    FMAX = args.f_max
    DM = args.dm
    PULSE_WIDTH = args.pulse_width
    PULSE_AMP = args.pulse_amp
    T0 = args.t0
    
    sims = SimFRB()
    frb = sims.pts_frb(NTIMES, NFREQS, FMIN, FMAX, DM, PULSE_WIDTH, PULSE_AMP, T0)
    
    fig, ax = plt.subplots(constrained_layout=True)
    im = ax.imshow(frb.T, aspect='auto', origin='lower', extent=[0, NTIMES, 0, NFREQS])
    ax.set_xlabel('Spectra')
    ax.set_ylabel('Frequency Channel')
    ax.set_title('Computer simulated FRB with DM {0:0.2f} pc$\cdot$cm$^3$'.format(DM))
    ax.set_xlim(0, NTIMES)
    ax.set_ylim(0, NFREQS)
    ax2 = ax.twinx()
    ax2.set_ylim(FMIN/1e6, FMAX/1e6)
    ax2.set_ylabel('Frequency [MHz]', rotation=270, labelpad=10)
    plt.show();