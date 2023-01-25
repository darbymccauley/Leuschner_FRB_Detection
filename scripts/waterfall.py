## Generates an interactive waterfall plot ##

import numpy as np
import matplotlib.pyplot as plt
import os
import argparse
from prepare import prepare_data

parser = argparse.ArgumentParser(description='Generate waterfall plot of data within file.')
parser.add_argument('file_path', type=str,  help='Data file path')
parser.add_argument('fmin', type=float, help='Minimum frequency of band in [MHz]')
parser.add_argument('fmax', type=float, help='Maximum frequency of band in [MHz]')

args = parser.parse_args()
FILE_PATH = args.file_path
FILENAME = os.path.split(FILE_PATH)[-1] # grab file name from file path
FMIN = args.fmin
FMAX = args.fmax

data = prepare_data(FILE_PATH)

fig, ax = plt.subplots(constrained_layout=True)
im = ax.imshow(data.T, aspect='auto', origin='lower', extent=[0, nspec, FMIN, FMAX])
cbar = fig.colorbar(im, pad=0.01)
cbar.set_label('Power', rotation=270, labelpad=20)
# im.set_clim(0, 5000)
ax.set_xlabel('Time [ms]')
ax.set_ylabel('Frequency [MHz]')
ax.set_title(FILENAME)
plt.show()
