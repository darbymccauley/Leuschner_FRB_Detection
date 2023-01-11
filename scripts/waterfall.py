## Generates an interactive waterfall plot ##

import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description='Generate waterfall plot of data within file.')
parser.add_argument('filename', type=str,  help='Data file name(.dat)')
parser.add_argument('fmin', type=float, help='Minimum frequency of band in [MHz]')
parser.add_argument('fmax', type=float, help='Maximum frequency of band in [MHz]')

args = parser.parse_args()
FILENAME = args.filename
FMIN = args.fmin
FMAX = args.fmax


# The total number of channels per spectra is 2060. Only 2048 of them
# contain spectral data (one for each frequency channel). The remaining 12 channels
# store spectrum information, such as the time in which the spectra was collected 
# and the FPGA count of the spectral frame. 
# For more information see https://github.com/liuweiseu/limbo_recorder/tree/auto_files#file-format
total_chans = 2060 # TOTAL number of channels
fchans = 2048 # frequency channels
info_chans = 12 # channels containing spectra information 
# The header of the data file takes up the first 1024 byte
header = 1024


f = open(FILENAME, 'rb')
y = np.frombuffer(f.read(), dtype='uint16', offset=header)
assert (y.size/total_chans).is_integer(), 'Non-integer number of spectra in file. Got {0}'.format(y.size/total_chans)+'spectra.'
nspec = int(y.size/total_chans)

data =  y.reshape([nspec, total_chans]) # reshape into [nspec, 2060]
data = data[:, info_chans:] # ignore info_chans


fig, ax = plt.subplots(constrained_layout=True)
im = ax.imshow(data.T, aspect='auto', origin='lower', extent=[0, nspec, FMIN, FMAX])
cbar = fig.colorbar(im, pad=0.01)
cbar.set_label('Power', rotation=270, labelpad=20)
im.set_clim(0, 5000)
ax.set_xlabel('Time [ms]')
ax.set_ylabel('Frequency [MHz]')
ax.set_title(FILENAME)
plt.show()