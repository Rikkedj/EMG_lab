import numpy as np

def apply_gain(signal, gain):
    return signal * gain

def saturate(signal, min_value=-5, max_value=5):
    """
    Saturate the signal between min_value and max_value.
    """
    return np.clip(signal, min_value, max_value)

def deadband(signal, threshold):
    """
    Apply deadband to the signal. If the absolute value of the signal
    is less than the threshold, set it to 0.
    """
    return np.where(np.abs(signal) < threshold, 0, signal)

def to_prosthesis(hand_diff_signal, wrist_diff_signal, hand_gain, wrist_gain, threshold):
    """
    Process the hand and wrist difference signals to control the prosthesis.
    
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
    hand_signal = apply_gain(hand_diff_signal, hand_gain)
    wrist_signal = apply_gain(wrist_diff_signal, wrist_gain)
    
    # Saturate signals
    hand_signal = saturate(hand_signal)
    wrist_signal = saturate(wrist_signal)
    
    # Apply deadband
    hand_signal = deadband(hand_signal, threshold)
    wrist_signal = deadband(wrist_signal, threshold)
    
    # Combine signals into an array
    combined_signal = np.array([hand_signal, wrist_signal])
    
    return combined_signal

# Example usage
if __name__ == "__main__":
    # Example input signals
    hand_diff_signal = np.array([0.1, 3, 4, 6, -7, -4, -0.2])
    wrist_diff_signal = np.array([1, 0.5, -3, 2, 5, -5.5, -1])
    
    # Gains and threshold
    hand_gain = 2.0
    wrist_gain = 1.5
    threshold = 0.5
    
    # Process the signals
    combined_signal = to_prosthesis(hand_diff_signal, wrist_diff_signal, hand_gain, wrist_gain, threshold)
    
    # Output the result
    print("Processed signals:", combined_signal)

