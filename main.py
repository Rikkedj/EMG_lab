import sys
import os
import signal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from emg_myoelectric_signal_processing import preprocess_emg, apply_gain
import config, time, threading
from collections import deque
import pytrigno

stop_event = threading.Event()  # Event to stop threads

# Define a signal handler
def signal_handler(sig, frame):
    print("\nInterrupt received. Stopping threads and exiting...")
    stop_event.set()  # Set the stop event to True
    sys.exit(0)  # Exit the program

signal.signal(signal.SIGINT, signal_handler)  # Register the signal handler

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
    # Initialize connection to Trigno EMG
    try:
        dev = pytrigno.TrignoEMG(active_channels=config.ACTIVE_CHANNELS, samples_per_read=1000, # Note! Must have samples_per_read at least 1000 for filtfilt to work
                            host='localhost', cmd_port=config.COMMAND_PORT, data_port=config.EMG_PORT, stop_event=stop_event)
        dev.start()

    #while not stop_event.is_set():
        for i in range(10):
            raw_data = dev.read()
            if raw_data is not None:
                raw_emg_queue.append(raw_data)
                #print(raw_data)
            #else:
            #   break  # Exit the loop if reading fails

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
            raw_signal_gained = apply_gain(raw_signal, config.RAW_SIGNAL_GAIN)
            processed_emg = []
            for sensor in raw_signal_gained:
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
        else:
            time.sleep(2)  # Idle loop to wait for data
            print('Waiting for raw data...')
            #break  # Exit the loop if there is no data in the queue



def plot_data():
    fig, ax = plt.subplots()

    # Initialize an empty line for each channel
    lines = []
    for channel in range(len(config.ACTIVE_CHANNELS)):
        line, = ax.plot([], [], label=f'Channel {channel+1}')
        lines.append(line)

    # Set plot parameters
    ax.set_xlim(0, 10)
    ax.set_ylim(-1, 1)
    ax.set_xlabel('Time (samples)')
    ax.set_ylabel('Amplitude')
    ax.legend(loc='upper right')

    # Capture the start time
    start_time = time.time()

    # Animation function
    def animate(i):
        if not preprocessed_emg_queue.is_empty():
            # Get the last preprocessed data
            data = preprocessed_emg_queue.get_last()
            print('data in animate from preprocessed_queue:', data) 
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            num_samples = len(data[0])  # Assuming data shape is (num_channels, num_samples)
            print('num_samples:', num_samples)
            time_vector = np.linspace(elapsed_time - num_samples/config.PROCESSING_FREQ, elapsed_time, num_samples)
            
            # Update each line with new data
            for line, channel_data in zip(lines, data):
                #line.set_data(range(len(channel_data)), channel_data)
                line.set_data(time_vector, channel_data)

            # Adjust x-axis to fit the latest data
            ax.set_xlim(elapsed_time - 10, elapsed_time)  # 10-second rolling window
        
        return lines

    # Set up the animation
    ani = animation.FuncAnimation(fig, animate, blit=True, interval=50, cache_frame_data=False)

    # Display the plot
    plt.show()


def main():
    collector_thread = threading.Thread(target=collect_data, name="DataCollectorThread", daemon=True)
    processor_thread = threading.Thread(target=process_data, name="DataProcessorThread", daemon=True)
    #plotting_thread = threading.Thread(target=plot_data)
    # Start threads
    collector_thread.start()
    processor_thread.start()
    #plotting_thread.start()
    #while not stop_event.is_set():
    plot_data()
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