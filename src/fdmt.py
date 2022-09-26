import numpy as np
import time
import sys
import logging


# logger = logging.getLogger(__name__)

# sys.path.append('/mnt/c/Users/darby/OneDrive/Desktop/Leuschner_FRB_Detection/src/')

# import _cart

DISPERSION_CONSTANT = 4.148808*10**9 # [Mhz * pc^-1 * cm^3]
Verbose = False

def FDMT(Image, f_min, f_max, maxDT, dataType, Verbose=True):
    N_f, N_t = Image.shape
    niters = int(np.log2(N_f))
    if (N_f not in [2**i for i in range(1,30)]) or (N_t not in [2**i for i in range(1, 30)]):
        raise NotImplementedError('Input dimensions must be a power of 2.')
    
    x = time.time()
    State = FDMT_initialization(Image, f_min, f_max, maxDT, dataType)
    # PDB('Initialization complete.') # XXX logger
    
    for i in range(1, niters+1):
        State = FDMT_iteration(State, f_min, f_max, maxDT, dataType, N_f, i, Verbose)
    # PDB('total_time:', time.time() - x) # XXX logger
    [F, dT, T] = State.shape
    DMT = np.reshape(State, [dT,T])
    return DMT


def FDMT_initialization(Image, f_min, f_max, maxDT, dataType):
    [N_f, N_t] = Image.shape

    delta_f = (f_max - f_min)/N_f
    N_D = maxDT-1
    delta_t = int( np.ceil( N_D * ((f_min**-2 - (f_min+delta_f)**-2) / (f_min**-2 - f_max**-2)) ) )

    Output = np.zeros([N_f, delta_t+1, N_t], dataType)
    Output[:,0,:] = Image

    for i_delta_t in range(1, delta_t+1):
        Output[:, i_delta_t, i_delta_t:] = Output[:, i_delta_t-1, i_delta_t:] + Image[:, :-i_delta_t]
    return Output


def FDMT_iteration(Input, f_min, f_max, maxDT, dataType, N_f, iteration_num, Verbose=False):
    input_dims = Input.shape
    output_dims = list(input_dims)

    delta_f = (f_max - f_min)/N_f
    delta_F = 2**iteration_num * delta_f
    # the maximum delta_t needed to calculate the ith iteration
    N_D = maxDT-1
    delta_t = int( np.ceil( N_D * ((f_min**-2 - (f_min+delta_F)**-2) / (f_min**-2 - f_max**-2)) ) )
    # PDB("deltaT = ",deltaT) # XXX logger
    # PDB("N_f = ",F/2.**(iteration_num)) # XXX logger
    # PDB('input_dims', input_dims) # XXX logger

    output_dims[0] = output_dims[0]//2

    output_dims[1] = delta_t + 1
    # PDB('output_dims', output_dims) # XXX logger
    Output = np.zeros(output_dims, dataType)

    ShiftOutput = 0
    ShiftInput = 0
    T = output_dims[2]

    F_jumps = output_dims[0]

    if iteration_num > 0:
        correction = delta_f/2
    else:
        correction = 0

    for i_F in range(F_jumps):
        f_start = (f_max - f_min)/F_jumps * (i_F) + f_min
        f_end = (f_max - f_min)/F_jumps * (i_F+1) + f_min
        f_middle = (f_end - f_start)/2 + f_start - correction
        f_middle_larger = (f_end - f_start)/2 + f_start + correction
        delta_t_local = int( np.ceil( N_D * ((f_start**-2 - f_end**-2) / (f_min**-2 - f_max**-2)) ) )

        for i_dT in range(delta_t_local+1):
            dT_middle = int( round(i_dT * (f_middle**-2 - f_start**-2) / (f_end**-2 - f_start**-2)) )
            dT_middle_index = dT_middle + ShiftInput
            dT_middle_larger = int( round(i_dT * (f_middle_larger**-2 - f_start**-2) / (f_end**-2 - f_start**-2)) )
            
            dT_rest = i_dT - dT_middle_larger
            dT_rest_index = dT_rest + ShiftInput

            i_T_min = 0
            i_T_max = dT_middle_larger

            Output[i_F, i_dT+ShiftOutput, i_T_min:i_T_max] = Input[2*i_F, dT_middle_index, i_T_min:i_T_max]

            i_T_min = dT_middle_larger
            i_T_max = T

            

            print(i_T_max-dT_middle_larger, np.abs(i_T_max-dT_middle_larger))
            # print(Output[i_F, i_dT+ShiftOutput, i_T_min:i_T_max].shape, Input[2*i_F, dT_middle_index, i_T_min:i_T_max].shape, Input[2*i_F+1, dT_rest_index, i_T_min-dT_middle_larger:i_T_max-dT_middle_larger].shape)
            Output[i_F, i_dT+ShiftOutput, i_T_min:i_T_max] = Input[2*i_F, dT_middle_index, i_T_min:i_T_max] + Input[2*i_F+1, dT_rest_index, i_T_min-dT_middle_larger:i_T_max-dT_middle_larger]
    
    return Output


