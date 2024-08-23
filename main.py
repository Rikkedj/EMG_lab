import sys
import os
import signal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import plots
from emg_signal_processing import emg_in, emg_preprocessing, myoprocessor, to_prosthesis
import config, time, threading
import pytrigno, pyserial
from classes import ThreadSafeState, ThreadSafeQueue
import serial.tools.list_ports
import serial
import matplotlib.animation as animation


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


''' Myoprocessor function proposed solution. '''
def myoprocessor_controll(hand_or_wrist, cocontraction):
    if not preprocessed_emg_queue.is_empty():
        start_controlled = time.process_time_ns()
        sample_index, processed_emg = preprocessed_emg_queue.get_last()  # Get the last preprocessed signal from the queue
        #print('Starting sequential control...', start_controlled)
        hand_controll, wrist_controll = myoprocessor.sequential_control(processed_emg, hand_or_wrist, cocontraction)
        end_controlled = time.process_time_ns()
        #print('Sequential control ended at:', end_controlled)
       # print('Time to control:', end_controlled - start_controlled)
        return hand_controll, wrist_controll
    else:
        return None, None

''' Myoprocessor function proposed solution. '''
def myoprocessor_controll_directly(preprocessed_data, hand_or_wrist, cocontraction):
    if not preprocessed_data is None:
        hand_controll, wrist_controll = myoprocessor.sequential_control(preprocessed_data, hand_or_wrist, cocontraction)

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

    # Initialize connection to serial port
    try:
        SERIAL_PORT = 'COM6'  # Replace 'COM3' with your port
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
                # print('raw_emg_queue:', raw_emg_queue.queue)
                #preprocessed_data = emg_preprocessing.preprocess_raw_data(raw_emg_queue=raw_emg_queue, preprocessed_emg_queue=preprocessed_emg_queue)
                preprocessed_data = emg_preprocessing.preprocess_raw_data_directly(raw_data=raw_data, preprocessed_emg_queue=preprocessed_emg_queue)
                #print('preprocessed_data:', preprocessed_data)
                
                # print('preprocessed_emg_queue:', preprocessed_emg_queue.queue)
                #hand_controll, wrist_controll = myoprocessor_controll(hand_or_wrist, cocontraction)
                hand_controll, wrist_controll = myoprocessor_controll_directly(preprocessed_data, hand_or_wrist, cocontraction)
                #print('hand_controll:', hand_controll)
                #print('wrist_controll:', wrist_controll)
                setpoints = prosthesis_setpoints(hand_controll, wrist_controll)
            #print('prosthesis_setpoint:', setpoints)
            #if ser.is_open:
            #    pyserial.write_to_hand(ser=ser, setpoints=setpoints)
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
   

    #plots.plot_preprocessed_signal(preprocessed_emg_queue, stop_event)
    #plots.plot_prosthesis_setpoints(prosthesis_setpoint_queue, stop_event)

    # Wait for data processing thread to finish
    processing_thread.join()
    #ser.close()  # Close serial port

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