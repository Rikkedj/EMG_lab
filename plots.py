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
    window_pros = int(config.PROCESSING_FREQ*preprocessed_emg_queue.window_size)
    step_size_raw  = int(config.SENSOR_FREQ)
    step_size_pros = int(config.PROCESSING_FREQ)

    # Raw emg
    fig_raw, ax1 = plt.subplots()
    ax1.set_title("Raw EMG Signal")
    ax1.set_xlabel("Sample Index")
    ax1.set_ylabel("Amplitude")
    ax1.set_ylim(-1, 1)  
    ax1.grid(True)
    lines1 = [ax1.plot([], [], label=f'EMG {i+1}')[0] for i in range(len(config.ACTIVE_CHANNELS))]  # Create a line for each sensor
    ax1.legend(loc='upper right')

    # Preprocessed emg
    fig_pros, ax2 = plt.subplots()
    ax2.set_title("Preprocessed EMG Signal")
    ax2.set_xlabel("Sample Index")
    ax2.set_ylabel("Amplitude")
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
    preprocessed_buffer = np.zeros((len(config.ACTIVE_CHANNELS), int(window_pros)))
    setpoint_buffer = np.zeros((2, int(window_pros)))  # Assuming 2 prosthesis setpoints (Hand and Wrist)
    start_time = time.process_time()
    
    current_pos_raw = 0  # Start at position 0
    current_pos_pros = 0

    while not stop_event.is_set():
        if not raw_emg_queue.is_empty():
            #sample_index, raw_data = raw_emg_queue.get_copy()
            sample_index_raw, raw_data = raw_emg_queue.get_last()
            
            if sample_index_raw == last_sample_raw:
                print('Same sample as last read, skipping...')
                continue
            last_sample_raw = sample_index_raw
            
            
            #for dataset in raw_data:
            if current_pos_raw + step_size_raw <= window_raw:
                raw_data_buffer[:, current_pos_raw:current_pos_raw+step_size_raw] = raw_data
                current_pos_raw += step_size_raw
            else:
                shift_amount = current_pos_raw + step_size_raw - window_raw
                raw_data_buffer = np.roll(raw_data_buffer, -shift_amount, axis=1)
                raw_data_buffer[:, -step_size_raw:] = raw_data
                current_pos_raw = current_pos_raw + step_size_raw

            for i, line in enumerate(lines1):
                # Update x and y data directly from the queue
                line.set_xdata(np.arange(current_pos_raw-step_size_raw, current_pos_raw-step_size_raw+window_raw))
                line.set_ydata(raw_data_buffer[i])

            # Autoscale the x-axis only
            ax1.relim()
            ax1.autoscale_view()  

            # Redraw the plot
            fig_raw.canvas.draw()
            fig_raw.canvas.flush_events()

            plt.pause(0.001)  # Small delay for the plot update


        if not preprocessed_emg_queue.is_empty():
            sample_index_pros, preprocessed_data = preprocessed_emg_queue.get_last()
            
            if current_pos_pros + step_size_pros <= window_pros:
                preprocessed_buffer[:, current_pos_pros:current_pos_pros+step_size_pros] = preprocessed_data
                current_pos_pros += step_size_pros
            else:
                shift_amount_pros = current_pos_pros + step_size_pros - window_pros
                preprocessed_buffer = np.roll(preprocessed_buffer, -shift_amount_pros, axis=1)
                preprocessed_buffer[:, -step_size_pros:] = preprocessed_data
                current_pos_pros += step_size_pros

            for i, line in enumerate(lines2):
                #line.set_data(np.arange(preprocessed_data.shape[1]), preprocessed_data[i, :])
                #num_samples = preprocessed_buffer[i].shape[0]  # Number of samples for channel i
                #line.set_data(np.arange(num_samples), preprocessed_data[i])
                line.set_xdata(np.arange(current_pos_pros-step_size_pros, current_pos_pros-step_size_pros+window_pros))
                line.set_ydata(preprocessed_buffer[i])
                
            ax2.relim()
            ax2.autoscale_view()
            # Redraw the plot
            fig_pros.canvas.draw()
            fig_pros.canvas.flush_events()

            plt.pause(0.001)
            #plt.draw()

        if not prosthesis_setpoint_queue.is_empty():
            sample_index, setpoints = prosthesis_setpoint_queue.get_last()
            hand_setpoint, wrist_setpoint = setpoints

            line3.set_data(np.arange(len(hand_setpoint)), hand_setpoint)
            line4.set_data(np.arange(len(wrist_setpoint)), wrist_setpoint)

            ax3.relim()
            ax3.autoscale_view()
            ax4.relim()
            ax4.autoscale_view()

            plt.pause(0.01)
            plt.draw()

    plt.ioff()  # Disable interactive mode when exiting
    plt.close(fig_raw, fig_pros, fig_setpoint)



