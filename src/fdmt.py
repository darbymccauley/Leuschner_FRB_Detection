import numpy as np
import matplotlib.pyplot as plt
# import time
# import sys


DispersionConstant = 4.148808e6 


def FDMT(Image, f_min, f_max, maxDT, dataType):
    N_f, N_t = Image.shape
    niters = int(np.log2(N_f))
    if (N_f not in [2**i for i in range(1, 30)]) or (N_t not in [2**i for i in range(1, 30)]):
        raise NotImplementedError('Input dimensions must be a power of 2.')
    
    State = FDMT_initialization(Image, f_min, f_max, maxDT, dataType)
    # PDB('Initialization complete.') # XXX logger
    
    for i in range(1, niters+1):
        State = FDMT_iteration(State, f_min, f_max, maxDT, dataType, N_f, i)
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


def FDMT_iteration(Input, f_min, f_max, maxDT, dataType, N_f, iteration_num):
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
            
            Output[i_F, i_dT+ShiftOutput, i_T_min:i_T_max] = Input[2*i_F, dT_middle_index, i_T_min:i_T_max] + Input[2*i_F+1, dT_rest_index, i_T_min-dT_middle_larger:i_T_max-dT_middle_larger]
    
    return Output

def compute_DM(DMT, f_min, f_max, t_samp):
    dmt_max_index = np.argmax(DMT)
    i_dm_max, i_t_max = np.unravel_index(dmt_max_index, shape=DMT.shape)
    dm = (i_dm_max*t_samp)/(DispersionConstant*(f_min**-2 - f_max**-2))
    return dm


def pulse_delay(freq, DM):
    """
    Computes the dispersion measure dependent time delay of pulse at
    a given frequency.

    Inputs:
        - freq [MHz]: frequency
        - DM [pc*cm^-3]: dispersion measure
    Returns: pulse time delay [ms]
    """
    return (DispersionConstant * DM)/(freq**2)


def dedisperse(Image, f_min, f_max, t_samp, plot=False):
    nchans, nspec = Image.shape

    t_min, t_max = 0, nspec*t_samp
    freqs = np.linspace(f_min, f_max, nchans)

    dmt = FDMT(Image, f_min, f_max, nspec, 'int64')
    measured_dm = compute_DM(dmt, f_min, f_max, t_samp)

    delays = pulse_delay(freqs, measured_dm)
    bins = delays/t_samp
    rounded_bins = np.round(bins).astype(int)

    for i in range(len(Image)):
        Image[i] = np.roll(Image[i], -rounded_bins[i])

    if plot:
        fig, ax = plt.subplots(constrained_layout=True)
        im = ax.imshow(Image, aspect='auto', origin='lower', extent=[t_min, t_max, f_min, f_max])

        ax.set_xlabel('Time [ms]')
        ax.set_ylabel('Frequency [MHz]')
        ax.set_xlim(t_min, t_max)
        ax.set_ylim(f_min, f_max)

        ax2 = ax.twinx()
        ax2.set_ylim(0, nchans)
        ax2.set_ylabel('Channel', rotation=270, labelpad=10)
        
        ax3 = ax.twiny()
        ax3.set_xlim(0, nspec)
        ax3.set_xlabel('Spectrum', labelpad=10)

        plt.show();

    return Image








def HybridDedispersion(SNAP_signal, t_samp, pulse_width, max_dm, f_min, f_max, SigmaBound=10):
    """
    -- STILL A WORK IN PROGRESS --
    For now, this function takes in a pulse_width. I want to eventually find a way to
    remove this input param. I want this function to continuously run and look for pulses
    independent of pulse width or other pulse parameters. I want it to be a general function.
    This will likely require some minimum threshold power requirements that will roughly detect
    the upper and lower bounds (width) of the pulse, which is then used to compute N_p and
    we are off to the races. 


    Inputs:
        - SNAP_signal: frequency vs. time power matrix. Output of the SNAP.
        - t_samp [ms]: sampling time/time resolution
        - pulse_width [ms]: width of the FRB pulse
        - max_dm [pc*cm^-3]: maximal dispersion measure to scan
        - f_min [MHz]: minimum frequency of the base band
        - f_max [MHz]: maximum frequency of the base band
        - SigmaBound: the minimum statistical significance to trigger the saving of a result
    """
    N_f, N_t = SNAP_signal.shape
    N_total =  N_f*N_t

    # # Look at each spectra and determine the pulse width
    # for i in range(N_t):
    #     spec = SNAP_signal[:, i]

    N_p = pulse_width/t_samp

    f = np.arange(0, f_max-f_min, (f_max-f_min)/N_total)

    ConversionConst = DispersionConstant * (f_min**-2 - f_max**-2) * (f_max - f_min)
    N_d = max_dm * ConversionConst

    n_coherent = int(np.ceil(N_d/(N_p**2)))
    print('Number of coherent dedispersion iterations:', n_coherent)

    FDMT_normalization = FDMT(np.ones([N_f, N_t]), f_min, f_max, N_t, 'int64')

    for i in range(n_coherent):
        print('Coherent iteration', i)
        cur_coherent_dm = i * (max_dm/n_coherent)
        print('Current DM being tested:', cur_coherent_dm)

        d = DispersionConstant * cur_coherent_dm
        H = np.exp( -((2*np.pi*1j*d)/(f_min+f)) - ((2*np.pi*1j*d*f)/(f_max**2)) )
        H_power = np.abs(H.reshape(N_f, N_t))**2

        FDMT_input = SNAP_signal * H_power
        # FDMT_input -= np.mean(FDMT_input)
        # FDMT_input /= 0.25*np.std(FDMT_input)
        # V = np.var(FDMT_input)
        
        DMT = FDMT(FDMT_input, f_min, f_max, N_t, 'int64')
        # DMT /= np.sqrt(FDMT_normalization*V + 1e-6)
        
        if np.max(DMT) > SigmaBound:
            SigmaBound = np.max(DMT)
            # measured_DM = compute_DM(DMT, f_min, f_max, t_samp)
            print('FRB detected! \nMeasured DM of FRB event:', cur_coherent_dm, 'pc*cm^-3. \nAchieved score with', SigmaBound, 'sigmas.')



    