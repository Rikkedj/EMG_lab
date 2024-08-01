import pandas as pd


def load_emg_data_csv(file_path):
    """
    Load EMG data from a CSV file with European decimal and delimiter handling.

    Args:
        file_path (str): The path to the CSV file containing the EMG data.

    Returns:
        pd.DataFrame: A DataFrame containing the EMG data.
    """
    try:
        # Read the CSV file with semicolon as delimiter and comma as decimal separator
        df = pd.read_csv(file_path, delimiter='\t', decimal=',')
      
        # If the initial attempt fails, try other possible delimiters
        if df.shape[1] == 1:
            # Try with a semicolon if tabs don't work
            df = pd.read_csv(file_path, sep=';', decimal=',', encoding='utf-8')

        # Rename columns to avoid duplication
        df.columns = [
            'Time_EMG_1', 'Signal_EMG_1', 
            'Time_EMG_2', 'Signal_EMG_2', 
            'Time_EMG_3', 'Signal_EMG_3', 
            'Time_EMG_4', 'Signal_EMG_4'
        ]
        # Display basic information about the data
        print("CSV Data loaded successfully!")
        print(f"Number of sensors (columns): {df.shape[1] // 2}")
        print(f"Number of samples (rows): {df.shape[0]}")
        print(f"Column names (sensor labels): {list(df.columns)}")

        # Return the DataFrame
        return df

    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return None

