# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import serial
import numpy as np

# Initialize serial communication
def float_to_quantized_byte(value, min_value=-5.0, max_value=5.0):
    """
    Scales a float to a range and converts it to a byte (0-255).
    """
    # Ensure the value is within the specified range
    clipped_value = np.clip(value, min_value, max_value)
    
    # Normalize to 0-255
    normalized = int((clipped_value - min_value) / (max_value - min_value) * 255)
    
    return normalized


def write_to_hand(ser, setpoints):   
    """
    Write setpoints to the hand using serial communication.
    """
    last_setpoint = "hand"
    #if ser.is_open:
    hand_setpoints = setpoints[0]
    wrist_setpoints = setpoints[1]  
    for i in range(len(hand_setpoints)):
        packet = [0x00, 0x00, 0x00, 0x00]  # Initialize packet

        hand_val = hand_setpoints[i]
        wrist_val = wrist_setpoints[i]

        if hand_val != 0 and wrist_val == 0:
            if hand_val > 0:
                hand_val = float_to_quantized_byte(hand_val)
                packet[0] = hand_val # Open with torque = hand_val
            else:
                hand_val = float_to_quantized_byte(hand_val)
                packet[1] = hand_val   # Close with torque = hand_val
        elif hand_val == 0 and wrist_val != 0:
            if wrist_val > 0:   # Turn right with torque = wrist_val
                wrist_val = float_to_quantized_byte(wrist_val)
                packet[2] = wrist_val
            else:
                wrist_val = float_to_quantized_byte(wrist_val)
                packet[3] = wrist_val # Turn left with torque = wrist_val
        elif hand_val == 0 and wrist_val == 0:
            packet = [0x00, 0x00, 0x00, 0x00]
        else:
            print("Both wrist and hand setpoints cannot be non-zero at the same time")
        # Send setpoints to the hand
        packet_bytes = bytearray(packet)
        ser.write(packet_bytes)

        print("Bytes written:", ser.read(1))
    #else:
     #   print("Serial port is not open")

    #ser.close()  # Close serial port



def test_serial_communication(ser):
    """
    Test serial communication by sending a byte to the hand.
    """
    packet = [0xaa, 0x00, 0x00, 0x00]
    packet_byte  = bytearray(packet)
    print("Packet byte:", packet_byte) 
    if ser.is_open:
        ser.write(packet_byte)
        #ser.read(1)
        print("Byte sent to hand", ser.read(1))
    else:
        print("Serial port is not open")

    