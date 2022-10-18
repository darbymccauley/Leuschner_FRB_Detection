import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


def DM_delay(DM, freq):
    """
    Computes the frequency-dependent dispersion measure
    time delay.

    Inputs:
        - DM [pc*cm^-3]: dispersion measure
        - freq [MHz]: frequency
    Returns:
        - Pulse time delay in [ms] 
    """
    const = 4140
    A = DM*const*1e3 # 1e3 for conversion to ms
    return A/(freq**2)

def make_frb(nspec=1024, nchans=2048, DM=332.72, pulse_width=2.12, f_min=1150, f_max=1650, t_samp=0.064, offset=0, plot=False):
    """
    Simulates a fast radio burst (FRB) observation given a 
    certain set of parameters.

    Inputs:
        - nspec: number of spectra
        - nchans: number of frequency channels
        - DM [pc*cm^-3]: dispersion measure
        - pulse_width [ms]: width of FRB pulse
        - f_min [MHz]: lower frequency of bandwidth
        - f_max [MHz]: upper frequency of bandwidth
        - t_samp [ms]: sampling time/time resolution
        - offset [ms]: offset the pulse start time
        - plot (bool): plot output results
    Returns:
        - Power matrix of shape (nchans, nspec)
    """
    shape = (nchans, nspec)
    freqs = np.linspace(f_min, f_max, nchans)
    t_min = 0
    t_max = t_samp*nspec

    signal_power = 0.5
    
    # td0 = DM_delay(DM, f_max)
    # tds = DM_delay(DM, freqs) - td0 + offset
    # bins = tds/t_samp
    delays = DM_delay(DM, freqs) + offset
    delay_bins = delays/t_samp
    rounded_bins = np.round(delay_bins).astype(int)

    pulse_bin_width = np.round(pulse_width/t_samp).astype(int)

    Image = np.random.normal(size=shape, loc=1, scale=0.2) # XXX

    FWHM_frac = 2*np.sqrt(2*np.log(2))
    sigma = pulse_width/FWHM_frac
    window_len = 11
    gauss_window = signal.windows.gaussian(window_len, sigma/t_samp)

    for i in range(len(Image)):
        if rounded_bins[i] > nspec:
            continue # so the tail of the pulse doesn't loop back around
        Image[i] = np.roll(Image[i], rounded_bins[i]) # shift by DM delay to produce dispersion curve
        Image[i, rounded_bins[i]:rounded_bins[i]+pulse_bin_width] += signal_power # give power to curve
        
    # for spec in range(nspec):



    
    if plot:
        fig, ax = plt.subplots(constrained_layout=True)
        im = ax.imshow(Image, aspect='auto', origin='lower', extent=[t_min, t_max, f_min, f_max])

        ax.set_xlabel('Time [ms]')
        ax.set_ylabel('Frequency [MHz]')
        ax.set_xlim(t_min, t_max)
        ax.set_ylim(f_min, f_max)

        ax2 = ax.twinx()
        ax2.set_ylim(0, nchans)
        ax2.set_ylabel('Channel', rotation=270, labelpad=10)
        
        ax3 = ax.twiny()
        ax3.set_xlim(0, nspec)
        ax3.set_xlabel('Spectrum', labelpad=10)

        plt.show();

    return Image