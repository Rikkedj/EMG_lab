import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
from emg_myoelectric_signal_processing import preprocess_emg, split_emg_data, apply_gain
import config
import pandas as pd

def load_emg_data_csv(file_path):
    """
    Load EMG data from a CSV file with European decimal and delimiter handling.

    Args:
        file_path (str): The path to the CSV file containing the EMG data.

    Returns:
        pd.DataFrame: A DataFrame containing the EMG data.
    """
    try:
        # Read the CSV file with semicolon as delimiter and comma as decimal separator
        df = pd.read_csv(file_path, delimiter='\t', decimal=',')
      
        # If the initial attempt fails, try other possible delimiters
        if df.shape[1] == 1:
            # Try with a semicolon if tabs don't work
            df = pd.read_csv(file_path, sep=';', decimal=',', encoding='utf-8')

        # Rename columns to avoid duplication
        df.columns = [
            'Time_EMG_1', 'Signal_EMG_1', 
            'Time_EMG_2', 'Signal_EMG_2', 
            'Time_EMG_3', 'Signal_EMG_3', 
            'Time_EMG_4', 'Signal_EMG_4'
        ]

        # Display basic information about the data
        print("CSV Data loaded successfully!")
        print(f"Number of sensors (columns): {df.shape[1] // 2}")
        print(f"Number of samples (rows): {df.shape[0]}")
        print(f"Column names (sensor labels): {list(df.columns)}")

        # Return the DataFrame
        return df

    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return None



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
    
    ## Bedre å gjøre dette i main i guess

def plot_combined_emg_signals(emg_1, emg_2, emg_3, emg_4):
    """
    Plot all EMG sensor signals in the same plot for comparison.

    Args:
        emg_1 (np.ndarray): 2xN array for sensor 1.
        emg_2 (np.ndarray): 2xN array for sensor 2.
        emg_3 (np.ndarray): 2xN array for sensor 3.
        emg_4 (np.ndarray): 2xN array for sensor 4.
    """
    time = np.arange(len(emg_1))
    plt.figure(figsize=(14, 6))
    
    # Plot each sensor's signal on the same plot
    plt.plot(time, emg_1, label='EMG Sensor 1', color='b')
    plt.plot(time, emg_2, label='EMG Sensor 2', color='g')
    plt.plot(time, emg_3, label='EMG Sensor 3', color='r')
    plt.plot(time, emg_4, label='EMG Sensor 4', color='m')
    
    # Add labels, title, legend, and grid
    plt.xlabel('Time [samples]')
    plt.ylabel('Signal Value')
    plt.title('Combined EMG Signals from All Sensors')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    RAW_SIGNAL_GAIN = 1000  #Change this in lab 1
    ### Plot raw signal here
    raw_signals = load_emg_data_csv('./test_data/emg_raw1.csv')
    print("Raw Signal:", raw_signals)
    raw_signals = apply_gain(raw_signals, RAW_SIGNAL_GAIN)
    splitted_signals = split_emg_data(raw_signals)
    emg_sig1 = splitted_signals[0][:]
    emg_sig2 = splitted_signals[1][:]
    emg_sig3 = splitted_signals[2][:]
    emg_sig4 = splitted_signals[3][:]

    ## Duplicated for now, change bhow preprocess_emg works. This is now hard coded, but need a way to detect how many sensors are used, and only extract and process those
    processed_signal_1 = preprocess_emg(
        emg_sig1[1][:],
        original_rate=config.SENSOR_FREQ,
        target_rate=config.PROCESSING_FREQ,
        lowcut=config.FILTER_LOW_CUTOFF_FREQUENCY,
        highcut=config.FILTER_HIGH_CUTOFF_FREQUENCY,
        order=config.FILTER_ORDER,
        btype=config.FILTER_BTYPE
    )
    
    processed_signal_2 = preprocess_emg(
        emg_sig2[1][:],
        original_rate=config.SENSOR_FREQ,
        target_rate=config.PROCESSING_FREQ,
        lowcut=config.FILTER_LOW_CUTOFF_FREQUENCY,
        highcut=config.FILTER_HIGH_CUTOFF_FREQUENCY,
        order=config.FILTER_ORDER,
        btype=config.FILTER_BTYPE
    )
    processed_signal_3 = preprocess_emg(
        emg_sig3[1][:],
        original_rate=config.SENSOR_FREQ,
        target_rate=config.PROCESSING_FREQ,
        lowcut=config.FILTER_LOW_CUTOFF_FREQUENCY,
        highcut=config.FILTER_HIGH_CUTOFF_FREQUENCY,
        order=config.FILTER_ORDER,
        btype=config.FILTER_BTYPE
    )
    processed_signal_4 = preprocess_emg(
        emg_sig4[1][:],
        original_rate=config.SENSOR_FREQ,
        target_rate=config.PROCESSING_FREQ,
        lowcut=config.FILTER_LOW_CUTOFF_FREQUENCY,
        highcut=config.FILTER_HIGH_CUTOFF_FREQUENCY,
        order=config.FILTER_ORDER,
        btype=config.FILTER_BTYPE
    )
    print("Processed Signal:", processed_signal_1)
    #plot_signals(processed_signal_1, "Processed Signal 1")
    plot_combined_emg_signals(processed_signal_1, processed_signal_2, processed_signal_3, processed_signal_4)

if __name__ == "__main__":
    main()