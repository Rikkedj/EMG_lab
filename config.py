'''
Configuration values for the project. Paramters are used in the main.py file.
FILTER_BTYPE: Should be 'low', 'high', 'band' or 'stop' depending on the filter type. 
If you choose 'band' or 'stop' you have to specify both low and high cutoff frequencies, if you choose 'low' you have to specify the high cutoff frequency, 
if you choose 'high' you have to specify the low cutoff frequency.
'''
## Trigno Control Utility Setup
TCU_IP = '127.0.0.1'
COMMAND_PORT = 50040
EMG_PORT = 50043
ACC_PORT = 50044

# List of the of EMG sources in use
ACTIVE_CHANNELS = [6,7]

## EMG Preprocessing values
SENSOR_FREQ = 2000
PROCESSING_FREQ = 33.3
RAW_SIGNAL_GAIN = 1000 ## This should be changed in Lab 1, maybe remove to main script
RECTIFIED_SIGNAL_GAIN = 120
FILTER_LOW_CUTOFF_FREQUENCY = None
FILTER_HIGH_CUTOFF_FREQUENCY = 10
FILTER_ORDER = 4
FILTER_BTYPE = 'low'
HAND_DEADBAND_TRESHOLD = 0.7
WRIST_DEADBAND_TRESHOLD = 0.7
HAND_GAIN = 1.3
WRIST_GAIN = 1.3





