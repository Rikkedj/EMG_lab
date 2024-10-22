import numpy as np
import matplotlib.pyplot as plt
import feature_extraction as fe

''' Test functions'''
def test_features_calculation_time(raw_emg):
    time_vec = []
    for i in range(100):
        start = time.time()
        fe.EMGaac(raw_emg)
        time_vec.append(time.time()-start)
    
    return np.mean(time_vec)

def generate_synthetic_emg(n_samples=1000, n_channels=8, freqs=[10, 20], amplitudes=[1, 0.5], noise_level=0.1, dc_offset=0):
    """
    Generate a synthetic EMG signal.
    
    Parameters:
    - n_samples: Number of samples in the signal.
    - n_channels: Number of EMG channels (sources).
    - freqs: List of frequencies for the sine waves.
    - amplitudes: List of amplitudes for the sine waves.
    - noise_level: Standard deviation of the added Gaussian noise.
    - dc_offset: DC offset added to the signal.
    
    Returns:
    - Synthetic EMG data array of shape (n_samples, n_channels).
    """
    t = np.linspace(0, 1, n_samples)
    emg_data = np.zeros((n_samples, n_channels))
    
    for channel in range(n_channels):
        # Create a signal by summing sine waves with different frequencies and amplitudes
        signal = np.zeros(n_samples)
        for freq, amp in zip(freqs, amplitudes):
            signal += amp * np.sin(2 * np.pi * freq * t)
        
        # Add Gaussian noise
        noise = np.random.normal(0, noise_level, n_samples)
        
        # Add DC offset
        signal += dc_offset
        
        # Combine the sine waves, noise, and DC offset for each channel
        emg_data[:, channel] = signal + noise
    
    return emg_data

def test_emg_feature_extraction(data):
    # Generate synthetic EMG data
    #data = generate_synthetic_emg(n_samples=1000, n_channels=8)
    
    # Test all feature extraction functions and print the results
    print("AAV:", fe.EMGaav(data))
    print("Variance:", fe.EMGvar(data))
    print("Zero-crossings:", fe.EMGzc(data))
    print("Wavelength:", fe.EMGwaveL(data))
    print("Number of turns:", fe.EMGnt(data))
    print("Myopulse percentage rate:", fe.EMGmyop(data))
    print("Histogram (10 bins):", fe.EMGhist(data, nBins=10))
    print("Autoregressive coefficients (order 4):", fe.EMGar(data, p=4))
    print("Average Amplitude Change (AAC):", fe.EMGaac(data))
    print("Slope Sign Changes (SSC):", fe.EMGssc(data))
    print("Mean Absolute Value (MAV):", fe.EMGmav(data))
    print("Mean Square Value (MSV):", fe.EMGmsv(data))
    print("Root Mean Square (RMS):", fe.EMGrms(data))
    print("Wilson Amplitude (WAMP):", fe.EMGwamp(data))

def plot_test_signal(emg_data, sample_rate=1000):
    """
    Plot the synthetic EMG signal for each channel.
    
    Parameters:
    - emg_data: The EMG data array of shape (n_samples, n_channels).
    - sample_rate: Sampling rate in Hz (default: 1000 Hz).
    """
    n_samples, n_channels = emg_data.shape
    time = np.linspace(0, n_samples / sample_rate, n_samples)
    
    # Create a figure and subplots for each channel
    fig, axs = plt.subplots(n_channels, 1, figsize=(12, 2 * n_channels), sharex=True)
    fig.suptitle("Synthetic EMG Signal for Each Channel", fontsize=16)
    
    # Plot each channel's data
    for i in range(n_channels):
        axs[i].plot(time, emg_data[:, i], label=f'Channel {i+1}')
        axs[i].set_ylabel("Amplitude")
        axs[i].legend(loc='upper right')
        axs[i].grid(True)
    
    axs[-1].set_xlabel("Time (s)")
    plt.tight_layout(rect=[0, 0, 1, 0.97])  # Adjust layout to make room for the title
    plt.show()
