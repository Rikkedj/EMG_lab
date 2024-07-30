import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
import time
import config


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
            processed_data = preprocessed_data_queue.get_last()
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
