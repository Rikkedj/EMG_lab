import numpy as np
from scipy.signal import resample
from .filters import filter_signal

def rectification(signal):
    """
    Rectify the EMG signal (absolute value).
    """
    return np.abs(signal)

def downsample(signal, original_rate, target_rate):
    factor = int(original_rate / target_rate)
    if factor <= 0:
        raise ValueError("Target rate must be less than the original rate")
    
    # Ensure the signal length is a multiple of the downsampling factor
    trimmed_length = len(signal) - (len(signal) % factor)
    trimmed_signal = signal[:trimmed_length]
    
    # Reshape and average
    downsampled_signal = trimmed_signal.reshape(-1, factor).mean(axis=1)
    return downsampled_signal

def preprocess_emg(signal, original_rate=2000, target_rate=33.3, lowcut=None, highcut=None, order=4, btype='band'):
    """
    Preprocess the EMG signal: rectify, downsample, and filter.
    
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




