#################################
# Computer generated FRB signal #
#################################

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

CONST = 4140e12 # s Hz^2 / (pc / cm^3)

def DM_delay(DM, freq):
    """
    Computes the frequency-dependent dispersion measure
    time delay.
    Inputs:
        - DM [pc*cm^-3]: dispersion measure
        - freq [Hz]: frequency
    Returns:
        - Pulse time delay in [s] 
    """
    return np.float32(DM * CONST) / freq**2

class SimFRB:
    # def __init__(self
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
        times = np.arange(ntimes)*1e-4 # [s]
        freqs = np.linspace(f_min, f_max, nfreqs)
        dt = times[1] - times[0]
        tmid = times[times.size // 2]
        delays = DM_delay(DM, freqs)
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
        delays = DM_delay(DM, freqs)
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
        profile[:, 0:3] = 0
        profile.shape = (-1, ntimes)
        
        profile += np.random.normal(size=profile.shape, loc=10) # add noise
        profile -= np.mean(profile, axis=0, keepdims=True)
        return profile

    

# if __name__ == '__main__':
#     NSPEC, NCHANS = 2048, 2048
#     FMIN, FMAX = 1410e6, 1640e6 # [Hz] 230 MHz bandwidth
#     frb = pts_frb(ntimes=NSPEC, nfreqs=NCHANS, f_min=FMIN, f_max=FMAX, pulse_amp=10)
#     plt.figure()
#     plt.imshow(frb.T, aspect='auto', origin='lower')
#     plt.show()
    
#     import sys
#     sys.path.append('../src/fdmt')
#     from fdmt_homebrew import FDMT
    
#     MAXDM = 500
#     FREQS = np.linspace(FMIN, FMAX, NCHANS) # [Hz]
#     TIMES = np.arange(NSPEC)*1e-4 # [s]
#     fdmt = FDMT(freqs=FREQS, times=TIMES, maxDM=MAXDM)
#     dmt = fdmt.apply(frb)
#     t0, dm0 = inds = np.unravel_index(np.argmax(dmt, axis=None), dmt.shape)
#     dm = np.linspace(0, MAXDM, NSPEC)[dm0]
#     print('Measured DM:', dm)
    
#     plt.figure()
#     plt.imshow(dmt, aspect='auto', origin='lower')
#     plt.show()