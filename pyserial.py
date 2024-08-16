# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import serial

# Initialize serial communication
SERIAL_PORT = 'COM3'  # Replace 'COM3' with your port
ser = serial.Serial(SERIAL_PORT, baudrate=9600, timeout=1)  # Open serial port
