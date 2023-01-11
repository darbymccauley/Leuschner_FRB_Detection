import numpy as np
from fdmt_homebrew import FDMT
import matplotlib.pyplot as plt
# import os
import argparse

parser = argparse.ArgumentParser('Run FDMT algorithm on data file.')
parser.add_argument('file_path', type=str, help='Data file path')
# parser.add_argument('ntimes', type=int, help='number of spectra')
# parser.add_argument('nchans', type=int, help='number of channels')
parser.add_argument('fmin', help='minimum frequency of band in [Hz]')
parser.add_argument('fmax', help='maximum frequency of band in [Hz]')

args = parser.parse_args()
FILE_PATH = args.file_path
# NTIMES = args.ntimes
# NCHANS = args.nchans
FMIN = float(args.fmin)
FMAX = float(args.fmax)


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

FREQS = np.linspace(FMIN, FMAX, fchans) # frequency range in [Hz]


## Prepare data
f = open(FILE_PATH, 'rb')
y = np.frombuffer(f.read(), dtype='uint16', offset=header)
assert (y.size/total_chans).is_integer(), 'Non-integer number of spectra in file. Got {0}'.format(y.size/total_chans)+'spectra.'
nspec = int(y.size/total_chans)
# tsamp = 0.1 # [ms] -- SNAP collects a new spectrum every 0.1 ms
TIMES = np.linspace(0, 1, nspec)

data =  y.reshape([nspec, total_chans]) # reshape into [nspec, 2060]
data = data[:, info_chans:] # ignore info_chans


MAXDM = 500
fdmt = FDMT(freqs=FREQS, times=TIMES, maxDM=MAXDM)
dmt = fdmt.apply(data)

print(dmt.shape)
t0, dm0 = inds = np.unravel_index(np.argmax(dmt, axis=None), dmt.shape)
print(TIMES[t0], np.linspace(0, MAXDM, fchans)[dm0])

plt.figure()
plt.imshow(dmt, aspect='auto')
plt.show()