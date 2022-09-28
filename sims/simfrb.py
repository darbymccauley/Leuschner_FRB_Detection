import numpy as np
import matplotlib.pyplot as plt
from scipy import signal



def DM_delay(self, DM, freq):
    """
    Compute the dispersion measure pulse delay time.

    Inputs:
        - DM: dispersion measure
        - freq: frequency
    Returns:
        - pulse delay in [ms]
    """
    const = 4140
    A = DM*4140*1e3
    return A/(freq**2)


def smearing(Power, nspec, pulse_width, t_samp):
    """
    Smears the FRB pulse by convolving it with a gaussian window.
    
    Inputs:
        - Power: power matrix with shape (nchans, nspec)
        - nspec: number of spectra
        - pulse_width [ms]: width of the pulse
        - t_samp [ms]: sampling rate
    Returns:
        - Smeared power matrix of shape (nchans, nspec)
    """
    FWHM_frac = 2*np.sqrt(2*np.log(2))
    sigma = pulse_width/FWHM_frac
    sigma_bins = sigma/t_samp
    Smeared = np.empty_like(Power)
    for spec in range(nspec):
        freq = Power[:, spec]
        Smeared[:, spec] = np.convolve(freq, signal.windows.gaussian(20, sigma_bins), mode='same')
    return Smeared


def make_frb(nspec=128, nchans=1024, DM=332.72, pulse_width=2, f_min=1150, f_max=1650, t_samp=64e3):
    """
    Make an FRB with the specified attributes. FRB is dispersed.

    Inputs:
        - nspec: number of spectra
        - nchans: number of frequency channels
        - DM: dispersion measure
        - pulse_width [ms]: width of the pulse 
        - f_min [MHz]: bottom frequency of passband
        - f_max [MHz]: top frequency of passband 
        - t_samp [ms]: sampling rate
    Returns:
        - power matrix of shape (nspec, nchans)
    """
    shape = (nchans, nspec)
    
    freqs = np.linspace(f_min, f_max, nchans)

    t_min = 0
    t_max = t_samp*nspec
    times = np.linspace(t_min, t_max, nspec)

    signal_power = 10

    td0 = DM_delay(DM, f_max)
    tds = DM_delay(DM, freqs) - td0

    bins = tds/t_samp
    rounded_bins = np.round(bins).astype(int)

    Image = np.random.randn(np.prod(shape)).reshape(shape)
    for i in range(len(Image)):
        index = rounded_bins[i]
        if index >= nspec:
            continue
        Image[i, index] += signal_power
    Smeared = smearing(Image, nspec, pulse_width, t_samp)
    return Smeared




