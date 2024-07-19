import numpy as np
from scipy.signal import resample
from .filters import filter_signal

def rectification(signal):
    """
    Rectify the EMG signal (absolute value).
    """
    return np.abs(signal)

def downsample(signal, original_rate, target_rate):
    """
    Downsample the signal from original_rate to target_rate using averaging.
    """
    # Calculate the downsample factor
    factor = int(original_rate / target_rate)
    
    # Use numpy's resample function for averaging
    downsampled_signal = resample(signal, len(signal) // factor)
    
    return downsampled_signal


def preprocess_emg(signal, original_rate=2000, target_rate=33.3, lowcut=None, highcut=None, order=4, btype='band'):
    """
    Preprocess the EMG signal: rectify, downsample, and low-pass filter.
    
    Parameters:
    - signal: Raw EMG signal.
    - original_rate: Original sampling rate of the signal (Hz).
    - target_rate: Target sampling rate after downsampling (Hz).
    - lowcut: Low cutoff frequency for the low-pass filter.
    - highcut: High cutoff frequency for the low-pass filter.
    - order: Order of the Butterworth filter.
    - btype: Type of the filter ('band', 'low', 'high', 'stop').
    """

    print("Original signal:", signal[:10])  # Print first 10 samples
    rectified_signal = rectification(signal)
    print("Rectified signal:", rectified_signal[:10])
    downsampled_signal = downsample(rectified_signal, original_rate, target_rate)
    print("Downsampled signal:", downsampled_signal[:10])
    filtered_signal = filter_signal(downsampled_signal, lowcut=lowcut, highcut=highcut, fs=target_rate, order=order, btype=btype)
    print("Filtered signal:", filtered_signal[:10])

    return filtered_signal




