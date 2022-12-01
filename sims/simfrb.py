import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from tqdm import tqdm


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

def make_frb(nspec=4096, nchans=4096, DM=332.72, pulse_width=2.12, f_min=1150, f_max=1650, t_samp=0.06128, SNR=2, plot=False):
    """
    Simulates a fast radio burst (FRB) observation given a 
    certain set of parameters.
    Inputs:
        - nspec: number of spectra
        - nchans: number of frequency channels
        - DM [pc*cm^-3]: dispersion measure
        - pulse_width [ms]: width of FRB pulse
        - f_min [MHz]: lower frequency of band
        - f_max [MHz]: upper frequency of band
        - t_samp [ms]: sampling time/time resolution
        - offset [ms]: offset the pulse start time
        - SNR: signal-to-noise level
        - plot (bool): plot output results
    Returns:
        - Power matrix of shape (nchans, nspec)
    """
    shape = (nchans, nspec)
    freqs = np.linspace(f_min, f_max, nchans)
    t_min = 0
    t_max = t_samp*nspec

    delays = DM_delay(DM, freqs)
    delay_bins = delays/t_samp
    rounded_bins = np.round(delay_bins).astype(int)

    pulse_bin_width = np.round(pulse_width/t_samp).astype(int)

    noise_std = 0.2 # XXX
    Image = np.random.normal(size=shape, loc=1, scale=noise_std)
    noise_power = 1
    signal_power = SNR*noise_power

    FWHM_frac = 2*np.sqrt(2*np.log(2))
    sigma = pulse_bin_width/FWHM_frac
    window_len = pulse_bin_width
    gauss_window = signal.windows.gaussian(window_len, sigma)

    Image[:, :pulse_bin_width] += signal_power
    for i in range(len(Image)):
        if rounded_bins[i] > nspec:
            continue # so the tail of the pusle doesn't loop back around
        Image[i] = np.roll(Image[i], rounded_bins[i])
        # Image[i, :] *= gauss_window 

    if plot:
        plot_frb(Image, t_min, t_max, f_min, f_max)
        
    return Image


def plot_frb(Image, t_min, t_max, f_min, f_max):
    """
    Plot FRB data.
    
    Inputs:
        - Image: Power matrix of shape (nchans, nspec)
        - t_min [ms]: start time
        - t_max [ms]: end time
        - f_min [MHz]: lower frequency of band
        - f_max [MHz]: upper frequency of band
    Returns: plot of Image with time and frequency main axes,
      and channel and spectrum number minor axes.
    """
    nchans, nspec = Image.shape
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


def collect_data(obs_time, file_path, nchans=4096, DM=332.72, pulse_width=2.12, f_min=1150, f_max=1650, t_samp=0.0612, SNR=2):
    """
    Collect simulated FRB data and chunk the spectra into
    saved datafiles.

    Inputs:
        - obs_time [s]: observation time in seconds
        - file_path (str): path to save collected files to
        - nchans (int): number of frequency channels
        - DM [pc*cm^-3]: dispersion measure
        - pulse_width [ms]: time width of FRB pulse
        - f_min [MHz]: lower frequency of band
        - f_max [MHz]: upper frequency of band
        - t_samp [ms]: sampling time/time resolution
        - SNR: signal-to-noise ratio
    Returns: A series of data files saved to specified file 
      path, each containing 1s worth of data.
    """
    obs_time_ms = obs_time*1e3 # convert s to ms
    nspec_1s = np.round(1e3/t_samp).astype(int) # number of spectra in 1 second 
    nspec_tot = np.round(obs_time_ms/t_samp).astype(int) # total number of spectra to be collected in observing time
    nblocks = np.round(nspec_tot/nspec_1s).astype(int)

    Image = make_frb(nspec=nspec_tot, nchans=nchans, DM=DM, pulse_width=pulse_width, f_min=f_min, f_max=f_max, t_samp=t_samp, SNR=SNR)

    spec0 = 0
    for block in range(1, nblocks+1):
        if block == np.max(nblocks)+1: # needed in case last number of spectra in last block is not equal to nspec_1s
            data_chunk = Image[:, spec0:]
            np.savetxt(file_path+'/block_'+str(block)+'.txt', data_chunk)
        data_chunk = Image[:, spec0:block*nspec_1s]
        np.savetxt(file_path+'/block_'+str(block)+'.txt', data_chunk)
        spec0 = block*nspec_1s


def half_block(Image):
    """
    Split data from data files into halves for
    use in later power analysis.
    
    Inputs:
        - Image: data from data file
    Returns: Two matrixes each 0.5s in time width.
    """
    # data = np.loadtxt(file)
    half_index = np.round(Image.shape[1]/2).astype(int)
    first_half, second_half = Image[:, :half_index], Image[:, half_index:]
    return first_half, second_half


def find_pulse(data_file, minimum_sigma=2):
    """
    Look for pulses in the data files and save 
    interesting data to a singular file.

    Inputs: 
        - data_file: data file containing power matrix
        - minimum_sigma: Minimum average power signal 
          that warrents a saving of data set
    Returns: XXX
    """
    data = np.loadtxt(data_file)
    first_half_data, second_half_data = half_block(data)
    blocks = [['first half of '+data_file, first_half_data], ['second half of '+data_file, second_half_data]]
    for name, half in blocks:
        f = open(FILENAME, 'a') # append mode
        if half.mean() > minimum_sigma:
            print(f'FRB pulse found in {name}. Saving...')



# def minimize_nspec(date_file, minimum_sigma):
#     Image = np.loadtxt(data_file)
#     nchans, nspec = Image.shape
#     log2_nspec = int(np.log2(nspec))
#     indices = []
#     for i in range(log2_nspec):
#         data = Image[:, 2**i:2**(i+1)]
#         if data.mean() > minimum_sigma:
#             indices.append(i)
#     minimum = 2**(np.min(indices)) - 1  
#     maximum = 2**(np.max(indices)+1)
#     length = maximum - minimum
#     end_index = int(2**np.ceil(np.log2(length)))
#     return Image[:, minimum:minimum+end_index]
    