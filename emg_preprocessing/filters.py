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
    nyq = 0.5 * fs
    if lowcut is not None:
        low = lowcut / nyq
    if highcut is not None:
        high = highcut / nyq

    ## Can add an additional check to make sure if btype=low, highcut is None and if btype=high, lowcut is None, and if btype=band, both are not None
    if btype == 'band':
        b, a = butter(order, [low, high], btype='band')
    elif btype == 'low':
        b, a = butter(order, high, btype='low')
    elif btype == 'high':
        b, a = butter(order, low, btype='high')
    elif btype == 'stop':
        b, a = butter(order, [low, high], btype='bandstop')
    else:
        raise ValueError("Invalid filter type. Choose from 'band', 'low', 'high', 'stop'.")

    return b, a

def filter_signal(emg_signal, lowcut=None, highcut=None, fs=1.0, order=4, btype='band'):
    b, a = butter_filter(lowcut, highcut, fs, order, btype)
    filtered_signal = filtfilt(b, a, emg_signal)
    return filtered_signal
