import numpy as np

def read_emg_signal():
    # FOR NOW: SIMULATE READING
    emg_signal = np.random.rand(1000) # Simmulating EMG data - FOR LATER: use libemg to read data from DELSYS database
    return emg_signal

## Apply raw EMG signal gain
def apply_gain(emg_signal, gain):
    return emg_signal * gain

## Split EMG signal into 4 individual signals
def split_emg_signal(emg_signal):
    emg_signal_1 = emg_signal[:, 0]
    emg_signal_2 = emg_signal[:, 1]
    emg_signal_3 = emg_signal[:, 2]
    emg_signal_4 = emg_signal[:, 3]
    return emg_signal_1, emg_signal_2, emg_signal_3, emg_signal_4