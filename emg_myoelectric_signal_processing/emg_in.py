import pytrigno
import time
import config


def trigno_startup(stop_event):
    try:
        start_conn = time.time()
        print("Connecting to Trigno EMG device...", start_conn)
        dev = pytrigno.TrignoEMG(active_channels=config.ACTIVE_CHANNELS, samples_per_read=1000, # Note! Must have samples_per_read at least 1000 for filtfilt to work
                            host='localhost', cmd_port=config.COMMAND_PORT, data_port=config.EMG_PORT, stop_event=stop_event)
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
    
def read_raw_data(dev, raw_emg_queue): # Change queue to window
    try:
        start_read = time.time()
        print('Reading EMG data...', start_read)
        raw_data = dev.read()
        raw_data_gained = raw_data*config.RAW_SIGNAL_GAIN
        if raw_data is not None:
            raw_emg_queue.append(raw_data_gained)
            end_append = time.time()
            print('appended data to queue:', end_append)
            print('raw emg: ', raw_data)
            print('time used reading and appending raw data:', end_append - start_read)
        return raw_data
    
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


# Not used
'''
def collect_data():
# Initialize connection to Trigno EMG
try:
    start_conn = time.time()
    print("Connecting to Trigno EMG device...", start_conn)
    dev = pytrigno.TrignoEMG(active_channels=config.ACTIVE_CHANNELS, samples_per_read=1000, # Note! Must have samples_per_read at least 1000 for filtfilt to work
                        host='localhost', cmd_port=config.COMMAND_PORT, data_port=config.EMG_PORT, stop_event=stop_event)
    dev.start()
    end_conn = time.time()
    print("Connected to Trigno EMG device.",end_conn)   
    print("Time used to connect to Trigno EMG device:", end_conn - start_conn)
    #while not stop_event.is_set():
    #    time.sleep(0.1)  # Idle loop
    for i in range(2):
        start_read = time.time()
        print('Reading EMG data...', start_read)
        raw_data = dev.read()
        raw_data_gained = raw_data*config.RAW_SIGNAL_GAIN
        if raw_data is not None:
            raw_emg_queue.append(raw_data_gained)
            end_append = time.time()
            print('appended data to queue:', end_append)
            print('raw emg: ', raw_data)
            print('time used reading and appending raw data:', end_append - start_read)
        #else:
        #   break  # Exit the loop if reading fails

except IOError as e:
    print("Error reading EMG data:", e)
    #break
except Exception as e:
    print("Unknown error:", e)
    #break

#if raw_emg_queue.is_full():
    #  break
finally:
    dev.stop()
    dev.__del__() # Close sockets
    print("EMG data collection stopped.")'''