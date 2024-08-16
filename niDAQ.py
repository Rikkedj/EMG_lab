import nidaqmx


DEV_NAME = "cDAQ9191-16C8EAEMod1" # Device name, you find this in NI MAX

# Periodically read from setpoint queue and write to the DAQ
# 1. Create a task
def write_to_daq(setpoint_queue):
    if setpoint_queue.is_empty():
        print("Setpoint queue is empty")
        return
    # Check if DAQ is connected
    try:
        with nidaqmx.Task() as task:
            print("Task created in daq")
            task.ao_channels.add_ao_voltage_chan(DEV_NAME+"/ao0") # ao0 is the channel number
            sample_index, setpoint = setpoint_queue.get_last()
            for i in range(len(setpoint)):
                print(task.write(setpoint[i], auto_start=True))
            #print(task.write(setpoint[0], auto_start=True)) # Write 3 values to the channel
    except nidaqmx.DaqError as e:
        print("Error writing to DAQ:", e)
        return
    except Exception as e:
        print("Unknown error:", e)
        return
    

'''
with nidaqmx.Task() as task:
    task.ao_channels.add_ao_voltage_chan(DEV_NAME+"/ao0") # ai0 is the channel number
    print(task.write([1.0, 2.0, 3.0, 9.3], auto_start=True)) # Write 3 values to the channel
'''