import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
import time
import config

    
def plot_all_signals(raw_emg_queue, preprocessed_emg_queue, prosthesis_setpoint_queue, stop_event):
    """
    Plot all signals in real-time.
    """
    plt.ion()  # Enable interactive mode
    # Define the time window size in seconds
    window_raw = int(config.SENSOR_FREQ*raw_emg_queue.window_size)
    window_processed = int(config.PROCESSING_FREQ*preprocessed_emg_queue.window_size)
    window_setpoint = int(config.PROCESSING_FREQ*prosthesis_setpoint_queue.window_size)

    # Raw emg
    fig_raw, ax1 = plt.subplots()
    ax1.set_title("Raw EMG Signal")
    ax1.set_xlabel("Sample Index")
    ax1.set_ylabel("Amplitude")
    ax1.set_xlim(0, window_raw+100)  # Initial x-limits
    ax1.set_ylim(-1, 1)  
    ax1.grid(True)
    lines1 = [ax1.plot([], [], label=f'EMG {i+1}')[0] for i in range(len(config.ACTIVE_CHANNELS))]  # Create a line for each sensor
    ax1.legend(loc='upper right')

    # Preprocessed emg
    fig_pros, ax2 = plt.subplots()
    ax2.set_title("Preprocessed EMG Signal")
    ax2.set_xlabel("Sample Index")
    ax2.set_ylabel("Amplitude")
    ax2.set_xlim(0, window_processed+100)  # Initial x-limits
    ax2.set_ylim(-5, 5)
    ax2.grid(True)
    lines2 = [ax2.plot([], [], label=f'EMG {i+1}')[0] for i in range(len(config.ACTIVE_CHANNELS))]
    ax2.legend(loc='upper right')

    # Setpoints
    fig_setpoint, (ax3, ax4) = plt.subplots(2, 1)
    ax3.set_title("Prosthesis Setpoints")
    #ax3.set_xlabel("Time")
    ax3.set_ylabel("Hand [V]")
    ax3.grid(True)
    #ax4.set_title("Prosthesis Setpoints: Wrist Control")
    ax4.set_xlabel("Time")
    ax4.set_ylabel("Wrist [V]")
    ax4.grid(True)
    
    ax3.set_ylim(-5.5, 5.5)  # Initial y-limits
    ax3.set_xlim(0, 34)  # Initial x-limits
    ax4.set_ylim(-5.5, 5.5) 
    ax4.set_xlim(0, 34)  # Initial x-limits

    line3, = ax3.plot([], [])
    line4, = ax4.plot([], [])

    # Initialize buffer to store data
    raw_data_buffer = np.zeros((len(config.ACTIVE_CHANNELS), int(window_raw)))
    last_sample_raw = 0
    preprocessed_buffer = np.zeros((len(config.ACTIVE_CHANNELS), int(window_processed)))
    setpoint_buffer = np.zeros((2, int(window_setpoint)))  # Assuming 2 prosthesis setpoints (Hand and Wrist)

    current_pos_raw = 0  # Start at position 0
    current_pos_processed = 0
    current_pos_setpoint = 0

    start_time = time.time()
    while not stop_event.is_set():
        if not raw_emg_queue.is_empty():
            #sample_index, raw_data = raw_emg_queue.get_copy()
            sample_index_raw, raw_data = raw_emg_queue.get_last()
            
            if sample_index_raw == last_sample_raw:
                #print('Same sample as last read, skipping...')
                time.sleep(0.01)
                continue
            
            last_sample_raw = sample_index_raw
            raw_data_buffer = np.roll(raw_data_buffer, -len(raw_data[0]), axis=1)  # Shift data to the left
            raw_data_buffer[:, -len(raw_data[0]):] = raw_data  # Append new data to the right
            
            for i, line in enumerate(lines1):
                line.set_xdata(np.arange(current_pos_raw, current_pos_raw + len(raw_data_buffer[i])))
                line.set_ydata(raw_data_buffer[i])

            ax1.relim()
            ax1.autoscale_view() 
            ax1.set_xlim(current_pos_raw, current_pos_raw + window_raw+100)
            fig_raw.canvas.draw()
            fig_raw.canvas.flush_events()
            plt.pause(0.001)
            current_pos_raw = current_pos_raw + len(raw_data[0])
            

        if not preprocessed_emg_queue.is_empty():
            sample_index_pros, preprocessed_data = preprocessed_emg_queue.get_last()
            
            preprocessed_buffer = np.roll(preprocessed_buffer, -len(preprocessed_data[0]), axis=1)  # Shift data to the left
            preprocessed_buffer[:, -len(preprocessed_data[0]):] = preprocessed_data  # Append new data to the right
            
            for i, line in enumerate(lines2):
                line.set_xdata(np.arange(current_pos_processed, current_pos_processed + len(preprocessed_buffer[i])))
                line.set_ydata(preprocessed_buffer[i])
                
            ax2.relim()
            ax2.autoscale_view()
            ax2.set_xlim(current_pos_processed, current_pos_processed + window_processed)
            # Redraw the plot
            fig_pros.canvas.draw()
            fig_pros.canvas.flush_events()
            plt.pause(0.001)
            current_pos_processed = current_pos_processed + len(preprocessed_data[0])

        if not prosthesis_setpoint_queue.is_empty():
            sample_index, setpoints = prosthesis_setpoint_queue.get_last()
            hand_setpoint, wrist_setpoint = setpoints

            setpoint_buffer = np.roll(setpoint_buffer, -len(hand_setpoint), axis=1)  # Shift data to the left
            setpoint_buffer[:, -len(hand_setpoint):] = setpoints
            
            line3.set_xdata(np.arange(current_pos_setpoint, current_pos_setpoint + len(setpoint_buffer[0])))
            line3.set_ydata(setpoint_buffer[0])

            line4.set_xdata(np.arange(current_pos_setpoint, current_pos_setpoint + len(setpoint_buffer[1])))
            line4.set_ydata(setpoint_buffer[1])

            ax3.relim()
            ax3.autoscale_view()
            ax4.relim()
            ax4.autoscale_view()

            ax3.set_xlim(current_pos_setpoint, current_pos_setpoint + window_setpoint)
            ax4.set_xlim(current_pos_setpoint, current_pos_setpoint + window_setpoint)
            fig_setpoint.canvas.draw()
            fig_setpoint.canvas.flush_events()
            current_pos_setpoint = current_pos_setpoint + len(setpoint_buffer[0])
            plt.pause(0.001)


    plt.ioff()  # Disable interactive mode when exiting
    #plt.close(fig_raw, fig_pros, fig_setpoint)