'''
def real_time_plot(raw_data_queue, processed_data_queue, setpoint_queue):
    """Plots data in real-time."""
    # Create a figure and axis
    plt.ion()  # Enable interactive mode
    # Define the time window size in seconds
    window_raw = int(config.SENSOR_FREQ*raw_emg_queue.window_size)
    window_pros = int(config.PROCESSING_FREQ*preprocessed_emg_queue.window_size)
    step_size_raw  = int(config.SENSOR_FREQ)
    step_size_pros = int(config.PROCESSING_FREQ)

    # Raw emg
    fig_raw, ax1 = plt.subplots()
    ax1.set_title("Raw EMG Signal")
    ax1.set_xlabel("Sample Index")
    ax1.set_ylabel("Amplitude")
    ax1.grid(True)
    lines1 = [ax1.plot([], [], label=f'EMG {i+1}')[0] for i in range(len(config.ACTIVE_CHANNELS))]  # Create a line for each sensor
    ax1.legend(loc='upper right')

    
    fig_pros, ax2 = plt.subplots()
    ax2.set_title("Preprocessed EMG Signal")
    ax2.set_xlabel("Sample Index")
    ax2.set_ylabel("Amplitude")
    ax2.grid(True)
    lines2 = [ax2.plot([], [], label=f'EMG {i+1}')[0] for i in range(len(config.ACTIVE_CHANNELS))]
    ax2.legend(loc='upper right')

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

    # Initialize empty data lists
    raw_data_list = []
    processed_data_list = []
    setpoint_list = []
    x_data = []

    # Initialize plot lines
    raw_line, = ax1.plot([], [], label='Raw Data')
    processed_line, = ax2.plot([], [], label='Processed Data')
    setpoint_line, = ax3.plot([], [], label='Setpoint')

    def init():
        ax1.set_xlim(0, 2000)  
        ax1.set_ylim(0, 2)    # Example y-axis limits
        ax2.set_xlim(0, 34)  
        ax2.set_ylim(-1, 10)    # Example y-axis limits
        ax3.set_xlim(0, 34)
        ax3.set_ylim(-5,5)  
        return raw_line, processed_line, setpoint_line

    def update(frame):
        # Pull all available data from the queue
        while not raw_data_queue.empty():
            sample_num, raw_data = raw_data_queue.get_copy()
            raw_data_list.append(raw_data)
            x_data.append(len(x_data))

        # Update the data in the plot
        raw_line.set_data(x_data, raw_data_list)
        processed_line.set_data(x_data, processed_data_list)
        setpoint_line.set_data(x_data, setpoint_list)

        # Adjust the x-axis to show the last 100 data points
        if len(x_data) > 100:
            ax.set_xlim(len(x_data) - 100, len(x_data))

        return raw_line, processed_line, setpoint_line

    ani = animation.FuncAnimation(fig, update, init_func=init, interval=100, blit=True)
    plt.legend()
    plt.show()
'''

