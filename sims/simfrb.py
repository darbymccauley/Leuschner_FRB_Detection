#################################
# Computer generated FRB signal #
#################################

import numpy as np
import matplotlib.pyplot as plt


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

def make_frb(ntimes=4096, nfreqs=2048, f_min=1150e6, f_max=1650e6, DM=332.72, pulse_width=2.12e-3, pulse_amp=2, t0=2e-3,
             dtype='float32', cdtype='complex64'):
    """
    Simulates a fast radio burst (FRB) observation given a 
    certain set of parameters.
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
    times = np.linspace(0, 1, ntimes) # 1 second interval
    freqs = np.linspace(f_min, f_max, nfreqs)
    dt = times[1] - times[0]
    tmid = times[times.size // 2]
    delays = DM_delay(DM, freqs)
    delays -= tmid + delays[-1] - t0  # center lowest delay at t0

    # assume same inherent profile for all freqs
    pulse = pulse_amp * np.exp(-(times - tmid)**2 / (2 * pulse_width**2))
    _pulse = np.fft.rfft(pulse).astype(cdtype)
    _ffreq = np.fft.rfftfreq(pulse.size, dt)
    phs = np.exp(-2j * np.pi * np.outer(_ffreq.astype(dtype), delays.astype(dtype)))
    _pulse_dly = np.einsum('i,ij->ij', _pulse, phs)
    profile = np.fft.irfft(_pulse_dly, axis=0).astype(dtype)
    profile += np.random.normal(size=profile.shape, loc=10) # add noise
    profile[:,::137] = 0  # blank out rfi
    profile[:,300:500] = 0  # blank out rfi
#     profile[::519] = 100  # rfi
    profile -= np.mean(profile, axis=0, keepdims=True)
    return profile


##########################################################################################################################################
# def collect_data(obs_time, file_path, nchans=4096, DM=332.72, pulse_width=2.12, f_min=1150, f_max=1650, t_samp=0.0612, SNR=2):
#     """
#     Collect simulated FRB data and chunk the spectra into
#     saved datafiles.

#     Inputs:
#         - obs_time [s]: observation time in seconds
#         - file_path (str): path to save collected files to
#         - nchans (int): number of frequency channels
#         - DM [pc*cm^-3]: dispersion measure
#         - pulse_width [ms]: time width of FRB pulse
#         - f_min [MHz]: lower frequency of band
#         - f_max [MHz]: upper frequency of band
#         - t_samp [ms]: sampling time/time resolution
#         - SNR: signal-to-noise ratio
#     Returns: A series of data files saved to specified file 
#       path, each containing 1s worth of data.
#     """
#     obs_time_ms = obs_time*1e3 # convert s to ms
#     nspec_1s = np.round(1e3/t_samp).astype(int) # number of spectra in 1 second 
#     nspec_tot = np.round(obs_time_ms/t_samp).astype(int) # total number of spectra to be collected in observing time
#     nblocks = np.round(nspec_tot/nspec_1s).astype(int)

#     Image = make_frb(nspec=nspec_tot, nchans=nchans, DM=DM, pulse_width=pulse_width, f_min=f_min, f_max=f_max, t_samp=t_samp, SNR=SNR)

#     spec0 = 0
#     for block in range(1, nblocks+1):
#         if block == np.max(nblocks)+1: # needed in case last number of spectra in last block is not equal to nspec_1s
#             data_chunk = Image[:, spec0:]
#             np.savetxt(file_path+'/block_'+str(block)+'.txt', data_chunk)
#         data_chunk = Image[:, spec0:block*nspec_1s]
#         np.savetxt(file_path+'/block_'+str(block)+'.txt', data_chunk)
#         spec0 = block*nspec_1s


# def half_block(Image):
#     """
#     Split data from data files into halves for
#     use in later power analysis.
    
#     Inputs:
#         - Image: data from data file
#     Returns: Two matrixes each 0.5s in time width.
#     """
#     # data = np.loadtxt(file)
#     half_index = np.round(Image.shape[1]/2).astype(int)
#     first_half, second_half = Image[:, :half_index], Image[:, half_index:]
#     return first_half, second_half


# def find_pulse(data_file, minimum_sigma=2):
#     """
#     Look for pulses in the data files and save 
#     interesting data to a singular file.

#     Inputs: 
#         - data_file: data file containing power matrix
#         - minimum_sigma: Minimum average power signal 
#           that warrents a saving of data set
#     Returns: XXX
#     """
#     data = np.loadtxt(data_file)
#     first_half_data, second_half_data = half_block(data)
#     blocks = [['first half of '+data_file, first_half_data], ['second half of '+data_file, second_half_data]]
#     for name, half in blocks:
#         f = open(FILENAME, 'a') # append mode
#         if half.mean() > minimum_sigma:
#             print(f'FRB pulse found in {name}. Saving...')



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
    