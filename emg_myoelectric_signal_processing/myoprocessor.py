import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from classes import ThreadSafeState
from mc_hand_startup import load_emg_data_csv
import time


## Sekvensiell styring (del 3)
HYSTERESIS_THRESHOLD = 3
HYSTERESIS_WIDTH = 1
#test_emg_signal = load_emg_data_csv('./test_data/processed_data_cocontraction.csv')

def hysteresis(signal, prev_state, threshold, width):
    """
    Apply hysteresis to the signal. If the signal is above the threshold, set it to 1. If the signal is below the threshold minus the width, set it to 0. Otherwise, keep the previous value.
    
    Parameters:
    - signal: The preprocessed myosignal from a single sensor. Only one value.
    - prev_state: The previous state of the cocontraction. Boolean value.
    - threshold: The threshold value for the hysteresis.
    - width: The width of the hysteresis.

    Returns:
    - state: The new state of the cocontraction. Boolean value.
    """
    if signal < (threshold-width):
        return False
    else:
        if signal > (threshold+width):
            return True
        else:
            return prev_state



def sequential_control(processed_signal, hand_or_wrist_state, cocontraction_state):
    '''
    Sequential control of the prosthesis using co-contraction. Will either end up with the state "hand_control" or "wrist_control". When the program is in a state, the difference between the myosignals will decide the movement of the prosthesis. 
    It is propotianal control, so the amplitude of the signals will decide the speed of the movement. The sign of the signal will decide the direction of the movement. 
    To go from one state to another the user will have to do a co-contraction over a certain threshold, which mean both the sensors are giving a "high" valued signal. 

    Wanted functionalities:
        - You should never be able to be in both states at the same time.
        - You should be able to go from one state to another by doing a co-contraction.
        - Which values are considered "high" or "low" is given by the hyseresis function, and are dependent on the hysterisis values given in the beginning of the file.

    Parameters:
    - cocontraction_active: Class of prev state and current state. Boolean value that tells if the user is doing a co-contraction. Shoule be True if there is a co-contraction, and False if there is not.
    - hand_or_wrist: The state of the prosthesis. Tells if we are in hand or wrist state with boolean values.
    - processed_signal: The preprocessed myosignals from the sensors.  

    Returns:
    - hand_diff_signal: The difference signal for the hand to be used in the prosthesis control.
    - wrist_diff_signal: The difference signal for the wrist to be used in the prosthesis control.
    '''
    cocontraction_active = cocontraction_state.get_state()
    prev_cocontraction_active = cocontraction_state.get_prev_state()
    
    hand_array = [] 
    wrist_array = []
    for i in range(len(processed_signal[0])):
        signal1 = processed_signal[0][i]
        signal2 = processed_signal[1][i]
        hyst_emg1 = hysteresis(signal=processed_signal[0][i], prev_state=prev_cocontraction_active, threshold=HYSTERESIS_THRESHOLD, width=HYSTERESIS_WIDTH)
        hyst_emg2 = hysteresis(signal=processed_signal[1][i], prev_state=prev_cocontraction_active, threshold=HYSTERESIS_THRESHOLD, width=HYSTERESIS_WIDTH)
        if hyst_emg1 and hyst_emg2:
            cocontraction_active = True
            cocontraction_state.set_state(cocontraction_active)
            print('Cocontraction active')
        else: 
            cocontraction_active = False
            cocontraction_state.set_state(cocontraction_active)
            print('Cocontraction not active')
    
        prev_cocontraction_active = cocontraction_state.get_prev_state()

        if (not prev_cocontraction_active) and cocontraction_active:
            hand_or_wrist_state.set_state(not hand_or_wrist_state.get_state()) # switch state
        
        if hand_or_wrist_state.get_state():
            print("wrist state")
            hand_diff_signal = 0
            wrist_diff_signal = processed_signal[0][i] - processed_signal[1][i]
        else:
            print("hand state")
            hand_diff_signal = processed_signal[0][i] - processed_signal[1][i]
            wrist_diff_signal = 0

        hand_array.append(hand_diff_signal)
        wrist_array.append(wrist_diff_signal)

    # Convert to NumPy arrays
    hand_array = np.array(hand_array, dtype=np.float64)
    wrist_array = np.array(wrist_array, dtype=np.float64)
    return hand_array, wrist_array

def main():
    '''
    start_time = time.process_time()
    print('start time control:', start_time)
    hand, wrist = sequential_control(test_emg_signal, hand_or_wrist, cocontraction)
    end_time = time.process_time()
    print('end time control:', end_time)
    print('time spent in control:', end_time-start_time)
    #print('hand:', hand)
    #print('wrist:', wrist)
    '''

#if __name__ == "__main__":
#    main()