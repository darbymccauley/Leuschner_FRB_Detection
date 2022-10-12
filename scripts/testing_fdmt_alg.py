import argparse
import numpy as np
import sys 

sys.path.append('/home/darbymccauley/research/leuschner/leuschner_frb_detector/Leuschner_FRB_Detection/src/')

import fdmt as fdmt 

parser = argparse.ArgumentParser(description='Run FDMT algorithm')
parser.add_argument('file', help='path to file with data in it')
parser.add_argument('f_min', help='Beginning frequency of base-band')
parser.add_argument('f_max', help='Ending frequency of base-band')
parser.add_argument('maxDT', help='Maximal delay (in time bins) of the maximal dispersion')
parser.add_argument('dataType', help='Type of data (int32 or int64 recommended)')

args = parser.parse_args()
IMAGE = np.loadtxt(args.file)
FMIN = float(args.f_min)
FMAX = float(args.f_max)
MAXDT = float(args.maxDT)
DATATYPE = args.dataType

dmt = fdmt.FDMT(IMAGE, FMIN, FMAX, MAXDT, DATATYPE)

import IPython; IPython.embed()

