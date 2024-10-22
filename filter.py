'''
Not use for a filter for now, but store here for reference.
'''

from scipy import signal
import numpy as np
from collections import deque

## Got from: https://www.samproell.io/posts/yarppg/yarppg-live-digital-filter/
class LiveFilter:
    """Base class for live filters.
    """
    def process(self, x):
        # do not process NaNs
        if np.isnan(x):
            return x

        return self._process(x)

    def __call__(self, x):
        return self.process(x)

    def _process(self, x):
        raise NotImplementedError("Derived class must implement _process")

class LiveLFilter(LiveFilter):
    def __init__(self, b, a):
        """Initialize live filter based on difference equation.

        Args:
            b (array-like): numerator coefficients obtained from scipy.
            a (array-like): denominator coefficients obtained from scipy.
        """
        self.b = b
        self.a = a
        self._xs = deque([0] * len(b), maxlen=len(b))
        self._ys = deque([0] * (len(a) - 1), maxlen=len(a)-1)

    def _process(self, x):
        """Filter incoming data with standard difference equations.
        """
        self._xs.appendleft(x)
        y = np.dot(self.b, self._xs) - np.dot(self.a[1:], self._ys)
        y = y / self.a[0]
        self._ys.appendleft(y)

        return y

def filtering_iir(raw_sig, order, lowcut, highcut, btype, fs):
   # Create the filter
   # b, a = signal.butter(order, [lowcut, highcut], btype=btype, fs=fs)
    b, a = signal.iirfilter(order, [lowcut, highcut], btype=btype, ftype='butter', fs=fs)
    live_lfilter = LiveLFilter(b, a)
    # simulate live filter - passing values one by one
    for x in raw_sig: print(x)
    y_live_lfilter = [live_lfilter(y) for y in raw_sig]
        
    return y_live_lfilter