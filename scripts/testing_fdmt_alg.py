import argparse
import numpy as np
import sys 
import time

sys.path.append('/home/darbymccauley/research/leuschner/leuschner_frb_detector/Leuschner_FRB_Detection/src/')
sys.path.append('/home/darbymccauley/research/leuschner/leuschner_frb_detector/Leuschner_FRB_Detection/sims/')

import fdmt as fdmt 
from simfrb import make_frb

parser = argparse.ArgumentParser(description='Generate a simulated FRB pulse with given characteristics.')
parser.add_argument('nspec', help='Number of spectra')
parser.add_argument('nchans', help='Number of frequency channels')
parser.add_argument('dm', help='Dispersion measure [pc*cm^-3]')
parser.add_argument('pulse_width', help='Width of pulse [ms]')
parser.add_argument('f_min', help='Minimum frequency of base-band [MHz]')
parser.add_argument('f_max', help='Maximum frequency of base-band [MHz]')
parser.add_argument('t_samp', help='Sampling time [ms]')
parser.add_argument('datatype', help='Data type (either int32 or int 64. int64 recommended')
parser.add_argument('plot', help='Plot output (bool)')

args = parser.parse_args()
NSPEC = int(args.nspec)
NCHANS = int(args.nchans)
DM = float(args.dm)
PULSE_WIDTH = float(args.pulse_width)
F_MIN = float(args.f_min)
F_MAX = float(args.f_max)
T_SAMP = float(args.t_samp)
DATATYPE = str(args.datatype)
PLOT = bool(args.plot)

frb = make_frb(nspec=NSPEC, nchans=NCHANS, DM=DM, pulse_width=PULSE_WIDTH, f_min=F_MIN, f_max=F_MAX, t_samp=T_SAMP, plot=PLOT)

# parser = argparse.ArgumentParser(description='Run FDMT algorithm')
# parser.add_argument('file', help='path to file with data in it')
# parser.add_argument('f_min', help='Beginning frequency of base-band')
# parser.add_argument('f_max', help='Ending frequency of base-band')
# parser.add_argument('maxDT', help='Maximal delay (in time bins) of the maximal dispersion')
# parser.add_argument('dataType', help='Type of data (int32 or int64 recommended)')

# args = parser.parse_args()
# IMAGE = np.loadtxt(args.file)
# FMIN = float(args.f_min)
# FMAX = float(args.f_max)
# MAXDT = float(args.maxDT)
# DATATYPE = args.dataType

t0 = time.time()
dmt = fdmt.FDMT(frb, F_MIN, F_MAX, NSPEC, DATATYPE)
tf = time.time()
print('\nComputation time for', NCHANS, 'DM trials:', tf-t0, 's.\n' )

# import IPython; IPython.embed()

