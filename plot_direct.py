'''  
plt.ion()
    fig, ax = plt.subplots()
    fig2, ax2 = plt.subplots()
    
    lines = [ax.plot([], [], label=f'EMG {i+1}')[0] for i in range(len(config.ACTIVE_CHANNELS))]  # Create a line for each sensor
    lines2 = [ax2.plot([], [], label=f'EMG {i+1}')[0] for i in range(len(config.ACTIVE_CHANNELS))]  # Create a line for each sensor

    ax.set_ylim(-1, 1)  # Adjust according to your EMG signal range
    ax.set_xlim(0, WINDOW_SIZE*config.SENSOR_FREQ+100)  # Adjust this based on how much data you want to plot at once
    ax.set_title("Real-Time EMG Data")
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")
    ax2.set_ylim(-5, 5)  # Adjust according to your EMG signal range
    ax2.set_xlim(0, WINDOW_SIZE*config.PROCESSING_FREQ)  # Adjust this based on how much data you want to plot at once
    ax2.set_title("Processed EMG Data")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Amplitude")

    data_buffer = np.zeros((len(config.ACTIVE_CHANNELS), WINDOW_SIZE*config.SENSOR_FREQ))  # Buffer to store data
    data_buffer_proc = np.zeros((len(config.ACTIVE_CHANNELS), int(WINDOW_SIZE*config.PROCESSING_FREQ)))  # Buffer to store data
    current_pos_raw = 0

    try:
        while not stop_event.is_set():
            raw_data = emg_in.read_raw_data(dev, raw_emg_queue=raw_emg_queue)
            data_buffer = np.roll(data_buffer, -len(raw_data[0]), axis=1)  # Shift data to the left
            data_buffer[:, -len(raw_data[0]):] = raw_data  # Append new data to the right
            
            for i, line in enumerate(lines):
                # Update x and y data directly from the queue
                #line.set_data(range(len(raw_data[i])), raw_data[i])
                #line.set_data(range(len(data_buffer[i])), data_buffer[i])
                line.set_xdata(np.arange(current_pos_raw, current_pos_raw + len(data_buffer[i])))
                line.set_ydata(data_buffer[i])

            ax.relim(True)
            ax.autoscale_view() 
            ax.set_xlim(current_pos_raw, current_pos_raw + WINDOW_SIZE*config.SENSOR_FREQ+100)
            # drawing updated values
            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.pause(0.1)
            current_pos_raw = current_pos_raw + len(raw_data[0])
            # print('raw_emg_queue:', raw_emg_queue.queue)
            #preprocessed_data = emg_preprocessing.preprocess_raw_data(raw_emg_queue=raw_emg_queue, preprocessed_emg_queue=preprocessed_emg_queue)
            preprocessed_data = emg_preprocessing.preprocess_raw_data_directly(raw_data=raw_data, preprocessed_emg_queue=preprocessed_emg_queue)
            print('preprocessed_data:', preprocessed_data)
            data_buffer_proc = np.roll(data_buffer_proc, -len(preprocessed_data[0]), axis=1)  # Shift data to the left
            data_buffer_proc[:, -len(preprocessed_data[0]):] = preprocessed_data  # Append new data to the right
            for i, line in enumerate(lines2):
                # Update x and y data directly from the queue
                #line.set_data(range(len(raw_data[i])), raw_data[i])
                line.set_data(range(len(data_buffer_proc[i])), data_buffer_proc[i])

            ax2.relim()
            ax2.autoscale_view() 
            # drawing updated values
            fig2.canvas.draw()
            fig2.canvas.flush_events()
            #time.sleep(0.1)
            plt.pause(0.1)

            # print('preprocessed_emg_queue:', preprocessed_emg_queue.queue)
            #hand_controll, wrist_controll = myoprocessor_controll(hand_or_wrist, cocontraction)
            hand_controll, wrist_controll = myoprocessor_controll_directly(preprocessed_data, hand_or_wrist, cocontraction)
            #print('hand_controll:', hand_controll)
            #print('wrist_controll:', wrist_controll)
            setpoints = prosthesis_setpoints(hand_controll, wrist_controll)
            #print('prosthesis_setpoint:', setpoints)
            #if ser.is_open:
            #    pyserial.write_to_hand(ser=ser, setpoints=setpoints)
            #else:
            #    print("Serial port is not open")

'''