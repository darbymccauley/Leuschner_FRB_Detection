## Generates an interactive waterfall plot ##

import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description='Generate waterfall plot of data within file.')
parser.add_argument('filename', type=str,  help='Data file name(.dat)')

args = parser.parse_args()
FILENAME = args.filename

f = open(FILENAME, 'rb')
x = np.frombuffer(f.read(), dtype='uint16')
# remove header from data file so only spectra remains
y = x[512:]
nchans = 2048 # number of frequency channels
assert (y.size/nchans).is_integer(), 'Non-integrer number of spectra in file. Got {0}'.format(y.size/nchans)+' spectra.'

# Reshape data so that it takes shape [nspec, nchans]
data = y.reshape([int(y.size/nchans), nchans])

plt.figure()
plt.imshow(data.T, aspect='auto')
plt.xlabel('Spectrum number')
plt.ylabel('Frequency channel')
plt.show()