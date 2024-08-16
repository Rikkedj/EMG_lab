"""
Copyright (c) 2017 The Regents of the University of California

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import socket
import struct
import numpy

class _BaseTrignoDaq(object):
    """
    Delsys Trigno wireless EMG system.

    Requires the Trigno Control Utility to be running.

    Parameters
    ----------
    host : str
        IP address the TCU server is running on.
    cmd_port : int
        Port of TCU command messages.
    data_port : int
        Port of TCU data access.
    rate : int
        Sampling rate of the data source.
    total_channels : int
        Total number of channels supported by the device.
    timeout : float
        Number of seconds before socket returns a timeout exception

    Attributes
    ----------
    BYTES_PER_CHANNEL : int
        Number of bytes per sample per channel. EMG and accelerometer data
    CMD_TERM : str
        Command string termination.

    Notes
    -----
    Implementation details can be found in the Delsys SDK reference:
    http://www.delsys.com/integration/sdk/
    """

    BYTES_PER_CHANNEL = 4
    CMD_TERM = '\r\n\r\n'

    def __init__(self, host, cmd_port, data_port, total_channels, timeout, stop_event):
        self.host = host
        self.cmd_port = cmd_port
        self.data_port = data_port
        self.total_channels = total_channels
        self.timeout = timeout
        self.stop_event = stop_event

        self._min_recv_size = self.total_channels * self.BYTES_PER_CHANNEL

        self._initialize()

    def _initialize(self):
        try:
            # Create command socket and consume the server's initial response
            self._comm_socket = socket.create_connection(
                (self.host, self.cmd_port), self.timeout)
            self._comm_socket.recv(1024)  # Initially reading a small packet to clear buffer

            # Create the data socket
            self._data_socket = socket.create_connection(
                (self.host, self.data_port), self.timeout)

            # Set the timeout for the data socket for non-blocking operations
            self._data_socket.settimeout(self.timeout)
        
        except socket.error as e:
            print(f"Error initializing sockets: {e}")
            raise e



    def start(self):
        """
        Tell the device to begin streaming data.

        You should call ``read()`` soon after this, though the device typically
        takes about two seconds to send back the first batch of data.
        """
        self._send_cmd('START')

    def read(self, num_samples):
        """
        Request a sample of data from the device.

        This is a blocking method, meaning it returns only once the requested
        number of samples are available.

        Parameters
        ----------
        num_samples : int
            Number of samples to read per channel.

        Returns
        -------
        data : ndarray, shape=(total_channels, num_samples)
            Data read from the device. Each channel is a row and each column
            is a point in time.
        """
        l_des = num_samples * self._min_recv_size
        l = 0
        packet = bytes()
        while l < l_des:
            if self.stop_event.is_set():
                print("Data reading stopped due to signal interrupt.")
                return None
            try:
                # Attempt to receive data from the socket
                chunk = self._data_socket.recv(l_des - l)
                if not chunk:
                    # If chunk is empty, the connection is closed
                    raise IOError("Device disconnected.")
                packet += chunk
            except socket.timeout:
                # Timeout occurred, check if stop event is set
                l = len(packet)
                packet += b'\x00' * (l_des - l)
                raise IOError("Device disconnected.")
            except socket.error as e:
                # Handle other socket errors
                print(f"Socket error: {e}")
                return None
            
            l = len(packet)

        data = numpy.asarray(
            struct.unpack('<'+'f'*self.total_channels*num_samples, packet))
        data = numpy.transpose(data.reshape((-1, self.total_channels)))

        return data

    def stop(self):
        """Tell the device to stop streaming data."""
        self._send_cmd('STOP')

    def reset(self):
        """Restart the connection to the Trigno Control Utility server."""
        self._initialize()

    def __del__(self):
        try:
            self._comm_socket.close()
            self._data_socket.close()
        except Exception as e:
            print(f"Error closing sockets: {e}")

    def _send_cmd(self, command):
        self._comm_socket.send(self._cmd(command))
        resp = self._comm_socket.recv(128)
        self._validate(resp)

    @staticmethod
    def _cmd(command):
        return bytes("{}{}".format(command, _BaseTrignoDaq.CMD_TERM),
                     encoding='ascii')

    @staticmethod
    def _validate(response):
        s = str(response)
        if 'OK' not in s:
            print("warning: TrignoDaq command failed: {}".format(s))


class TrignoEMG(_BaseTrignoDaq):
    """
    Delsys Trigno wireless EMG system EMG data.

    Requires the Trigno Control Utility to be running.

    Parameters
    ----------
    channel_range : tuple with 2 ints
        Sensor channels to use, e.g. (lowchan, highchan) obtains data from
        channels lowchan through highchan. Each sensor has a single EMG
        channel.
    active_channels : list of int
        List of active channels indices to read from.
    samples_per_read : int
        Number of samples per channel to read in each read operation.
    units : {'V', 'mV', 'normalized'}, optional
        Units in which to return data. If 'V', the data is returned in its
        un-scaled form (volts). If 'mV', the data is scaled to millivolt level.
        If 'normalized', the data is scaled by its maximum level so that its
        range is [-1, 1].
    host : str, optional
        IP address the TCU server is running on. By default, the device is
        assumed to be attached to the local machine.
    cmd_port : int, optional
        Port of TCU command messages.
    data_port : int, optional
        Port of TCU EMG data access. By default, 50041 is used, but it is
        configurable through the TCU graphical user interface.
    timeout : float, optional
        Number of seconds before socket returns a timeout exception.
    stop_event: threading.Event, optional for handling interrupts while running

    Attributes
    ----------
    rate : int
        Sampling rate in Hz.
    scaler : float
        Multiplicative scaling factor to convert the signals to the desired
        units.
    """

    def __init__(self, channel_range=None, active_channels=None, samples_per_read=2000, units='V',
                 host='localhost', cmd_port=50040, data_port=50041, timeout=10, stop_event=None):
        super(TrignoEMG, self).__init__(
            host=host, cmd_port=cmd_port, data_port=data_port,
            total_channels=16, timeout=timeout, stop_event=stop_event)

        self.channel_range = channel_range
        self.samples_per_read = samples_per_read

        # Ensure either channel_range or active_channels is specified
        if not channel_range and not active_channels:
            raise ValueError("Either channel_range or active_channels must be specified.")
        
        if channel_range:
            self.set_channel_range(channel_range)  
        elif active_channels:   
            self.set_active_channels(active_channels)

        self.rate = 2000

        self.scaler = 1.
        if units == 'mV':
            self.scaler = 1000.
        elif units == 'normalized':
            # max range of EMG data is 11 mV
            self.scaler = 1 / 0.011

    def set_channel_range(self, channel_range):
        """
        Sets the number of channels to read from the device.

        Parameters
        ----------
        channel_range : tuple
            Sensor channels to use (lowchan, highchan).
        """
        # Validate the channel range
        if not isinstance(channel_range, tuple) or len(channel_range) != 2:
            raise ValueError("Channel range must be a tuple of two integers.")

        if not all(isinstance(ch, int) for ch in channel_range):
            raise ValueError("Channel range values must be integers.")

        self.channel_range = channel_range
        self.active_channels = list(range(channel_range[0], channel_range[1] + 1))
        self.num_channels = channel_range[1] - channel_range[0] + 1

    def set_active_channels(self, active_channels):
        """
        Sets the active channels to read from the device.

        Parameters
        ----------
        active_channels : list of int
            List of active channels(sensors) to read from.
        """
        # Validate active channels
        if not isinstance(active_channels, list) or not active_channels:
            raise ValueError("Active channels must be a non-empty list of integers.")

        if not all(isinstance(ch, int) for ch in active_channels):
            raise ValueError("Active channels must only contain integers.")
        
        self.active_channels = [ch - 1 for ch in active_channels]
        self.num_channels = len(active_channels)

    def read(self):
        """
        Request a sample of data from the device.

        This is a blocking method, meaning it returns only once the requested
        number of samples are available.

        Returns
        -------
        data : ndarray, shape=(num_channels, num_samples)
            Data read from the device. Each channel is a row and each column
            is a point in time.
        """
        # Read full data from device
        data = super(TrignoEMG, self).read(self.samples_per_read)
        # Select only active channels
        active_data = data[self.active_channels, :]
        # Scale data if necessary
        return self.scaler * active_data
    
    def get_active_channels(self):
        """
        Get the list of active channels currently set.

        Returns
        -------
        active_channels : list of int
            List of active channel indices currently set.
        """
        return self.active_channels
 

class TrignoAccel(_BaseTrignoDaq):
    """
    Delsys Trigno wireless EMG system accelerometer data.

    Requires the Trigno Control Utility to be running.

    Parameters
    ----------
    channel_range : tuple with 2 ints
        Sensor channels to use, e.g. (lowchan, highchan) obtains data from
        channels lowchan through highchan. Each sensor has three accelerometer
        channels.
    samples_per_read : int
        Number of samples per channel to read in each read operation.
    host : str, optional
        IP address the TCU server is running on. By default, the device is
        assumed to be attached to the local machine.
    cmd_port : int, optional
        Port of TCU command messages.
    data_port : int, optional
        Port of TCU accelerometer data access. By default, 50042 is used, but
        it is configurable through the TCU graphical user interface.
    timeout : float, optional
        Number of seconds before socket returns a timeout exception.
    """
    def __init__(self, channel_range, samples_per_read, host='localhost',
                 cmd_port=50040, data_port=50042, timeout=10):
        super(TrignoAccel, self).__init__(
            host=host, cmd_port=cmd_port, data_port=data_port,
            total_channels=48, timeout=timeout)

        self.channel_range = channel_range
        self.samples_per_read = samples_per_read

        self.rate = 148.1

    def set_channel_range(self, channel_range):
        """
        Sets the number of channels to read from the device.

        Parameters
        ----------
        channel_range : tuple
            Sensor channels to use (lowchan, highchan).
        """
        self.channel_range = channel_range
        self.num_channels = channel_range[1] - channel_range[0] + 1

    def read(self):
        """
        Request a sample of data from the device.

        This is a blocking method, meaning it returns only once the requested
        number of samples are available.

        Returns
        -------
        data : ndarray, shape=(num_channels, num_samples)
            Data read from the device. Each channel is a row and each column
            is a point in time.
        """
        data = super(TrignoAccel, self).read(self.samples_per_read)
        data = data[self.channel_range[0]:self.channel_range[1]+1, :]
        return data