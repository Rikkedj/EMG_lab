import sys
import os
import signal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import plots
from emg_myoelectric_signal_processing import emg_in, emg_preprocessing, myoprocessor, to_prosthesis
import config, time, threading
import pytrigno
from classes import ThreadSafeState, ThreadSafeQueue
from niDAQ import write_to_daq

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
raw_emg_queue = ThreadSafeQueue(maxlen=1)
preprocessed_emg_queue = ThreadSafeQueue(maxlen=1)
prosthesis_setpoint_queue = ThreadSafeQueue(maxlen=1)

# Initialize states for hand/wrist control and cocontraction
cocontraction = ThreadSafeState()
hand_or_wrist = ThreadSafeState()


'''
Myoprocessor function proposed solution.'''
def myoprocessor_controll(hand_or_wrist, cocontraction):
    if not preprocessed_emg_queue.is_empty():
        start_controlled = time.process_time_ns()
        processed_emg = preprocessed_emg_queue.get_last()  # Get the last preprocessed signal from the queue
        #print('Starting sequential control...', start_controlled)
        hand_controll, wrist_controll = myoprocessor.sequential_control(processed_emg, hand_or_wrist, cocontraction)
        end_controlled = time.process_time_ns()
        #print('Sequential control ended at:', end_controlled)
       # print('Time to control:', end_controlled - start_controlled)
        return hand_controll, wrist_controll
    else:
        return None, None

def prosthesis_setpoints(hand_controll, wrist_controll):
    if hand_controll is not None and wrist_controll is not None:
        start_prosthesis = time.process_time_ns()
        #print('Starting prosthesis control...', start_prosthesis)
        prosthesis_setpoint = to_prosthesis.prosthesis_signals(hand_controll, wrist_controll)
        prosthesis_setpoint_queue.append(prosthesis_setpoint)
        end_prosthesis = time.process_time_ns()
        #print('Prosthesis control ended at:', end_prosthesis)
        #print('Time to control prosthesis:', end_prosthesis - start_prosthesis)
        return prosthesis_setpoint
    else:
        return None
    




def main():
    # Initialize connection to Trigno EMG
    dev = emg_in.trigno_startup(stop_event=stop_event)

    while not stop_event.is_set():
        raw_data = emg_in.read_raw_data(dev, raw_emg_queue)
        #print("length raw emg queue", len(raw_emg_queue.queue))
        preprocessed_data = emg_preprocessing.preprocess_raw_data(raw_emg_queue, preprocessed_emg_queue)
        #print("lenght processed emg queue", len(preprocessed_emg_queue.queue))    
        #print("preprocessed data", preprocessed_data)
        hand_controll, wrist_controll = myoprocessor_controll(hand_or_wrist, cocontraction)
        setpoints = prosthesis_setpoints(hand_controll, wrist_controll)
        print('prosthesis_setpoint:', setpoints)
        write_to_daq(prosthesis_setpoint_queue)


    emg_in.stop_trigno(dev)

    # Start plotting threads
    #raw_plot_thread = threading.Thread(target=plots.plot_raw_signal, args=(raw_emg_queue, stop_event))
    #preprocessed_plot_thread = threading.Thread(target=plots.plot_preprocessed_signal, args=(preprocessed_emg_queue, stop_event))
    #setpoints_plot_thread = threading.Thread(target=plots.plot_prosthesis_setpoints, args=(prosthesis_setpoint_queue, stop_event))

    #raw_plot_thread.start()
    #preprocessed_plot_thread.start()
    #setpoints_plot_thread.start()
    
    # Define threads for data processing
    '''def data_processing_thread():
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
    '''
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