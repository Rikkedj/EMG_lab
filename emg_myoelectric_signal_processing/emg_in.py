import numpy as np

# Do this in main atm, dont need this
def read_emg_signal():
    # FOR NOW: SIMULATE READING
    emg_signal = np.random.rand(1000) # Simmulating EMG data - FOR LATER: use libemg to read data from DELSYS database
    return emg_signal

## Apply raw EMG signal gain
def apply_gain(emg_signal, gain):
    return emg_signal * gain

""" ## Split EMG signal into 4 individual signals
def split_emg_signal(emg_signal):
    emg_signal_1 = emg_signal[:, 0]
    emg_signal_2 = emg_signal[:, 1]
    emg_signal_3 = emg_signal[:, 2]
    emg_signal_4 = emg_signal[:, 3]
    return emg_signal_1, emg_signal_2, emg_signal_3, emg_signal_4
 """
def split_emg_data(df):
    """
    Split EMG data into separate arrays for each sensor.

    Args:
        df (pd.DataFrame): The DataFrame containing the EMG data.

    Returns:
        list: A list of 2xN NumPy arrays, each representing a sensor's time and signal data.
    """
    num_sensors = df.shape[1] // 2  # Calculate the number of sensors
    sensor_arrays = []  # List to store the arrays for each sensor

    for sensor_num in range(1, num_sensors + 1):
        # Extract time and signal columns for the current sensor
        time_column = f'Time_EMG_{sensor_num}'
        signal_column = f'Signal_EMG_{sensor_num}'
        
        time_data = df[time_column].values  # Get time data as a NumPy array
        signal_data = df[signal_column].values  # Get signal data as a NumPy array

        # Combine time and signal data into a 2xN array
        sensor_array = np.vstack((time_data, signal_data))
        
        # Append the sensor array to the list
        sensor_arrays.append(sensor_array)

    return sensor_arrays