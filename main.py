import sys
import os
import signal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
from plots import plot_data
from emg_myoelectric_signal_processing import preprocess_emg, sequential_control, ThreadSafeQueue, CoContractionState
import config, time, threading
import pytrigno

stop_event = threading.Event()  # Event to stop threads

# Define a signal handler to handle interupts
def signal_handler(sig, frame):
    print("\nInterrupt received. Stopping threads and exiting...")
    stop_event.set()  # Set the stop event to True
    sys.exit(0)  # Exit the program

signal.signal(signal.SIGINT, signal_handler)  # Register the signal handler


# Initialize queues for raw data, processed data, and prosthesis setpoints
raw_emg_queue = ThreadSafeQueue(maxlen=100)
preprocessed_emg_queue = ThreadSafeQueue(maxlen=100)
prosthesis_setpoint_queue = ThreadSafeQueue(maxlen=10)


def collect_data():
    # Initialize connection to Trigno EMG
    try:
        dev = pytrigno.TrignoEMG(active_channels=config.ACTIVE_CHANNELS, samples_per_read=1000, # Note! Must have samples_per_read at least 1000 for filtfilt to work
                            host='localhost', cmd_port=config.COMMAND_PORT, data_port=config.EMG_PORT, stop_event=stop_event)
        dev.start()

        while not stop_event.is_set():
            time.sleep(0.1)  # Idle loop
            raw_data = dev.read()
            raw_data_gained = raw_data*config.RAW_SIGNAL_GAIN
            if raw_data is not None:
                raw_emg_queue.append(raw_data_gained)
                #print('raw emg: ', raw_data)
            else:
               break  # Exit the loop if reading fails

    except IOError as e:
        print("Error reading EMG data:", e)
        #break
    except Exception as e:
        print("Unknown error:", e)
        #break

    #if raw_emg_queue.is_full():
      #  break
    finally:
        dev.stop()
        dev.__del__() # Close sockets
        print("EMG data collection stopped.")
        

def process_data():
    while not stop_event.is_set():
        time.sleep(1)  # Idle loop to wait for data
        if not raw_emg_queue.is_empty():
            raw_signal = raw_emg_queue.get_last()  # Get the last raw signal from the queue
            processed_emg = []
            for sensor in raw_signal:
                processed_emg.append(preprocess_emg( # Filter, rectify, and downsample the raw signal
                    sensor,
                    original_rate=config.SENSOR_FREQ,
                    target_rate=config.PROCESSING_FREQ,
                    lowcut=config.FILTER_LOW_CUTOFF_FREQUENCY,
                    highcut=config.FILTER_HIGH_CUTOFF_FREQUENCY,
                    order=config.FILTER_ORDER,
                    btype=config.FILTER_BTYPE
                ))
            preprocessed_emg_queue.append(processed_emg) # Add an array of the preprocessed data to all the sensors to the queue
            sequential_control

            #print('processed emg: ', processed_emg)
        else:
            time.sleep(2)  # Idle loop to wait for data
            print('Waiting for raw data...')
            #break  # Exit the loop if there is no data in the queue



def main():
    collector_thread = threading.Thread(target=collect_data, name="DataCollectorThread", daemon=True)
    processor_thread = threading.Thread(target=process_data, name="DataProcessorThread", daemon=True)
    #plotting_thread = threading.Thread(target=plot_data)
    # Start threads
    collector_thread.start()
    processor_thread.start()
    #plotting_thread.start()
    #while not stop_event.is_set():
    plot_data(raw_data_queue=raw_emg_queue, preprocessed_data_queue=preprocessed_emg_queue, setpoint_queue=prosthesis_setpoint_queue)
    # Wait for threads to finish
    collector_thread.join()
    processor_thread.join()
    #plotting_thread.join()
    #collect_data()
    #process_data()

    print("Threads stopped. Program exiting cleanly.")
    print('raw_emg_queue:', raw_emg_queue.queue)
    #print('Lenght of last element in raw_emg_queue:', len(raw_emg_queue.get_last()[0]))
    print('preprocessed_emg_queue:', preprocessed_emg_queue.queue)
    # Register the signal handler
    #signal.signal(signal.SIGINT, signal_handler)

    ## INITIALIZE THREADS
    #collect_data_thread = threading.Thread(target=collect_data, args=(), daemon=True)
    #preprocess_data_thread = threading.Thread(target=process_data, args=(), daemon=True)
    # Start threads
    #collect_data_thread.start()
    #preprocess_data_thread.start() 

'''
    try:
        # Main thread logic if needed
        while not stop_event.is_set():
            time.sleep(0.1)  # Idle loop to wait for interrupt
    except KeyboardInterrupt:
        print("\nStopping threads due to keyboard interrupt...")
        stop_event.set()  # Set stop event to stop threads

    # Join threads to ensure clean exit
    collect_data_thread.join()
    #preprocess_data_thread.join()

    print("All threads stopped. Exiting program.") 
'''

if __name__ == "__main__":
    main()