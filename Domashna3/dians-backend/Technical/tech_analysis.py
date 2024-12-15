import numpy as np
from numpy import diff

def parse_data(data):
    data_copy = []
    for x in data:
        p = dict()
        p["last_transaction"] = int(x["last_transaction"][:-8].replace('.', ''))
        p["max_value"] = int(x["max_value"][:-8].replace('.', ''))
        p["min_value"] = int(x["min_value"][:-8].replace('.', ''))
        data_copy.append(p)
    return data_copy

def calculate_relative_strength_index(data, window):
    differences = np.diff(data)
    gain = np.where(differences > 0, differences, 0)
    loss = np.where(differences < 0, -differences, 0)
    
    avg_gain = np.convolve(gain, np.ones(window), 'valid') / window
    avg_loss = np.convolve(loss, np.ones(window), 'valid') / window
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Pad the result to match the length of the input data
    rsi = np.concatenate((np.full(window, np.nan), rsi))
    
    return rsi

def calculate_momentum(data, window):
    return data.diff(window)

def calculate_williams_percent_range(data, window):
    highest_high = data.rolling(window=window).max()
    lowest_low = data.rolling(window=window).min()
    return -100 * (highest_high - data) / (highest_high - lowest_low)

def calculate_stochastic_oscillator(data, window):
    highest_high = data.rolling(window=window).max()
    lowest_low = data.rolling(window=window).min()
    return 100 * (data - lowest_low) / (highest_high - lowest_low)

def calculate_ultimate_oscillator(data):
    last_transaction = data[:]["last_transaction"]
    min_value = data[:]["min_value"]
    max_value = data[:]["max_value"]
    buying_pressure = last_transaction - min_value
    true_range = max_value - min_value
    average1 = buying_pressure.rolling(window=7).sum() / true_range.rolling(window=7).sum()
    average2 = buying_pressure.rolling(window=14).sum() / true_range.rolling(window=14).sum()
    average3 = buying_pressure.rolling(window=28).sum() / true_range.rolling(window=28).sum()
    return 100 * (4 * average1 + 2 * average2 + average3) / 7

def calculate_sma(data, window):
    return data.rolling(window=window).mean()

def calculate_ema(data, window):
    return data.ewm(span=window, adjust=False).mean()

def calculate_hull_moving_average(data, window):
    half_window = window // 2
    sqrt_window = int(np.sqrt(window))
    wma1 = data.rolling(window=half_window).mean()
    wma2 = data.rolling(window=window).mean()
    diff = 2 * wma1 - wma2
    return diff.rolling(window=sqrt_window).mean()

def volume_weighted_moving_average(data, window):
    volume = data["volume"]
    return volume.rolling(window=window).sum() / volume.rolling(window=window).sum()

def ichimoku_base_line(data, window):
    return (data["max_value"].rolling(window).max() + data["min_value"].rolling(window).min()) / 2

def tech_results(data, window):
    data = parse_data(data)
    last_transactions = np.array([x["last_transaction"] for x in data])
    result = dict()
    result["rsi"] = calculate_relative_strength_index(last_transactions, window)
    # result["momentum"] = calculate_momentum(last_transactions, window)
    # result["williams_percent_range"] = calculate_williams_percent_range(last_transactions, window)
    # result["stochastic_oscillator"] = calculate_stochastic_oscillator(last_transactions, window)
    # result["ultimate_oscillator"] = calculate_ultimate_oscillator(data)
    # result["sma"] = calculate_sma(last_transactions, window)
    # result["ema"] = calculate_ema(last_transactions, window)
    # result["hull_moving_average"] = calculate_hull_moving_average(last_transactions, window)
    # result["volume_weighted_average_price"] = volume_weighted_moving_average(data, window)
    # result["ichimoku_base_line"] = ichimoku_base_line(data, window)
    return [result]