import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def plot_signals(signal, plot_label = "Signal"):
    """
    Plot the original and processed EMG signals.
    
    Parameters:
    - signal: Signal you want to plot
    - plot_name: Name of the plot
    """
    # Creating time vectors for plotting
    time = np.arange(len(signal))

    # Plot processed signal
    plt.plot(time, signal, color='red', label=plot_label)
    plt.title('Processed EMG Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)

    # Display plots
    plt.tight_layout()
    plt.show()
    
    ## Bedre å gjøre dette i main i guess

def plot_combined_emg_signals(emg_1, emg_2, emg_3, emg_4):
    """
    Plot all EMG sensor signals in the same plot for comparison.

    Args:
        emg_1 (np.ndarray): 2xN array for sensor 1.
        emg_2 (np.ndarray): 2xN array for sensor 2.
        emg_3 (np.ndarray): 2xN array for sensor 3.
        emg_4 (np.ndarray): 2xN array for sensor 4.
    """
    time = np.arange(len(emg_1))
    plt.figure(figsize=(14, 6))
    
    # Plot each sensor's signal on the same plot
    plt.plot(time, emg_1, label='EMG Sensor 1', color='b')
    plt.plot(time, emg_2, label='EMG Sensor 2', color='g')
    plt.plot(time, emg_3, label='EMG Sensor 3', color='r')
    plt.plot(time, emg_4, label='EMG Sensor 4', color='m')
    
    # Add labels, title, legend, and grid
    plt.xlabel('Time [samples]')
    plt.ylabel('Signal Value')
    plt.title('Combined EMG Signals from All Sensors')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def update_plot(frame, data_queue):
    if not data_queue.is_empty():
        data = data_queue.get_last()
        for sensor in data:
            frame.set_xdata(np.arange(len(sensor)))
            frame.set_ydata(data)

def plot_live(fig):
    ani = FuncAnimation(fig, update_plot, blit=True, interval=100)
    plt.show()


