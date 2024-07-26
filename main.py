import sys
import os
import signal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from emg_myoelectric_signal_processing import preprocess_emg, split_emg_data, apply_gain
from mc_hand_startup import load_emg_data_csv
import config, time, threading, check_trigno, argparse
from collections import deque


stop_event = threading.Event()  # Event to stop threads

# Define a signal handler
def signal_handler(sig, frame):
    print("\nInterrupt received. Stopping threads and exiting...")
    stop_event.set()  # Set the stop event to True
    sys.exit(0)  # Exit the program

NUM_SENSORS = 0 
## INITIALIZE QUEUES
class ThreadSafeQueue:
    def __init__(self, maxlen=1000):
        self.queue = deque(maxlen=maxlen)  # Use deque for efficient appending and popping
        self.lock = threading.Lock()  # Lock for thread safety

    def append(self, item):
        with self.lock:
            self.queue.append(item)

    def get_last(self):
        """
        Returns the last element of the queue safely.
        """
        with self.lock:
            if self.queue:  # Check if the queue is not empty
                return self.queue[-1]
            else:
                return None  # or raise an exception, depending on your use case

    def is_full(self):
        with self.lock:
            return len(self.queue) >= self.queue.maxlen
    
    def is_empty(self):
        with self.lock:
            return len(self.queue) == 0
    
    def clear(self):
        with self.lock:
            self.queue.clear()


# Initialize queues for raw data, processed data, and prosthesis setpoints
raw_emg_queue = ThreadSafeQueue(maxlen=100)
preprocessed_emg_queue = ThreadSafeQueue(maxlen=100)
prosthesis_setpoint_queue = ThreadSafeQueue(maxlen=10)


def collect_data():
    # Should be a while loop when getting real-time data
    global raw_emg_queue
    ### while True:
    #raw_signal = load_emg_data_csv(file_path)
    #while not stop_event.is_set():
    for i in range(2):
        raw_data = check_trigno.check_emg(active_channels=config.ACTIVE_CHANNELS, stop_event=stop_event)
        raw_emg_queue.append(raw_data)
        print(raw_data)
    #time.sleep(1)
    #if raw_emg_queue.is_full():
    #        break

## NOte! For now Im not sure how the data will be collevted. Assuming it collects a block iof datapoints at a timme, so handle one block at a time
def process_data():
    global raw_emg_queue, preprocessed_emg_queue
    while not stop_event.is_set():
        if not raw_emg_queue.is_empty():
            raw_signal = raw_emg_queue.get_last()  # Get the last raw signal from the queue
            raw_signal_gained = apply_gain(raw_signal, config.RAW_SIGNAL_GAIN)
            processed_emg = []
            for raw_emg in split_emg_data(raw_signal_gained):
                processed_emg.append(preprocess_emg(
                    raw_emg,
                    original_rate=config.SENSOR_FREQ,
                    target_rate=config.PROCESSING_FREQ,
                    lowcut=config.FILTER_LOW_CUTOFF_FREQUENCY,
                    highcut=config.FILTER_HIGH_CUTOFF_FREQUENCY,
                    order=config.FILTER_ORDER,
                    btype=config.FILTER_BTYPE
                ))
            preprocessed_emg_queue.append(processed_emg)


def main():
    RAW_SIGNAL_GAIN = 1000  #Change this in lab 1
    
    collect_data()

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