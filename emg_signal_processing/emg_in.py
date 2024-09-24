import pytrigno
import time
import config


def trigno_startup():
    try:
        start_conn = time.time()
        print("Connecting to Trigno EMG device...", start_conn)
        dev = pytrigno.TrignoEMG(active_channels=config.ACTIVE_CHANNELS, samples_per_read=config.SENSOR_FREQ, # Note! Must have samples_per_read at least 1000 for filtfilt to work
                            host='localhost', cmd_port=config.COMMAND_PORT, data_port=config.EMG_PORT)
        dev.start()
        end_conn = time.time()
        print("Connected to Trigno EMG device.",end_conn)   
        print("Time used to connect to Trigno EMG device:", end_conn - start_conn)
        return dev
    except IOError as e:
        print("Error reading EMG data:", e)
        return None
    except Exception as e:
        print("Unknown error:", e)
        return None
    
def read_raw_data(dev): # Change queue to window
    try:
        raw_data = dev.read()
        raw_data_gained = raw_data*config.RAW_SIGNAL_GAIN
            
        return raw_data_gained
    
    except IOError as e:
        print("Error reading EMG data:", e)
        return None
    except Exception as e:
        print("Unknown error:", e)
        return None
    
    
def stop_trigno(dev):
    dev.stop()
    dev.__del__() # Close sockets
    print("EMG data collection stopped.")

