# tests/test_preprocessing.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from emg_preprocessing.preprocessing import preprocess_emg

# shit+alt+A to uncomment
""" def test_preprocess_emg():
    fs = 2000
    t = np.arange(0, 1, 1/fs)
    signal = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 50 * t)
    print("raw signal", signal)
    processed_signal = preprocess_emg(signal, original_rate=fs, target_rate=33.3, lowcut=10.0, order=4, btype='low')
    print("test", processed_signal)
    assert processed_signal is not None
    assert len(processed_signal) > 0

if __name__ == "__main__":
    import pytest
    pytest.main() """


fs = 2000
t = np.arange(0, 1, 1/fs)
signal = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 50 * t)

processed_signal = preprocess_emg(signal, original_rate=fs, target_rate=33.3, highcut=10.0, order=4, btype='low')
print("Processed Signal:", processed_signal)
