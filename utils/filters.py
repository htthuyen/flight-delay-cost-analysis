def select_airline(data, airline):
    """
    filter dataset by airline code 

    Parameters:
        data (pd.DataFrame): flight dataset
        airline(str): airline code (e.g. 'AA') 

    Returns:
        pd.DataFrame: Filtered dataset
    """
    airline = airline.strip().upper()

    df = data[data['OP_UNIQUE_CARRIER'] == airline]
    
    if df.empty:
        raise ValueError(f"No records found for airline input '{airline}'.")
    return df