'''


def plot_data(raw_data_queue=[], preprocessed_data_queue=[], setpoint_queue=[]):
# General plot function with subplots
    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle('EMG Signals', fontsize=16)

    subtitles = ["Raw EMG Data", "Processed EMG Data", "Setpoint Prosthesis"]
    for ax, subtitle in zip(axs, subtitles):
        ax.set_title(subtitle, fontsize=12)  # Use pad for spacing between title and plot

    # Initialize an empty line for each channel and each subplot
    all_lines = {'raw': [], 'processed': [], 'other': []}

    # Create lines for each type of data in a single loop
    for channel in range(len(config.ACTIVE_CHANNELS)):
        line_raw, = axs[0].plot([], [], label=f'EMG {channel+1}')
        line_processed, = axs[1].plot([], [])
        line_other, = axs[2].plot([], [])
        
        all_lines['raw'].append(line_raw)
        all_lines['processed'].append(line_processed)
        all_lines['other'].append(line_other)

    # Set plot parameters for each subplot
    axs[0].set_xlim(0, 10)  # Initial x-limits
    axs[0].set_ylim(-1, 1)  # Initial y-limits for raw data
    axs[0].set_ylabel('Signal Value', fontsize=8)
    axs[0].legend(loc='upper right', fontsize='small', ncol=2)
    axs[0].grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
    axs[0].set_facecolor('lightyellow')

    axs[1].set_ylim(-1, 1)  # Initial y-limits for processed data
    axs[1].set_ylabel('Conditioned EMG', fontsize=8)
    #axs[1].legend(loc='upper right', fontsize='small', ncol=2)
    axs[1].grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
    axs[1].set_facecolor('lightblue')

    axs[2].set_ylim(-5, 5)  # Initial y-limits for other data
    axs[2].set_xlabel('Time (seconds)', fontsize=12)
    axs[2].set_ylabel('Hand [V]', fontsize=8)
    #axs[2].legend(loc='upper right', fontsize='small', ncol=2)
    axs[2].grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
    axs[2].set_facecolor('lightgreen')

    # Customize tick parameters
    for ax in axs:
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.2f}'))
        ax.xaxis.set_major_locator(plt.MaxNLocator(10))

    # Initialize variables to capture the initial time and y-limits
    start_time = time.time()
    #smooth_y_min, smooth_y_max = -1, 1

    # Smoothing factor for y-axis (lower is smoother)
    #smoothing_factor = 0.1
    # Animation function
    def animate(i):
        #nonlocal smooth_y_min, smooth_y_max

        # Handle raw data plot
        if not raw_data_queue.is_empty():
            raw_data = raw_data_queue.get_last()
            num_samples = len(raw_data[0])
            time_vector = np.linspace(0, num_samples / config.SENSOR_FREQ, num_samples)
            print('raw data in plot:', raw_data)
            for line, channel_data in zip(all_lines['raw'], raw_data):
                line.set_data(time_vector, channel_data)

            # Adjust x-axis to fit the latest data
            elapsed_time = time.time() - start_time
            axs[0].set_xlim(elapsed_time - 10, elapsed_time)  # 10-second rolling window

            # Calculate new y-limits for raw data
            all_data = np.concatenate(raw_data)
            y_min, y_max = np.min(all_data), np.max(all_data)

            # Apply smoothing to y-limits
            #smooth_y_min = smooth_y_min * (1 - smoothing_factor) + y_min * smoothing_factor
            #mooth_y_max = smooth_y_max * (1 - smoothing_factor) + y_max * smoothing_factor

            # Set the smoothed y-limits
            #axs[0].set_ylim(smooth_y_min - 0.1 * abs(smooth_y_min), smooth_y_max + 0.1 * abs(smooth_y_max))
            axs[0].set_ylim(y_min - 0.1 * abs(y_min), y_max + 0.1 * abs(y_max))  # Add a margin of 10% to the limits

        # Handle processed data plot
        if not preprocessed_data_queue.is_empty():
            sample_index, processed_data = preprocessed_data_queue.get_last()
            num_samples = len(processed_data[0])
            time_vector = np.linspace(0, num_samples / config.PROCESSING_FREQ, num_samples)
            print('processed data in plot:', processed_data)

            for line, channel_data in zip(all_lines['processed'], processed_data):
                line.set_data(time_vector, channel_data)

            # Calculate new y-limits for processed data
            all_data = np.concatenate(processed_data)
            y_min, y_max = np.min(all_data), np.max(all_data)

            # Apply smoothing to y-limits
            #smooth_y_min = smooth_y_min * (1 - smoothing_factor) + y_min * smoothing_factor
            #smooth_y_max = smooth_y_max * (1 - smoothing_factor) + y_max * smoothing_factor

            # Set the smoothed y-limits
            #axs[1].set_ylim(smooth_y_min - 0.1 * abs(smooth_y_min), smooth_y_max + 0.1 * abs(smooth_y_max))
            axs[1].set_ylim(y_min - 0.1 * abs(y_min), y_max + 0.1 * abs(y_max))  # Add a margin of 10% to the limits

        # Handle other data plot
        if not setpoint_queue.is_empty():
            other_data = setpoint_queue.get_last()
            num_samples = len(other_data[0])
            time_vector = np.linspace(0, num_samples / config.SENSOR_FREQ, num_samples)
            
            for line, channel_data in zip(all_lines['other'], other_data):
                line.set_data(time_vector, channel_data)

            # Calculate new y-limits for other data
            all_data = np.concatenate(other_data)
            y_min, y_max = np.min(all_data), np.max(all_data)

            # Apply smoothing to y-limits
            #smooth_y_min = smooth_y_min * (1 - smoothing_factor) + y_min * smoothing_factor
            #smooth_y_max = smooth_y_max * (1 - smoothing_factor) + y_max * smoothing_factor

            # Set the smoothed y-limits
            #axs[2].set_ylim(smooth_y_min - 0.1 * abs(smooth_y_min), smooth_y_max + 0.1 * abs(smooth_y_max))
            axs[2].set_ylim(y_min - 0.1 * abs(y_min), y_max + 0.1 * abs(y_max))  # Add a margin of 10% to the limits
        
        # Return the updated lines as a list
        return [line for lines in all_lines.values() for line in lines]


    ani = animation.FuncAnimation(fig, animate, interval=50, cache_frame_data=False, blit=True)
    plt.show()



def plot_raw_signal(raw_emg_queue, stop_event):
    """
    Plot raw EMG signal in real-time.
    """
    start_time = time.time()
    plt.ion()  # Enable interactive mode
    fig, ax = plt.subplots()
    fig.suptitle('Raw EMG Signals', fontsize=16)
    ax.set_xlim(0, 10) # Initial limits
    ax.set_ylim(-1, 1)
    ax.set_title("Raw EMG Signal")
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Amplitude")
    ax.legend(loc='upper right')
    ax.grid(True)   
    lines = [ax.plot([], [])[0] for i in range(len(config.ACTIVE_CHANNELS))]  # Create a line for each sensor

    # Animation function
    def animate(i):
        if not raw_emg_queue.is_empty():
            # Get the last preprocessed data
            data = raw_emg_queue.get_last()
            print('data in animate from raw_emg_queue:', data) 
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            print('elapsed_time:', elapsed_time)
            num_samples = len(data[0])  # Assuming data shape is (num_channels, num_samples)
            print('num_samples:', num_samples)
            #time_vector = np.linspace(elapsed_time - num_samples/config.PROCESSING_FREQ, elapsed_time, num_samples)
            time_vector = np.linspace(0, num_samples / config.PROCESSING_FREQ, num_samples)
            print('time_vector:', time_vector)
            
            # Update each line with new data
            for line, channel_data in zip(lines, data):
                #line.set_data(range(len(channel_data)), channel_data)
                line.set_data(time_vector, channel_data)
                
            # Adjust x-axis to fit the latest data
            ax.set_xlim(elapsed_time - 10, elapsed_time)  # 10-second rolling window
            y_min, y_max = np.min(data), np.max(data)
            ax.set_ylim(y_min - 0.1 * abs(y_min), y_max + 0.1 * abs(y_max))  # Add a margin of 10% to the limits

        return lines

    # Set up the animation
    ani = animation.FuncAnimation(fig, animate, blit=True, interval=50, cache_frame_data=False)
    
    plt.ioff()  # Disable interactive mode when exiting
    plt.close(fig)

def plot_preprocessed_signal(preprocessed_emg_queue, stop_event):
    """
    Plot preprocessed EMG signal in real-time.
    """
    start_time = time.time()
    plt.ion()  # Enable interactive mode
    fig, ax = plt.subplots()
    fig.suptitle('Preprocessed EMG Signals', fontsize=16)
    ax.set_xlim(0, 10) # Initial limits
    ax.set_ylim(-1, 1)
    ax.set_title("Preprocessed EMG Signal")
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Amplitude")
    ax.legend(loc='upper right')
    ax.grid(True)   
    lines = [ax.plot([], [])[0] for i in range(len(config.ACTIVE_CHANNELS))]  # Create a line for each sensor

    # Animation function
    def animate(i):
        if not preprocessed_emg_queue.is_empty():
            # Get the last preprocessed data
            data = preprocessed_emg_queue.get_last()
            #print('data in animate from raw_emg_queue:', data) 
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            #print('elapsed_time:', elapsed_time)
            num_samples = len(data[0])  # Assuming data shape is (num_channels, num_samples)
            #print('num_samples:', num_samples)
            #time_vector = np.linspace(elapsed_time - num_samples/config.PROCESSING_FREQ, elapsed_time, num_samples)
            time_vector = np.linspace(0, num_samples / config.PROCESSING_FREQ, num_samples)
            #print('time_vector:', time_vector)
            
            # Update each line with new data
            for line, channel_data in zip(lines, data):
                #line.set_data(range(len(channel_data)), channel_data)
                line.set_data(time_vector, channel_data)
                
            # Adjust x-axis to fit the latest data
            ax.set_xlim(elapsed_time - 10, elapsed_time)  # 10-second rolling window
            y_min, y_max = np.min(data), np.max(data)
            ax.set_ylim(y_min - 0.1 * abs(y_min), y_max + 0.1 * abs(y_max))  # Add a margin of 10% to the limits

        return lines

    # Set up the animation
    ani = animation.FuncAnimation(fig, animate, blit=True, interval=50, cache_frame_data=False)
    
    plt.ioff()  # Disable interactive mode when exiting
    plt.close(fig)


def plot_prosthesis_setpoints(prosthesis_setpoint_queue, stop_event):
    """
    Plot prosthesis setpoints for hand and wrist control in real-time.
    """
    plt.ion()
    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1.set_title("Prosthesis Setpoints: Hand Control")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Amplitude")
    ax2.set_title("Prosthesis Setpoints: Wrist Control")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Amplitude")

    line1, = ax1.plot([], [])
    line2, = ax2.plot([], [])

    while not stop_event.is_set():
        if not prosthesis_setpoint_queue.is_empty():
            setpoints = prosthesis_setpoint_queue.get_last()
            hand_setpoint, wrist_setpoint = setpoints

            line1.set_data(np.arange(len(hand_setpoint)), hand_setpoint)
            line2.set_data(np.arange(len(wrist_setpoint)), wrist_setpoint)

            ax1.relim()
            ax1.autoscale_view()
            ax2.relim()
            ax2.autoscale_view()

            plt.pause(0.01)
            plt.draw()

    plt.ioff()
    plt.close(fig)
'''
