import multiprocessing.process
import sys
import os
import math
import socket
import multiprocessing
from multiprocessing import Manager
import threading
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.style as mplstyle
import time, threading
import struct
import serial
import numpy as np
import select
import feature_extraction as fe
from scipy.signal import butter, filtfilt
import test

#mplstyle.use(['fast'])
plt.switch_backend('TkAgg')

class Trigno:
    def __init__(self):
        try:
            self.cmd = socket.create_connection(('localhost', 50040), 60)
            #self.cmd.recv(1024)  # Initially reading a small packet to clear buffer
            #def ctrl_c_handler(sig, frame):
            #    cmd.sendall(bytes("{}".format("STOP\r\n\r\n"), encoding='ascii'))
            #    print("exiting...")
            #    sys.exit(0)
            #signal.signal(signal.SIGINT, ctrl_c_handler)

            #self.cmd.sendall(bytes("{}{}".format('START\r\n\r\n'), encoding='ascii'))
            self.cmd.sendall(bytes('START\r\n\r\n', encoding='ascii'))
           # resp = self.cmd.recv(128)
           # self._validate(resp)

            print("creating connection with Delsys Trigno: ", self.cmd.recv(1024))

            # reading active sensors - this just crashes the trigno control utility...?
            #for i in range(0,16):
            #    self.cmd.sendall(bytes("SENSOR {} ACTIVE?\r\n\r\n".format(i), encoding='ascii'))
            #    print("Sensor {} active: ".format(i), self.cmd.recv(1024))
            
            self.data = socket.create_connection(('localhost', 50043), 60) # 60 = timeout
            print("creating data connection with Delsys Trigno: ")
  
            self.data.setblocking(True)
            #self.data.settimeout(10)

            self.prev_read_time = None
            self._start = time.time()

        except socket.error as e:
            print(f"Error initializing sockets: {e}")
            raise e
    
    # def read(self, interval):
    #     '''
    #     Trigno control utility sends data over TCP at some iffy rate. It's supposed to be 2kHz, but it's all over the place!
    #     '''
    #     # At startup, we need to set the first read time
    #     if self.prev_read_time == None:
    #         self.prev_read_time = time.time()
        
    #     # Sleep until it's time for the next read
    #     time.sleep(max(self.prev_read_time - time.time() + interval, 0))
    #     self.prev_read_time += interval
        
    #     # Use select to check if data is available on the socket
    #     ready_to_read, _, _ = select.select([self.data], [], [], 1)  # 1 second timeout
        
    #     l_des = math.ceil(interval * 2000) * 4 * 16  # Adjust packet size: 4 bytes per float, 16 channels
    #     packet = b''  # Initialize packet as bytes
    #     total_received = 0
        
    #     # Read data until we have the desired packet size
    #     while total_received < l_des:
    #         try:
    #             chunk = self.data.recv(l_des - total_received)
    #             if not chunk:
    #                 # If no data is received, fill with zeros to match the expected packet size
    #                 packet += b'\x00' * (l_des - total_received)
    #                 break
    #             packet += chunk
    #             total_received += len(chunk)
    #         except socket.timeout:
    #             # Handle socket timeout, padding the remaining bytes with zeros
    #             packet += b'\x00' * (l_des - total_received)
    #             raise IOError("Device disconnected or timed out.")
        
    #     # Ensure the packet size matches the expected length before unpacking
    #     if len(packet) < l_des:
    #         # Fill with zeros if the packet is shorter than expected
    #         packet += b'\x00' * (l_des - len(packet))
        
    #     try:
    #         # Unpack the packet to extract the data
    #         data = np.asarray(struct.unpack('<' + 'f' * (l_des // 4), packet))
    #         data = np.transpose(data.reshape((-1, 16)))  # Reshape based on 16 channels
    #     except struct.error as e:
    #         raise ValueError(f"Error unpacking data: {e}")
        
    #     return data

    def read(self, interval):
        '''
        Trigno control utility sends data over TCP at some iffy rate. It's supposed to be 2kHz, but it's all over the place!
        With interval = 1 (read data once a second), the buffer is filled with 1997 samples (approx as expected)
        With interval = 1/20, we get either 107 or 80 samples, alternating in a ratio of about 4:1
        With interval = 1/50 we get a consistent 26 samples
        Any faster than this, we also get 26 samples every time.
        Even at 4kHz read rate, we get 26 samples in the buffer each time. The expectation is that it would block, because 
        there is no data to read... The same happens in nonblocking or with timeout = 0

        '''
        # At startup, we need to set the first read time
        if self.prev_read_time == None:
            self.prev_read_time = time.time()
        #sleep until time >= self.t + interval_ms
        time.sleep(max(self.prev_read_time - time.time() + interval, 0))
        self.prev_read_time += interval
        
        #ready_to_read, _, _ = select.select([self.data], [], [], 1)  # 1 second timeout
        #d = self.data.recv(4*16*math.ceil(interval*2000*80)) # at most: 4 bytes per 16 channels, at 2000hz * safety factor
        #if self.data in ready_to_read:
        # l_des = math.ceil(interval*2000*80)*4*16
        # l = 0
        # packet = bytes()
        # while l < l_des:
        #     try:
        #         packet += self.data.recv(l_des - l)
        #     except socket.timeout:
        #         l = len(packet)
        #         packet += b'\x00' * (l_des - l)
        #         raise IOError("Device disconnected.")
        #     l = len(packet)

        # data = np.asarray(struct.unpack('<'+'f'*4*16*math.ceil(interval*2000*80), packet))
        # data = np.transpose(data.reshape((-1, 16)))
        
        # return data
        
        d = self.data.recv(4*16*math.ceil(interval*2000*80)) 
        print("read time: ", "{:07.2f}".format((self.prev_read_time-self._start)*1000), " ", len(d))


        last_valid_block_idx = 0
        num_blocks = int(len(d)/64)
        for block_idx in range(0, num_blocks):
            block = d[block_idx*64 : (block_idx+1)*64]
            block_valid = any(block)
            if block_valid:
                last_valid_block_idx = block_idx
            #print(block_idx, block_valid, block)

            vs = struct.unpack('<'+'f'*16, d[last_valid_block_idx*64 : (last_valid_block_idx+1)*64])
            #print("{:07.2f}".format((self.prev_read_time-self._start)*1000), len(d), last_valid_block_idx, vs)
        return vs
        
    @staticmethod
    def _validate(response):
        s = str(response)
        if 'OK' not in s:
            print("warning: TrignoDaq command failed: {}".format(s))


