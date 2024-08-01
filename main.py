import sys
import os
import signal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import plots
from emg_myoelectric_signal_processing import preprocess_emg, sequential_control, to_prosthesis
import config, time, threading
import pytrigno
from classes import ThreadSafeState, ThreadSafeQueue

#plt.switch_backend('Qt5Agg')  # Alternative: 
plt.switch_backend('TkAgg')

'''
To handle keyboard interruptions, like ctrl-c, we need a signal handler and an event to be passed to the threads.
'''
stop_event = threading.Event()  # Event to stop threads

def signal_handler(sig, frame):
    print("\nInterrupt received. Stopping threads and exiting...")
    stop_event.set()  # Set the stop event to True
    sys.exit(0)  # Exit the program

signal.signal(signal.SIGINT, signal_handler)  # Register the signal handler


# Initialize queues for raw data, processed data, and prosthesis setpoints
raw_emg_queue = ThreadSafeQueue(maxlen=100)
preprocessed_emg_queue = ThreadSafeQueue(maxlen=100)
prosthesis_setpoint_queue = ThreadSafeQueue(maxlen=10)



cocontraction = ThreadSafeState()
hand_or_wrist = ThreadSafeState()
def trigno_startup():
    try:
        start_conn = time.time()
        print("Connecting to Trigno EMG device...", start_conn)
        dev = pytrigno.TrignoEMG(active_channels=config.ACTIVE_CHANNELS, samples_per_read=1000, # Note! Must have samples_per_read at least 1000 for filtfilt to work
                            host='localhost', cmd_port=config.COMMAND_PORT, data_port=config.EMG_PORT, stop_event=stop_event)
        dev.start()
        end_conn = time.time()
        print("Connected to Trigno EMG device.",end_conn)   
        print("Time used to connect to Trigno EMG device:", end_conn - start_conn)
        return dev
    except IOError as e:
        print("Error reading EMG data:", e)
        return None
    except Exception as e:
        print("Unknown error:", e)
        return None
    
def read_raw_data(dev):
    try:
        start_read = time.time()
        print('Reading EMG data...', start_read)
        raw_data = dev.read()
        raw_data_gained = raw_data*config.RAW_SIGNAL_GAIN
        if raw_data is not None:
            raw_emg_queue.append(raw_data_gained)
            end_append = time.time()
            print('appended data to queue:', end_append)
            print('raw emg: ', raw_data)
            print('time used reading and appending raw data:', end_append - start_read)
        return raw_data
    except IOError as e:
        print("Error reading EMG data:", e)
        return None
    except Exception as e:
        print("Unknown error:", e)
        return None
    
def stop_trigno(dev):
    dev.stop()
    dev.__del__() # Close sockets
    print("EMG data collection stopped.")

def collect_data():
    # Initialize connection to Trigno EMG
    try:
        start_conn = time.time()
        print("Connecting to Trigno EMG device...", start_conn)
        dev = pytrigno.TrignoEMG(active_channels=config.ACTIVE_CHANNELS, samples_per_read=1000, # Note! Must have samples_per_read at least 1000 for filtfilt to work
                            host='localhost', cmd_port=config.COMMAND_PORT, data_port=config.EMG_PORT, stop_event=stop_event)
        dev.start()
        end_conn = time.time()
        print("Connected to Trigno EMG device.",end_conn)   
        print("Time used to connect to Trigno EMG device:", end_conn - start_conn)
        #while not stop_event.is_set():
        #    time.sleep(0.1)  # Idle loop
        for i in range(2):
            start_read = time.time()
            print('Reading EMG data...', start_read)
            raw_data = dev.read()
            raw_data_gained = raw_data*config.RAW_SIGNAL_GAIN
            if raw_data is not None:
                raw_emg_queue.append(raw_data_gained)
                end_append = time.time()
                print('appended data to queue:', end_append)
                print('raw emg: ', raw_data)
                print('time used reading and appending raw data:', end_append - start_read)
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
        
def preprocess_raw_data():
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
        return processed_emg
    else:
        time.sleep(2)
        print('Waiting for raw data...')

def myoprocessor(hand_or_wrist, cocontraction):
    if not preprocessed_emg_queue.is_empty():
        start_controlled = time.process_time_ns()
        processed_emg = preprocessed_emg_queue.get_last()  # Get the last preprocessed signal from the queue
        print('Starting sequential control...', start_controlled)
        hand_controll, wrist_controll = sequential_control(processed_emg, hand_or_wrist, cocontraction)
        end_controlled = time.process_time_ns()
        print('Sequential control ended at:', end_controlled)
        print('Time to control:', end_controlled - start_controlled)
        return hand_controll, wrist_controll
    else:
        return None, None

