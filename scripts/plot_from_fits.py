import numpy as np
import matplotlib.pyplot as plt
import argparse
from astropy.io import fits


parser = argparse.ArgumentParser(description='Plot power matrix.')

parser.add_argument('filename', type=str,  help='Fits file name')
parser.add_argument('col_name', type=str, help='auto0_real, auto1_real, cross_real, or cross_imag')

args = parser.parse_args()
FILENAME = args.filename
COL_NAME = args.col_name

F = fits.open(FILENAME)
data = np.array([F[nspec].data[COL_NAME] for i in range(1, len(F)-1)]) # ignore PrimaryHDU

plt.figure()
plt.imshow(data, aspect='auto', interpolation='nearest', origin='lower')
plt.show()
