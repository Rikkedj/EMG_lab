import numpy as np
from scipy.signal import butter, filtfilt

def butter_filter(lowcut=None, highcut=None, fs=1.0, order=4, btype='band'):
    """
    Apply a Butterworth filter to the signal depending on the btype.
    
    Parameters:
    lowcut: low cutoff frequency
    highcut: high cutoff frequency
    fs: sampling frequency
    order: order of the Butterworth filter
    btype: type of filter ('band', 'low', 'high', 'stop')
    """
    nyq = 0.5 * fs  # Nyquist frequency
    low = None
    high = None

    if lowcut is not None:
        low = lowcut / nyq
    if highcut is not None:
        high = highcut / nyq

    # Ensure the parameters make sense for the specified filter type
    if btype == 'band':
        if low is None or high is None:
            raise ValueError("Both lowcut and highcut must be specified for bandpass filter")
        b, a = butter(order, [low, high], btype='band')
    elif btype == 'low':
        if high is None:
            raise ValueError("Highcut must be specified for lowpass filter")
        b, a = butter(order, high, btype='low')
    elif btype == 'high':
        if low is None:
            raise ValueError("Lowcut must be specified for highpass filter")
        b, a = butter(order, low, btype='high')
    elif btype == 'stop':
        if low is None or high is None:
            raise ValueError("Both lowcut and highcut must be specified for bandstop filter")
        b, a = butter(order, [low, high], btype='bandstop')
    else:
        raise ValueError("Invalid filter type. Choose from 'band', 'low', 'high', 'stop'.")

    return b, a


def filter_signal(emg_signal, lowcut=None, highcut=None, fs=1.0, order=4, btype='band'):
    b, a = butter_filter(lowcut, highcut, fs, order, btype)
    filtered_signal = filtfilt(b, a, emg_signal)
    return filtered_signal


'''
Preprocessiing signal. Have to seperate the signals into subarrays before processing.
'''

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
    print("trimmed_length from downsample", trimmed_length)
    trimmed_signal = signal[:trimmed_length]
    print("trimmed_signal from downsample", trimmed_signal)
    
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
    print("input signal", signal)
    rectified_signal = rectification(signal)
    print("rectified_signal", rectified_signal)
    downsampled_signal = downsample(rectified_signal, original_rate, target_rate)
    print("downsampled_signal", downsampled_signal)
    filtered_signal = filter_signal(downsampled_signal, lowcut=lowcut, highcut=highcut, fs=target_rate, order=order, btype=btype)
    

    return filtered_signal




