from collections import deque
import threading
import config
import numpy as np



class ThreadSafeQueue:
    def __init__(self, window_size=10):
        self.queue = deque(maxlen=window_size)  # Use deque for efficient appending and popping
        self.window_size = window_size
        self._sample_num = 0
        self.lock = threading.Lock()  # Lock for thread safety

    def append(self, item):
        with self.lock:
            # here you should check if the data is new and handle if the queue is full
            self.queue.append(item)
            self._sample_num += 1

    def get_last(self):
        """
        Returns the last element of the queue with number of sample safely.
        """
        with self.lock:
            if self.queue:  # Check if the queue is not empty
                return (self._sample_num, self.queue[-1])
            else:
                return None  # or raise an exception, depending on your use case
    
    def get_copy(self):
        """
        Returns a copy of the entire queue with number of sample.
        """
        with self.lock:
            return (self._sample_num, list(self.queue))  # Return a shallow copy of the queue as a list
        
    def is_full(self):
        with self.lock:
            return len(self.queue) >= self.queue.maxlen
    
    def is_empty(self):
        with self.lock:
            return len(self.queue) == 0
    
    def clear(self):
        with self.lock:
            self.queue.clear()

class ThreadSafeState:
    def __init__(self):
        self._state = False
        self._prev_state = False
        self._lock = threading.Lock()

    def set_state(self, state: bool):
        with self._lock:
            self._prev_state = self._state
            self._state = state

    def get_state(self):
        with self._lock:
            return self._state
        
    def get_prev_state(self):
        with self._lock:
            return self._prev_state


#deque(maxlen=N): A bounded deque that restricts the maximum number of elements (N) it can hold. When new items are added and the deque is full, the oldest items are automatically removed to accommodate the new items.
class DataWindow:
    def __init__(self, num_channels, window_size):
        #self.window = np.zeros(maxlen=window_size)
        #self.sensors = deque(maxlen=num_channels)
        self.window = deque(maxlen=window_size)
        self.count = 0
        self.lock = threading.Lock()
        self.condition = threading.Condition()

    def write(self, data):
        with self.condition:
            self.window.append(data)
            self.count += 1
            self.condition.notify_all()


    def read(self, last_count):
        with self.condition:
            while self.count == last_count:
                self.condition.wait()

            return list(self.window)


''' Class for configuration values, so that it can easily be refressed during runtime. '''
class Config:
    def __init__(self):
        self.TCU_IP = config.TCU_IP
        self.COMMAND_PORT = config.COMMAND_PORT
        self.EMG_PORT = config.EMG_PORT
        self.ACC_PORT = config.ACC_PORT
        self.ACTIVE_CHANNELS = config.ACTIVE_CHANNELS
        self.SENSOR_FREQ = config.SENSOR_FREQ
        self.PROCESSING_FREQ = config.PROCESSING_FREQ
        self.RAW_SIGNAL_GAIN = config.RAW_SIGNAL_GAIN
        self.RECTIFIED_SIGNAL_GAIN = config.RECTIFIED_SIGNAL_GAIN
        self.FILTER_LOW_CUTOFF_FREQUENCY = config.FILTER_LOW_CUTOFF_FREQUENCY
        self.FILTER_HIGH_CUTOFF_FREQUENCY = config.FILTER_HIGH_CUTOFF_FREQUENCY
        self.FILTER_ORDER = config.FILTER_ORDER
        self.FILTER_BTYPE = config.FILTER_BTYPE
        self.HAND_DEADBAND_TRESHOLD = config.HAND_DEADBAND_TRESHOLD
        self.WRIST_DEADBAND_TRESHOLD = config.WRIST_DEADBAND_TRESHOLD
        self.HAND_GAIN = config.HAND_GAIN
        self.WRIST_GAIN = config.WRIST_GAIN

    def refresh(self):
        self.TCU_IP = config.TCU_IP
        self.COMMAND_PORT = config.COMMAND_PORT
        self.EMG_PORT = config.EMG_PORT
        self.ACC_PORT = config.ACC_PORT
        #self.ACTIVE_CHANNELS = config.ACTIVE_CHANNELS # No need to refresh this, cant be changed when connection is established
        self.SENSOR_FREQ = config.SENSOR_FREQ
        self.PROCESSING_FREQ = config.PROCESSING_FREQ
        self.RAW_SIGNAL_GAIN = config.RAW_SIGNAL_GAIN
        self.RECTIFIED_SIGNAL_GAIN = config.RECTIFIED_SIGNAL_GAIN
        self.FILTER_LOW_CUTOFF_FREQUENCY = config.FILTER_LOW_CUTOFF_FREQUENCY
        self.FILTER_HIGH_CUTOFF_FREQUENCY = config.FILTER_HIGH_CUTOFF_FREQUENCY
        self.FILTER_ORDER = config.FILTER_ORDER
        self.FILTER_BTYPE = config.FILTER_BTYPE
        self.HAND_DEADBAND_TRESHOLD = config.HAND_DEADBAND_TRESHOLD
        self.WRIST_DEADBAND_TRESHOLD = config.WRIST_DEADBAND_TRESHOLD
        self.HAND_GAIN = config.HAND_GAIN
        self.WRIST_GAIN = config.WRIST_GAIN