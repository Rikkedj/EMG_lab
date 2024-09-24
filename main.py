import multiprocessing.process
import sys
import os
import signal
import math
import socket
import multiprocessing
from multiprocessing import Manager
import threading
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.style as mplstyle
from emg_signal_processing import emg_in, emg_preprocessing, myoprocessor, to_prosthesis
import time, threading
import struct
import serial
import numpy as np
from scipy import signal
from collections import deque
mplstyle.use(['fast'])
plt.switch_backend('TkAgg')


class Trigno:

    def __init__(self):
        self.cmd = socket.create_connection(("localhost", 50040), 10)

        #def ctrl_c_handler(sig, frame):
        #    cmd.sendall(bytes("{}".format("STOP\r\n\r\n"), encoding='ascii'))
        #    print("exiting...")
        #    sys.exit(0)
        #signal.signal(signal.SIGINT, ctrl_c_handler)

        self.cmd.sendall(bytes("START\r\n\r\n", encoding='ascii'))
        print("creating connection: ", self.cmd.recv(1024))

        # reading active sensors - this just crashes the trigno control utility...?
        #for i in range(0,16):
        #    self.cmd.sendall(bytes("SENSOR {} ACTIVE?\r\n\r\n".format(i), encoding='ascii'))
        #    print("Sensor {} active: ".format(i), self.cmd.recv(1024))
        
        self.data = socket.create_connection(("localhost", 50041), 10)
        self.data.setblocking(True)
        #self.data.settimeout(10)

        self.prev_read_time = None
        self._start = time.time()

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
        
        d = self.data.recv(4*16*math.ceil(interval*2000*80)) # at most: 4 bytes per 16 channels, at 2000hz * safety factor
        print("read time: ", "{:07.2f}".format((self.prev_read_time-self._start)*1000), " ", len(d))
        #d = []
        #while not any(d):
        #    try:
        #        d = self.data.recv(4*16*math.ceil(interval*2000*80)) 
        #        break
        #    except:
        #        pass


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

class Thread_Safe_Buffer:
    def __init__(self, length):
        self.buf = np.zeros((length,16))
        self.length = length
        self.lock = threading.Lock()

    def push(self, value):
        with(self.lock):
            for i in range (self.length-1,0,-1):
                self.buf[i,:] = self.buf[i-1,:]
            self.buf[0,:] = value
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

def plotter(buffer, interval):
    fig, ax = plt.subplots()
    #plt.ion() ## Vet ikke om denne er nødvendig, men den gjør plottingen dobbelt så treg
    ax.set_ylim(-0.1,0.1)
    
    lines = [ax.plot([], [], markevery=10, label=f'EMG {i+1}')[0] for i in range(16)]  # Create a line for each sensor
    mpl.rcParams['path.simplify'] = True
    mpl.rcParams['path.simplify_threshold'] = 1.0
    while True:
        buf = buffer.copy()
        for i, line in enumerate(lines):
            line.set_xdata(range(len(buf[:,i])))
            line.set_ydata(buf[:,i])

        start = time.time()
        ax.relim()
        ax.autoscale_view() 
        fig.canvas.draw()
        fig.canvas.flush_events()
        print("Plotting time:" , "{:07.2f}".format((time.time() - start)*1000))
        
        plt.pause(interval)


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


def main():

    trigno = Trigno()
    rawdata_buf = Thread_Safe_Buffer(1000)
    preprocessed_buf = Thread_Safe_Buffer(1000)

   # rawdata_buf = Multiprocess_Safe_Buffer(1000)
   # preprocessed_buf = Multiprocess_Safe_Buffer(1000)

    #plotter_thr = threading.Thread(target=plotter, args=(rawdata_buf, 1/10))
    #plotter_all_thr = threading.Thread(target=plotter_all, args=(rawdata_buf, preprocessed_buf, 1/10))
    #plotter_all_thr.start()
    
    #plotter_raw_proc = multiprocessing.Process(target=plotter, args=(rawdata_buf.buf, 1/10))
    #plotter_filtered_proc = multiprocessing.Process(target=plotter, args=(preprocessed_buf.buf, 1/10))
#    plotter_filtered = threading.Thread(target=plotter, args=(preprocessed_buf, 1/10))
    #led_thr = threading.Thread(target=outputter, args=(rawdata_buf, 1/100) )
    
    #plotter_thr.start()
    #plotter_raw_proc.start()
    #plotter_filtered_proc.start()
    #plotter_filtered.start()
    #led_thr.start()
    while True:
        #print("rawdata_buf content: ", rawdata_buf.copy())
        print(np.multiply(trigno.read(1/250), 1000))
        rawdata_buf.push(np.multiply(trigno.read(1/250), 1000))
        print("rawdata_buf content: ", rawdata_buf.copy())
        filtered = filtering_iir(rawdata_buf.copy()[0,:], order=4, lowcut=20, highcut=450, btype='band', fs=2000)
        #preprocessed_buf.push(filtered)
        
        

        

    
    while True:


        d = data.recv(4*16)
        #for i in range(0, len(d)):
        #    if d[i] == 0:
        #        d = d[:i]
        #        break
        if d[0] != 0:
            vs = struct.unpack('<'+'f'*16, d)
            vs_str = []
            for v in vs:
                vs_str.append("{:07.4f}".format(v))
            print(", ".join(vs_str), " ", len(d), " ", "{:7.4f}".format(((time.time() - t) * 1000)))



    # Initialize connection to Trigno EMG
    dev = emg_in.trigno_startup()


    arr = []
    for i in range(100):
        t = time.time()
        raw_data = emg_in.read_raw_data(dev)
        #print(len(raw_data[0]), 'time: ', time.time()-t)
        arr.append(time.time()-t)

    fig, ax = plt.subplots()
    ax.plot(range(0,len(arr)) ,arr)
    plt.show()

if __name__ == "__main__":
    main()

