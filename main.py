import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
from emg_myoelectric_signal_processing import preprocess_emg
import config


def plot_signals(signal, plot_label = "Signal"):
    """
    Plot the original and processed EMG signals.
    
    Parameters:
    - signal: Signal you want to plot
    - plot_name: Name of the plot
    """
    # Creating time vectors for plotting
    time = np.arange(len(signal))

    # Plot processed signal
    plt.plot(time, signal, color='red', label=plot_label)
    plt.title('Processed EMG Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)

    # Display plots
    plt.tight_layout()
    plt.show()
    return 1



def main():
    fs = 2000  # Original sampling rate
    duration = 1  # 1 second of data
    t = np.linspace(0, duration, fs, endpoint=False)
    signal = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 50 * t)  # Example signal

    print("Original Signal:", signal)

    processed_signal = preprocess_emg(
        signal,
        original_rate=config.SENSOR_FREQ,
        target_rate=config.PROCESSING_FREQ,
        lowcut=config.FILTER_LOW_CUTOFF_FREQUENCY,
        highcut=config.FILTER_HIGH_CUTOFF_FREQUENCY,
        order=config.FILTER_ORDER,
        btype=config.FILTER_BTYPE
    )
    
    plot_signals(processed_signal, "Processed Signal")
    print("Processed Signal:", processed_signal)


if __name__ == "__main__":
    main()