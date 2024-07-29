"""
Tests communication with and data acquisition from a Delsys Trigno wireless
EMG system. Delsys Trigno Control Utility needs to be installed and running,
and the device needs to be plugged in. Tests can be run with a device connected
to a remote machine if needed.

The tests run by this script are very simple and are by no means exhaustive. It
just sets different numbers of channels and ensures the data received is the
correct shape.

Use `-h` or `--help` for options.
"""

import argparse
import config

try:
    import pytrigno
except ImportError:
    import sys
    sys.path.insert(0, '..')
    import pytrigno


def check_emg(host='localhost', active_channels=None, stop_event=None):
    dev = pytrigno.TrignoEMG(active_channels=active_channels, samples_per_read=270,
                             host=host, cmd_port=config.COMMAND_PORT, data_port=config.EMG_PORT, stop_event=stop_event)

    dev.start()
    
    data = dev.read()
    #assert data.shape == (5, 270)
    dev.stop()
    return data


def read_emg(dev):
    dev.start()
    data = dev.read()
    return data

def stop_emg(dev):
    dev.stop()  

def reset_emg(dev):
    dev.reset()


def check_accel(host):
    dev = pytrigno.TrignoAccel(channel_range=(0, 2), samples_per_read=10,
                               host=host)

    dev.start()
    for i in range(4):
        data = dev.read()
        assert data.shape == (3, 10)
    dev.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-a', '--addr',
        dest='host',
        default='localhost',
        help="IP address of the machine running TCU. Default is localhost.")
    args = parser.parse_args()

    check_emg(args.host)
    #check_accel(args.host)