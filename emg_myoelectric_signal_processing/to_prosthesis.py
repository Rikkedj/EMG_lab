import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import config

def saturate(signal, min_value=-5, max_value=5):
    """
    Saturate the signal between min_value and max_value.
    """
    if max_value < min_value:
        raise ValueError("max_value must be greater than min_value")
    else:
        return np.clip(signal, min_value, max_value)

def deadband(signal, threshold):
    """
    Apply deadband to the signal. If the absolute value of the signal
    is less than the threshold, set it to 0.
    """
    return np.where(np.abs(signal) < threshold, 0, signal)

## Need to send signal to NI DAQ
# order
# hand_gain and wrist gain 


def prosthesis_signals(hand_diff_signal, wrist_diff_signal):
    """
    Process the hand and wrist difference signals to control the prosthesis. The two signals come from myoprocessor, which is made in lab 3.
    
    Parameters:
    - hand_diff_signal: The difference signal for the hand.
    - wrist_diff_signal: The difference signal for the wrist.
    - hand_gain: The gain to apply to the hand signal.
    - wrist_gain: The gain to apply to the wrist signal.
    - threshold: The deadband threshold.
    
    Returns:
    - combined_signal: The array of processed hand and wrist signals.
    """
    # Apply gain
    hand_signal = hand_diff_signal*config.HAND_GAIN
    wrist_signal = wrist_diff_signal*config.WRIST_GAIN
    
    # Saturate signals
    hand_signal = saturate(hand_signal,-5,5)
    wrist_signal = saturate(wrist_signal,-5,5)
    
    # Apply deadband
    hand_signal = deadband(hand_signal, config.HAND_DEADBAND_TRESHOLD)
    wrist_signal = deadband(wrist_signal, config.WRIST_DEADBAND_TRESHOLD)
    
    # Combine signals into an array
    combined_signal = np.array([hand_signal, wrist_signal])
    
    return combined_signal

