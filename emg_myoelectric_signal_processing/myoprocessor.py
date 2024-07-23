#### Supposed to be a control signal for a prosthesis #####

def differentiate(signal1, signal2, signal3, signal4):
    """
    Take difference of two signals for each of the functions:
    hand (open/close) and 
    wrist (rotate clockwise / rotate counterclockwise).
    
    Parameters:
    - signal1: The first signal, representing hand.
    - signal2: The second signal, representing hand.
    - signal3: The third signal, representing wrist.
    - signal4: The fourth signal, representing wrist.
    
    Returns:
    - hand_diff_signal: The difference signal for the hand.
    - wrist_diff_signal: The difference signal for the wrist.
    """
    hand_diff_signal = signal1 - signal2
    wrist_diff_signal = signal3 - signal4
    return hand_diff_signal, wrist_diff_signal