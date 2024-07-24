#### Supposed to be a control signal for a prosthesis #####

## Sekvensiell styring (del 3)
HYSTERESIS_THRESHOLD = 3
HYSTERESIS_WIDTH = 1

def hysteresis(signal, prev_state, threshold, width):
    """
    Apply hysteresis to the signal. If the signal is above the threshold, set it to 1. If the signal is below the threshold minus the width, set it to 0. Otherwise, keep the previous value.
    """
    if signal > threshold:
        return 1
    elif signal < threshold - width:
        return 0
    else:
        return signal

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

def sequential_control(hand_diff, wrist_diff):
    '''
    Sequential control of the prosthesis using co-contraction. Will either end up with the state "hand_control" or "wrist_control". When the program is in a state, the difference between the myosignals will decide the movement of the prosthesis. 
    It is propotianal control, so the amplitude of the signals will decide the speed of the movement. The sign of the signal will decide the direction of the movement. 
    To go from one state to another the user will have to do a co-contraction over a certain threshold, which mean both the sensors are giving a "high" valued signal. 

    Wanted functionalities:
        - You should never be able to be in both states at the same time.
        - You should be able to go from one state to another by doing a co-contraction.
        - Which values are considered "high" or "low" is given by the hyseresis function, and are dependent on the hysterisis values given in the beginning of the file.

    Parameters:
    - cocontraction_active: Boolean value that tells if the user is doing a co-contraction. Shoule be True if there is a co-contraction, and False if there is not.
    - hand_or_wrist: The state of the prosthesis. Tells if we are in hand or wrist state with boolean values.
    - prev_cocontraction_active: The value of cocontraction_active in the previous iteration.
    - prev_hand_or_wrist: The value of hand_or_wrist in the previous iteration.


    
    '''