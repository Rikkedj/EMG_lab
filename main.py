import sys
import os
import signal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import matplotlib.pyplot as plt
import plots
from emg_signal_processing import emg_in, emg_preprocessing, myoprocessor, to_prosthesis
import time, threading
import pyserial
from classes import ThreadSafeState, ThreadSafeQueue
import serial.tools.list_ports
import serial


plt.switch_backend('TkAgg')

# Event to stop threads. To handle keyboard interruptions, like ctrl-c, we need a signal handler and an event to be passed to the threads.
stop_event = threading.Event()  
def signal_handler(sig, frame):
    print("\nInterrupt received. Stopping threads and exiting...")
    stop_event.set()  # Set the stop event to True
    sys.exit(0)  # Exit the program
signal.signal(signal.SIGINT, signal_handler)  # Register the signal handler


# Initialize queues for raw data, processed data, and prosthesis setpoints
WINDOW_SIZE = 5
raw_emg_queue = ThreadSafeQueue(window_size=WINDOW_SIZE)
preprocessed_emg_queue = ThreadSafeQueue(window_size=WINDOW_SIZE)
prosthesis_setpoint_queue = ThreadSafeQueue(window_size=WINDOW_SIZE)

# Initialize states for hand/wrist control and cocontraction
cocontraction = ThreadSafeState()
hand_or_wrist = ThreadSafeState()




def main():
    # Initialize connection to Trigno EMG
    dev = emg_in.trigno_startup(stop_event=stop_event)

    # Initialize connection to serial port
    try:
        SERIAL_PORT = 'COM6'  # Replace 'COM6' with your port. Should make something that finds the port automatically.
        ser = serial.Serial(SERIAL_PORT, baudrate=9600, timeout=1)  # Open serial port
    except serial.SerialException as e:
        print("Error opening serial port:", e)
        ser = None
    except Exception as e:
        print("Unknown error:", e)
        ser = None

    # Define threads for data processing
    def data_processing_thread():
        try:
            while not stop_event.is_set():
                raw_data = emg_in.read_raw_data(dev, raw_emg_queue=raw_emg_queue)
                #preprocessed_data = emg_preprocessing.preprocess_raw_data(raw_emg_queue=raw_emg_queue, preprocessed_emg_queue=preprocessed_emg_queue)
                preprocessed_data = emg_preprocessing.preprocess_raw_data_directly(raw_data=raw_data, preprocessed_emg_queue=preprocessed_emg_queue)

                #hand_controll, wrist_controll = myoprocessor.myoprocessor_controll(preprocessed_emg_queue, hand_or_wrist, cocontraction)
                hand_controll, wrist_controll = myoprocessor.myoprocessor_controll_directly(preprocessed_data, hand_or_wrist, cocontraction)
                setpoints = to_prosthesis.prosthesis_setpoints(prosthesis_setpoint_queue, hand_controll, wrist_controll)

                #if ser.is_open:
                #    pyserial.write_to_hand(ser=ser, setpoints=setpoints)
                    #print('wsetpoints:', setpoints)
                #else:
                #    print("Serial port is not open")

        except Exception as e:
            print("Unknown error:", e)
            stop_event.set()


    # Start data processing thread
    processing_thread = threading.Thread(target=data_processing_thread)
    processing_thread.start()
    # Start plotting in the main thread
    plots.plot_all_signals(raw_emg_queue=raw_emg_queue, preprocessed_emg_queue=preprocessed_emg_queue, prosthesis_setpoint_queue=prosthesis_setpoint_queue, stop_event=stop_event)
    # Wait for data processing thread to finish
    processing_thread.join()
    #ser.close()  # Close serial port


if __name__ == "__main__":
    main()