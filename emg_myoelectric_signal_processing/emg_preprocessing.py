import numpy as np
from scipy.signal import butter, filtfilt
import config
import time

def butter_filter(lowcut=None, highcut=None, fs=1.0, order=4, btype='low'):
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


def filter_signal(emg_signal, lowcut=None, highcut=None, fs=1.0, order=4, btype='low'):
    b, a = butter_filter(lowcut=lowcut, highcut=highcut, fs=fs, order=order, btype=btype)
    filtered_signal = filtfilt(b, a, emg_signal)
    return filtered_signal


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


def preprocess_raw_data(raw_emg_queue, preprocessed_emg_queue): # Change queue to window
    if not raw_emg_queue.is_empty():
        raw_signal = raw_emg_queue.get_last()  # Get the last raw signal from the queue 
        processed_emg = []
        for sensor in raw_signal:
            rectified = np.abs(sensor)
            downsampled = downsample(rectified, original_rate=config.SENSOR_FREQ, target_rate=config.PROCESSING_FREQ)
            gained = downsampled * config.RECTIFIED_SIGNAL_GAIN
            filtered = filter_signal(gained, lowcut=config.FILTER_LOW_CUTOFF_FREQUENCY, highcut=config.FILTER_HIGH_CUTOFF_FREQUENCY, fs=config.PROCESSING_FREQ, order=config.FILTER_ORDER, btype=config.FILTER_BTYPE)
            processed_emg.append(filtered) # Filter, rectify, and downsample the raw signal

        preprocessed_emg_queue.append(processed_emg) # Add an array of the preprocessed data to all the sensors to the queue
        return processed_emg
    else:
        time.sleep(2)
        print('Waiting for raw data...')



'''
def preprocess_emg(signal, original_rate=2000, target_rate=33.3, lowcut=None, highcut=None, order=4, btype='low'):
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
    rectified_signal = np.abs(signal)
    downsampled_signal = downsample(rectified_signal, original_rate, target_rate)
    gained_signal = downsampled_signal * config.RECTIFIED_SIGNAL_GAIN
    filtered_signal = filter_signal(gained_signal, lowcut=lowcut, highcut=highcut, fs=target_rate, order=order, btype=btype)
    
    return filtered_signal

'''