def prosthesis_setpoints(hand_controll, wrist_controll):
    if hand_controll is not None and wrist_controll is not None:
        start_prosthesis = time.process_time_ns()
        print('Starting prosthesis control...', start_prosthesis)
        prosthesis_setpoint = to_prosthesis(hand_controll, wrist_controll)
        prosthesis_setpoint_queue.append(prosthesis_setpoint)
        end_prosthesis = time.process_time_ns()
        print('Prosthesis control ended at:', end_prosthesis)
        print('Time to control prosthesis:', end_prosthesis - start_prosthesis)
        return prosthesis_setpoint
    else:
        return None
    
def process_data():
    #while not stop_event.is_set():
    #    time.sleep(1)  # Idle loop to wait for data
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
            print('processed emg: ', processed_emg)
            
            start_controlled = time.process_time_ns()
            print('Starting sequential control...', start_controlled)
            hand_controll, wrist_controll = sequential_control(processed_emg, hand_or_wrist, cocontraction)
            print('Hand control:', hand_controll)
            print('Wrist control:', wrist_controll)
            end_controlled = time.process_time_ns()
            print('Sequential control ended at:', end_controlled)
            print('Time to control:', end_controlled - start_controlled)

            start_prosthesis = time.process_time_ns()
            print('Starting prosthesis control...', start_prosthesis)
            prosthesis_setpoint = to_prosthesis(hand_controll, wrist_controll)
            print('Prosthesis setpoint:', prosthesis_setpoint)
            prosthesis_setpoint_queue.append(prosthesis_setpoint)
            end_prosthesis = time.process_time_ns()
            print('Prosthesis control ended at:', end_prosthesis)
            print('Time to control prosthesis:', end_prosthesis - start_prosthesis)

        else:
            time.sleep(2)  # Idle loop to wait for data
            print('Waiting for raw data...')
            #break  # Exit the loop if there is no data in the queue



def main():
    # Initialize connection to Trigno EMG
    dev = trigno_startup()
    
    # Start plotting threads
    #raw_plot_thread = threading.Thread(target=plots.plot_raw_signal, args=(raw_emg_queue, stop_event))
    #preprocessed_plot_thread = threading.Thread(target=plots.plot_preprocessed_signal, args=(preprocessed_emg_queue, stop_event))
    #setpoints_plot_thread = threading.Thread(target=plots.plot_prosthesis_setpoints, args=(prosthesis_setpoint_queue, stop_event))

    #raw_plot_thread.start()
    #preprocessed_plot_thread.start()
    #setpoints_plot_thread.start()
    
    # Define threads for data processing
    def data_processing_thread():
        while not stop_event.is_set():
            try:
                raw_data = read_raw_data(dev)
                print('raw_emg_queue:', raw_emg_queue.queue)
                preprocessed_data = preprocess_raw_data()
                print('preprocessed_emg_queue:', preprocessed_emg_queue.queue)
                hand_controll, wrist_controll = myoprocessor(hand_or_wrist, cocontraction)
                print('hand_controll:', hand_controll)
                print('wrist_controll:', wrist_controll)
                setpoints = prosthesis_setpoints(hand_controll, wrist_controll)
                print('prosthesis_setpoint:', setpoints)

            except Exception as e:
                print("Unknown error:", e)
                stop_event.set()
                break

    # Start data processing thread
    processing_thread = threading.Thread(target=data_processing_thread)
    processing_thread.start()

    # Start plotting in the main thread
    #plots.plot_raw_signal(raw_emg_queue, stop_event)
    #plots.plot_preprocessed_signal(preprocessed_emg_queue, stop_event)
    plots.plot_prosthesis_setpoints(prosthesis_setpoint_queue, stop_event)

    # Wait for data processing thread to finish
    processing_thread.join()

    stop_trigno(dev)
'''
    while not stop_event.is_set():
        try:
            raw_data = read_raw_data(dev)
            print('raw_emg_queue:', raw_emg_queue.queue)
            preprocessed_data = preprocess_raw_data()
            print('preprocessed_emg_queue:', preprocessed_emg_queue.queue)
            hand_controll, wrist_controll = myoprocessor(hand_or_wrist, cocontraction)
            print('hand_controll:', hand_controll)
            print('wrist_controll:', wrist_controll)
            setpoints = prosthesis_setpoints(hand_controll, wrist_controll)
            print('prosthesis_setpoint:', setpoints)

        except KeyboardInterrupt:
            print("\nStopping threads due to keyboard interrupt...")
            stop_event.set()
            break
        except Exception as e:
            print("Unknown error:", e)
            stop_event.set()
            break

    stop_trigno(dev)

    # Wait for plot threads to finish
    #raw_plot_thread.join()
    #preprocessed_plot_thread.join()
    #setpoints_plot_thread.join()

    print("All threads stopped. Exiting program.")

'''

if __name__ == "__main__":
    main()