class Thread_Safe_Buffer:
    def __init__(self, length, width=16):
        self.buf = np.zeros((length, width))
        self.length = length
        self.lock = threading.Lock()

    def push(self, value):
        with(self.lock):
            for i in range (self.length-1,0,-1):
                self.buf[i,:] = self.buf[i-1,:] # Shift all rows down, so that new data can be inserted at the top
            #self.buf[0:value.shape[1],:] = value.T
            self.buf[0,:] = value
    def push_filtered(self, value):
        with(self.lock):
            self.buf = value


    # def push(self, value):
    #     """
    #     Push a 16 x n array into the buffer.
    #     If the buffer is full, the oldest data will be discarded.
    #     """
    #     with self.lock:
    #         n = value.shape[1]  # Get the number of samples in the incoming array

    #         # Check if incoming data has the correct shape
    #         if value.shape[0] != 16:
    #             raise ValueError("Input array must have shape (16, n)")

    #         # Determine how many rows we can shift down
    #         rows_to_shift = min(self.length - n, self.length)

    #         # Shift existing data to make room for new samples
    #         if rows_to_shift > 0:
    #             self.buf[rows_to_shift:, :] = self.buf[:self.length - rows_to_shift, :]
    #         else:
    #             # If we are adding more data than the buffer can hold
    #             self.buf = np.zeros((self.length, 16))  # Reset buffer if necessary

    #         # Insert the new data at the top of the buffer
    #         self.buf[:n, :] = value.T  # Transpose to match the buffer shape

    def copy(self):
        with(self.lock):
            return np.copy(self.buf)

