from collections import deque
import threading

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
        