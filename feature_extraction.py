import numpy as np
import scipy.signal
#import pywt

'''AAV: Average Absolute Value'''
def EMGaav(data):
    nSamples, nSources = data.shape
    AAV = np.zeros(nSources)
    for iSource in range(nSources):
    #for i in range(data.shape[1]):
        AAV[iSource] = np.mean(np.abs(data[:, iSource]))
    
    return AAV.T


'''Calculates the variance of EMG data for each channel (column of data).'''
def EMGvar(data):
    VAR = np.var(data, axis=0)
    #VAR = np.zeros(data.shape[1])
    #for i in range(data.shape[1]):
    #    VAR[i] = np.var(data, axis=1)
    return VAR


'''Counts the number of zero-crossings in the EMG signal for each channel. A zero-crossing occurs when the signal changes sign between two samples.'''
def EMGzc(data):
    nSamples, nSources = data.shape
    threshold = 0
    ZC = np.zeros(nSources)
    for iSource in range(nSources):
        x_i = data[:-1, iSource] # all elements except the last one
        x_i1 = data[1:, iSource] # all elements except the first one
        ZC[iSource] = np.sum(np.sign(-x_i * x_i1) > threshold)
    return ZC

''' Calculates the wavelength by summing the absolute differences between consecutive samples for each channel.'''
def EMGwaveL(X, config=None):
    nSamples, nSources = X.shape
    WAVE = np.zeros(nSources)
    for source in range(nSources):
        Xwl = X[1:, source]
        Xwl1 = X[:-1, source]  # x_i-1
        Xwave = np.abs(Xwl - Xwl1)
        WAVE[source] = np.sum(Xwave)
    return WAVE

'''Calculates the number of turns in the EMG signal, which is the number of times the signal slope changes sign.'''
def EMGnt(data, config=None):
    nSamples, nSources = data.shape
    NT = np.zeros(nSources)
    for iSource in range(nSources):
        x = data[:-2, iSource] # x_i
        x1 = data[1:-1, iSource] # x_i+1
        x2 = data[2:, iSource] # x_i+2
        NT[iSource] = np.sum(np.sign(-(x1 - x) * (x2 - x1)) > 0)
    return NT

'''Calculates the myopulse percentage rate, which is the proportion of time the signal is above a specified threshold.'''
def EMGmyop(data, config=None, threshold=0.025):
    _, nSources = data.shape
    MYOP = np.zeros(nSources)
    for iSource in range(nSources):
        x = data[:, iSource]
        MYOP[iSource] = np.mean(x > threshold)
    return MYOP

'''Calculates the histogram of the EMG signal for each channel, with a specified number of bins.'''
def EMGhist(data, config=None, nBins=10):
    nSamples, nSources = data.shape
    HST = []
    for iSource in range(nSources):
        xhist, _ = np.histogram(data[:, iSource], bins=nBins)
        HST.append(xhist)
    return HST

'''Calculates autoregressive (AR) model coefficients of the EMG signal. It uses the Levinson-Durbin recursion to solve the Yule-Walker equations.'''
def EMGar(data, config=None, p=4):
    AR = []
    for i in range(data.shape[1]):
        x = data[:, i]
        R = np.correlate(x, x, mode='full')[-x.size:]
        A = np.polyfit(R, x, deg=p)
        AR.append(-A[1:p+1])
    return np.array(AR)

'''Calculates the average amplitude change (AAC) of the EMG signal, which is the mean of the absolute differences between consecutive samples.'''
def EMGaac(data, config=None):
    nSamples, nSources = data.shape
    AAC = np.zeros(nSources)
    for iSource in range(nSources):
        x = data[:-1, iSource] # x_i
        x1 = data[1:, iSource] # x_i+1
        AAC[iSource] = np.mean(np.abs(x1 - x))
    return AAC

'''Caculates the slope sign changes (SSC) of the EMG signal, which is the number of times the slope of the waveform changes sign.'''
def EMGssc(data, config=None, threshold=0):
    nSamples, nSources = data.shape
    SSC = np.zeros(nSources)
    for iSource in range(nSources):
        x_prev = data[:-2, iSource]   # x_(i-1)
        x_curr = data[1:-1, iSource]  # x_i
        x_next = data[2:, iSource]    # x_(i+1)

        product = (x_curr - x_prev) * (x_curr - x_next)
        SSC[iSource] = np.sum(product > threshold)
    return SSC

'''Calculates the Mean Absolute Value (MAV) of the EMG signal for each channel.'''
def EMGmav(data):
    return np.mean(np.abs(data), axis=0)

'''Calculates the Mean Square Value (MSV) of the EMG signal for each channel.'''
def EMGmsv(data):
    return np.mean(data**2, axis=0)

'''Calculates the Root Mean Square (RMS) of the EMG signal for each channel.'''
def EMGrms(data):
    return np.sqrt(np.mean(data**2, axis=0))

'''Calculates the The Wilson Amplitude (WAMP) of the EMG signal for each channel. Counts the number of times the difference between consecutive samples exceeds a threshold, indicating significant signal changes. '''
def EMGwamp(data, threshold=0.1):
    diff = np.abs(np.diff(data, axis=0))
    return np.sum(diff > threshold, axis=0)



def feature_extraction(EMG_signal, config=None):
    '''Extracts features from the EMG signal using a set of feature extraction functions.'''
    features = []
    features.append(EMGaav(EMG_signal)) # same as mav
    features.append(EMGvar(EMG_signal))
    features.append(EMGzc(EMG_signal))
    features.append(EMGwaveL(EMG_signal))
    features.append(EMGnt(EMG_signal))
    features.append(EMGmyop(EMG_signal))
    #features.append(EMGhist(EMG_signal)) # Denne blir til en matrise, ikke smme dimensjoner som de andre. Finn ut av hvordan det funker
    #features.append(EMGar(EMG_signal)) # DOES NOT WORK ATM
    features.append(EMGaac(EMG_signal))
    features.append(EMGssc(EMG_signal))
   # features.append(EMGmav(EMG_signal))
    features.append(EMGmsv(EMG_signal))
    features.append(EMGrms(EMG_signal))
    features.append(EMGwamp(EMG_signal))

    return np.concatenate(features) # Returns a single array of all features


# ################# Frequency functions, not sure if they are right - double check! #################
# '''Windowed Fourier Transform (WF). Calculates the frequency domain representation of a signal over windows.'''
# def EMGwf(data, window_size=256, overlap=128):
#     freqs, times, Sxx = scipy.signal.spectrogram(data, nperseg=window_size, noverlap=overlap, axis=0)
#     return freqs, times, Sxx  # Returns frequencies, times, and spectrogram of the signal

# '''Wavelet Packet Transform (WPT). Decomposes the signal using wavelet packets to capture both time and frequency information.'''
# def EMGwpt(data, wavelet='db4', level=4):
#     wpt_features = []
#     for iSource in range(data.shape[1]):
#         wp = pywt.WaveletPacket(data=data[:, iSource], wavelet=wavelet, mode='symmetric', maxlevel=level)
#         features = [node.data for node in wp.get_level(level, 'freq')]
#         wpt_features.append(np.concatenate(features))
#     return np.array(wpt_features)

# '''Wavelet Transform (WT). Uses wavelets to decompose the signal and extract frequency and time information.'''
# def EMGwt(data, wavelet='db4', level=4):
#     wt_features = []
#     for iSource in range(data.shape[1]):
#         coeffs = pywt.wavedec(data[:, iSource], wavelet, level=level)
#         wt_features.append(np.concatenate(coeffs))
#     return np.array(wt_features)
