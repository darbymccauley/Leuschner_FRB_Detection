import argparse
import numpy as np
import sys

sys.path.append('/home/darbymccauley/research/leuschner/leuschner_frb_detector/Leuschner_FRB_Detection/sims/')

from simfrb import make_frb

parser = argparse.ArgumentParser(description='Generate a simulated FRB pulse with given characteristics.')
parser.add_argument('nspec', help='Number of spectra')
parser.add_argument('nchans', help='Number of frequency channels')
parser.add_argument('dm', help='Dispersion measure [pc*cm^-3]')
parser.add_argument('pulse_width', help='Width of pulse [ms]')
parser.add_argument('f_min', help='Minimum frequency of base-band [MHz]')
parser.add_argument('f_max', help='Maximum frequency of base-band [MHz]')
parser.add_argument('t_samp', help='Sampling time [ms]')
parser.add_argument('plot', help='Plot output (bool)')

args = parser.parse_args()
NSPEC = int(args.nspec)
NCHANS = int(args.nchans)
DM = float(args.dm)
PULSE_WIDTH = float(args.pulse_width)
F_MIN = float(args.f_min)
F_MAX = float(args.f_max)
T_SAMP = float(args.t_samp)
PLOT = args.plot

frb = make_frb(nspec=NSPEC, nchans=NCHANS, DM=DM, pulse_width=PULSE_WIDTH, f_min=F_MIN, f_max=F_MAX, t_samp=T_SAMP, plot=PLOT)


import IPython
import matplotlib.pyplot as plt
sys.path.append('/home/darbymccauley/research/leuschner/leuschner_frb_detector/Leuschner_FRB_Detection/src/')
import fdmt as fdmt
IPython.embed()


