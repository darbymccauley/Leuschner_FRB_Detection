# Prepares data files so they are workable

import numpy as np

# The header contains 1024 bytes of data. Each spectra contains 2048
# frequency channels. The beginning of each spectra also contains an 
# additional 12 bytes of metadata that stores spectrum information,
# such as time in which the spectra was collected (in sec and ms) and
# the FPGA spectral frame count. Therefore, if you want only the 2048
# spectral channels, you must remove the preceeding 12 bytes from each
# spectra first.
# For more information see https://github.com/liuweiseu/limbo_recorder/tree/auto_files#file-format
header = 1024
total_chans = 2060 # TOTAL number of channels (fchans+info_chans)
fchans = 2048 # frequency channels
info_chans = 12 # each spectrum contains 12 bytes of metadata

def prepare_data(filename):
    """
    Inputs:
        - filename (str): File path+name. Must be binary data file (.dat)
    Returns:
        - data: array of shape (nspec, 2048) representing spectral data 
            within the file
    """
    f = open(filename, 'rb')
    y = np.frombuffer(f.read(), dtype='uint16', offset=header)
    assert (y.size/total_chans).is_integer(), 'Non-integer number of spectra in file. Got {0}'.format(y.size/total_chans)+'spectra.'
    nspec = int(y.size/total_chans)
    data =  y.reshape([nspec, total_chans]) # reshape into [nspec, 2060]
    data = data[:, info_chans:] # ignore info_chans
    return data