class Multiprocess_Safe_Buffer:
    def __init__(self, length):
        self.length = length
        self.manager = Manager()
        self.buf = self.manager.list([np.zeros(16) for _ in range(length)])  # Use Manager().list() for shared access
        self.lock = multiprocessing.Lock()

    def push(self, value):
        with(self.lock):
            for i in range (self.length-1,0,-1):
                self.buf[i] = self.buf[i-1]
            self.buf[0] = value

            
    def copy(self):
        with(self.lock):
            return np.array(self.buf)
        

def plotter(buffer, interval, feature):
    fig, ax = plt.subplots()
    ax.set_ylim(-0.1, 0.1)
    
    # Create lines for EMG signals
    lines = [ax.plot([], [], markevery=10, label=f'EMG {i+1}')[0] for i in range(16)]  
    # Create lines for features
    feature_lines = [ax.plot([], [], linestyle='--', label=f'Feature {i+1}', color='gray')[0] for i in range(16)]

    mpl.rcParams['path.simplify'] = True
    mpl.rcParams['path.simplify_threshold'] = 1.0
    
    while True:
        buf = buffer.copy()
        feature_buf = feature.copy()
        
        # Update EMG signal lines
        for i, line in enumerate(lines):
            line.set_xdata(range(len(buf[:, i])))
            line.set_ydata(buf[:, i])
        
        # Update feature lines (constant values)
        for i, feature_line in enumerate(feature_lines):
            feature_line.set_xdata(range(len(buf[:, i])))
            feature_line.set_ydata([feature_buf[0, i]] * len(buf))  # Set feature as a constant horizontal line

        start = time.time()
        ax.relim()
        ax.autoscale_view() 
        fig.canvas.draw()
        fig.canvas.flush_events()
        print("Plotting time:", "{:07.2f}".format((time.time() - start) * 1000))
        
        plt.pause(interval)

# def plotter(buffer, interval):
#     fig, ax = plt.subplots()
#     #plt.ion() ## Vet ikke om denne er nødvendig, men den gjør plottingen dobbelt så treg
#     ax.set_ylim(-0.1,0.1)
    
#     lines = [ax.plot([], [], markevery=10, label=f'EMG {i+1}')[0] for i in range(16)]  # Create a line for each sensor
#     mpl.rcParams['path.simplify'] = True
#     mpl.rcParams['path.simplify_threshold'] = 1.0
#     while True:
#         buf = buffer.copy()
#         for i, line in enumerate(lines):
#             line.set_xdata(range(len(buf[:,i])))
#             line.set_ydata(buf[:,i])

#         start = time.time()
#         ax.relim()
#         ax.autoscale_view() 
#         fig.canvas.draw()
#         fig.canvas.flush_events()
#         print("Plotting time:" , "{:07.2f}".format((time.time() - start)*1000))
        
#         plt.pause(interval)


def plotter_all(raw_buffer, proc_buffer, interval):
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    plt.ion() ## Vet ikke om denne er nødvendig, men den gjør plottingen dobbelt så treg
    ax1.set_ylim(-0.1,0.1)
    ax2.set_ylim(-0.1,0.1)

    lines1 = [ax1.plot([], [], markevery=10, label=f'EMG {i+1}')[0] for i in range(16)]  # Create a line for each sensor
    lines2 = [ax2.plot([], [], markevery=10, label=f'EMG {i+1}')[0] for i in range(16)]  # Create a line for each sensor
    mpl.rcParams['path.simplify'] = True
    mpl.rcParams['path.simplify_threshold'] = 1.0
    while True:
        buf_raw = raw_buffer.copy()
        buf_proc = proc_buffer.copy()
        for i, line in enumerate(lines1):
            line.set_xdata(range(len(buf_raw[:,i])))
            line.set_ydata(buf_raw[:,i])

        for i, line in enumerate(lines2):
            line.set_xdata(range(len(buf_proc[:,i])))
            line.set_ydata(buf_proc[:,i])

        start = time.time()
        ax1.relim()
        ax1.autoscale_view() 
        fig1.canvas.draw()
        fig1.canvas.flush_events()
        ax2.relim()
        ax2.autoscale_view()
        fig2.canvas.draw()
        fig2.canvas.flush_events()
        print("Plotting time:" , "{:07.2f}".format((time.time() - start)*1000))
        
        plt.pause(interval)
        
