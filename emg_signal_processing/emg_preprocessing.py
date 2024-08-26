import numpy as np
from scipy.signal import butter, filtfilt
import config
import time

def butter_filter(lowcut=None, fs=1.0, order=4, btype='low'):
    """
    Apply a Butterworth filter to the signal depending on the btype.
    
    Parameters:
    lowcut: low cutoff frequency
    fs: sampling frequency
    order: order of the Butterworth filter
    btype: type of filter ('low')
    """
    nyq = 0.5 * fs  # Nyquist frequency
    low = None

    if lowcut is not None:
        low = lowcut / nyq

    if btype == 'low':
        b, a = butter(order, low, btype='low')
    else:
        raise ValueError("Invalid filter type. Can only be lowpass.")

    return b, a


def filter_signal(emg_signal, lowcut=None, fs=1.0, order=4, btype='low'):
    b, a = butter_filter(lowcut=lowcut, fs=fs, order=order, btype=btype)
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
    """
    Preprocess the EMG signal: rectify, downsample, and filter.
    
    Parameters:
    - raw_emg_queue: The queue containing the raw EMG data.
    - preprocessed_emg_queue: The queue to append the preprocessed data to.
    """
    if not raw_emg_queue.is_empty():
        sample_index, raw_signal = raw_emg_queue.get_last()  # Get the last raw signal from the queue 
        print('Preprocessing index: ', sample_index)
        processed_emg = []
        for sensor in raw_signal:
            rectified = np.abs(sensor)
            downsampled = downsample(rectified, original_rate=config.SENSOR_FREQ, target_rate=config.PROCESSING_FREQ)
            gained = downsampled * config.RECTIFIED_SIGNAL_GAIN
            filtered = filter_signal(emg_signal=gained, lowcut=config.FILTER_LOW_CUTOFF_FREQUENCY, fs=config.PROCESSING_FREQ, order=config.FILTER_ORDER, btype='low')
            correct_mean = filtered - np.mean(filtered)

            processed_emg.append(correct_mean) # Filter, rectify, and downsample the raw signal

        preprocessed_emg_queue.append(processed_emg) # Add an array of the preprocessed data to all the sensors to the queue
        return processed_emg
    else:
        time.sleep(2)
        print('Waiting for raw data...')


def preprocess_raw_data_directly(raw_data, preprocessed_emg_queue): # Change queue to window
    """
    Preprocess the EMG signal: rectify, downsample, and filter.
    
    Parameters:
    - raw_emg_queue: The queue containing the raw EMG data.
    - preprocessed_emg_queue: The queue to append the preprocessed data to.
    """
    if not raw_data is None:
        processed_emg = []
        for sensor in raw_data:
            rectified = np.abs(sensor)
#            print('Rectified:', rectified)

            downsampled = downsample(rectified, original_rate=config.SENSOR_FREQ, target_rate=config.PROCESSING_FREQ)
            print('Downsampled:', downsampled)
            
            gained = downsampled * config.RECTIFIED_SIGNAL_GAIN
            print('Gained:', gained)
            
            filtered = filter_signal(gained, lowcut=config.FILTER_LOW_CUTOFF_FREQUENCY, fs=config.PROCESSING_FREQ, order=config.FILTER_ORDER, btype='low')
            correct_mean = filtered - np.mean(filtered)
            processed_emg.append(correct_mean) # Filter, rectify, and downsample the raw signal
            #rectified = np.abs(correct_mean)
#            processed_emg.append(rectified) # Filter, rectify, and downsample the raw signal

        preprocessed_emg_queue.append(processed_emg) # Add an array of the preprocessed data to all the sensors to the queue
        return processed_emg
    else:
        time.sleep(2)
        print('Waiting for raw data...')