def outputter(buffer, interval):
    ser = serial.Serial('COM6', baudrate=9600, timeout=1)  # Open serial port
    while True:
        vs = buffer.copy()
        #ch0 = (np.mean(vs[0:20,0]) + 0.045) * 5000 
        #ch1 = (np.mean(vs[0:20,1]) + 0.030) * 5000  
        #a = int(max(min( ch0, 250), 0))
        #b = int(max(min(-ch0, 250), 0))
        #c = int(max(min( ch1, 250), 0))
        #d = int(max(min(-ch1, 250), 0))

        a = 255 if np.mean(vs[0:10,0]) > 0     else 0
        b = 255 if np.mean(vs[0:10,0]) < -0.05 else 0
        c = 255 if np.mean(vs[0:10,1]) > 0     else 0
        d = 255 if np.mean(vs[0:10,1]) < -0.05 else 0
        ser.write(bytes([a,b,c,d]))

def remove_dc_offset(data): # Note: this changes the signal for the wole window size, ending up with the plot moving up and down -> doen't work
    for i in range (data.shape[1]):
        data[:,i] = data[:,i] - np.mean(data[:,i])

    return data

def train_classifier(rawdata_buf, classes, window_size=100, sampling_freq=2000, sample_time=2):
    window_size_time = window_size/sampling_freq
    training_buf = Thread_Safe_Buffer(int(window_size_time*sample_time)+100) #100 as safety margin
    for class_i in classes:
        print(f"Collecting training data for class {class_i}...")
        for i in range(0, sample_time):
            features = fe.feature_extraction(rawdata_buf.copy())
            training_buf.push(features)
            time.sleep(window_size_time)

    return training_buf

def main():
    trigno = Trigno()
    #print("Trigno connected")
    rawdata_buf = Thread_Safe_Buffer(1000,16)
    #preprocessed_buf = Thread_Safe_Buffer(1000)
    #feature_buf = Thread_Safe_Buffer(1)

    #plotter_thr = threading.Thread(target=plotter, args=(rawdata_buf, 1/10, feature_buf))
    #plotter_thr.start()

    #plotter_all_thr = threading.Thread(target=plotter_all, args=(rawdata_buf, preprocessed_buf, 1/10))
    #plotter_all_thr.start()

    #plotter_filtered = threading.Thread(target=plotter, args=(preprocessed_buf, 1/10, feature_buf))
    #plotter_filtered.start()

    #led_thr = threading.Thread(target=outputter, args=(rawdata_buf, 1/100) )    
    #led_thr.start()

    # raw_test  = test.generate_synthetic_emg(n_samples=100,n_channels=2,freqs=[10,20],amplitudes=[1,0.5],noise_level=0.1,dc_offset=2)
    # filtered_data = remove_dc_offset(raw_test)
    # test.test_emg_feature_extraction(filtered_data)
    # test.test_emg_feature_extraction(raw_test)
    # test.plot_test_signal(raw_test)
    # test.plot_test_signal(filtered_data)

    #train_classifier(rawdata_buf, ['open','close','rest'], window_size=100, sampling_freq=2000, sample_time=2)
    # for i in range(0, 100):
    #     rawdata_buf.push(np.multiply(trigno.read(interval=1/2000), 1000))
    #     filtered_data = remove_dc_offset(rawdata_buf.copy())
    #     preprocessed_buf.push_filtered(filtered_data)
    #     features = fe.feature_extraction(rawdata_buf.copy())

    while True:
        rawdata_buf.push(np.multiply(trigno.read(interval=1/2000), 1000))
        print("rawdata_buf", rawdata_buf.copy())
    #     filtered_data = remove_dc_offset(rawdata_buf.copy())
    #     preprocessed_buf.push_filtered(filtered_data)
    #     feature_buf.push(fe.EMGaac(rawdata_buf.copy()))
    #     print("mav", fe.EMGaac(rawdata_buf.copy()))

        
           

if __name__ == "__main__":
    main()

