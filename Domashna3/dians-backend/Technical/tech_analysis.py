import numpy as np
# import pandas as pd

def parse_singular(entry: str):
    return int(entry[:-8].replace('.', ''))

def parse_data(data):
    data_copy = []
    for entry in data:
        parsed = dict()
        for part in ['last_transaction', 'max_value', 'min_value']:
            parsed[part] = parse_singular(entry[part])
        parsed["volume"] = int(entry["volume"][:].replace('.', ''))
        data_copy.append(parsed)
    return data_copy

def calculate_relative_strength_index(data, window):
    differences = np.diff(data)
    gain = np.where(differences > 0, differences, 0)
    loss = np.where(differences < 0, -differences, 0)
    
    avg_gain = np.convolve(gain, np.ones(window), 'valid') / window
    avg_loss = np.convolve(loss, np.ones(window), 'valid') / window
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi[0],3)

def calculate_momentum(data, window):
    return round((data[0]-data[window-1])/data[window-1]*100,3)

def calculate_williams_percent_range(data, window):
    highest_high = max(data[:window])
    lowest_low = min(data[:window])
    return round(-100 * (highest_high - data[0]) / (highest_high - lowest_low),3)

def calculate_stochastic_oscillator(data, window):
    highest_high = max(data[:window])
    lowest_low = min(data[:window])
    return round(100 * (data[0] - lowest_low) / (highest_high - lowest_low),3)

def calculate_ultimate_oscillator(data):
    def rolling_sum(values, window):
        """Helper function to calculate the rolling sum for a given window size."""
        if len(values) < window:
            return 0  
        return sum(values[-window:])

    last_transaction = [x["last_transaction"] for x in data]
    min_value = [x["min_value"] for x in data]
    max_value = [x["max_value"] for x in data]

    buying_pressure = [last - min_ for last, min_ in zip(last_transaction, min_value)]
    true_range = [max_ - min_ for max_, min_ in zip(max_value, min_value)]
    
    def bp_tr_sum(window):
        bp_sum = rolling_sum(buying_pressure, window)
        tr_sum = rolling_sum(true_range, window)
        avg = bp_sum / tr_sum if tr_sum != 0 else 0
        return bp_sum, tr_sum, avg
    
    bp_sums = []
    tr_sums = []
    avgs = []

    for window in [7, 14, 28]:
        bp_sum, tr_sum, avg = bp_tr_sum(window)
        bp_sums.append(bp_sum)
        tr_sums.append(tr_sum)
        avgs.append(avg)
    
    ultimate_oscillator = 100 * ((4 * avgs[0]) + (2 * avgs[1]) + avgs[2]) / 7

    return round(ultimate_oscillator,3)


def calculate_sma(data, window):
    return round(sum(data[:window]) / window,3)

def calculate_ema(data, window):
    data = data[::-1]
    alpha = 2 /(window + 1.0)
    alpha_rev = 1-alpha
    n = data.shape[0]

    pows = alpha_rev**(np.arange(n+1))

    scale_arr = 1/pows[:-1]
    offset = data[0]*pows[1:]
    pw0 = alpha*alpha_rev**(n-1)

    mult = data*pw0*scale_arr
    cumsums = mult.cumsum()
    out = offset + cumsums*scale_arr[::-1]

    return round(out[window-1],3)

def weighted_moving_average(arr, window):
    weights = np.arange(1, window + 1)
    return np.convolve(arr, weights / weights.sum(), mode='valid')

def hull_moving_average(arr, period):
    arr = arr[::-1]
    
    half_period = period // 2
    wma_half = weighted_moving_average(arr, half_period)
    
    wma_full = weighted_moving_average(arr, period)
    
    diff = 2 * wma_half[len(wma_half) - len(wma_full):] - wma_full
    
    sqrt_period = int(np.sqrt(period))
    hma = weighted_moving_average(diff, sqrt_period)
    return round(hma[-1],3)

def volume_weighted_moving_average(data, window):
    weighted_price_sum = 0
    volume_sum = 0
    
    for entry in data[:window]:
        price = entry['last_transaction'] 
        volume = entry['volume']
        
        weighted_price_sum += price * volume
        volume_sum += volume

    vwma = weighted_price_sum / volume_sum if volume_sum != 0 else 0
    return round(vwma,3)

def ichimoku_base_line(data, period):
    """Calculate the Ichimoku Base Line (Kijun-Sen) for a list of dictionaries."""
    data = data[::-1]
    kijun_sen_values = []

    for i in range(period - 1, len(data)):
        highest_high = max([entry['max_value'] for entry in data[i - period + 1:i + 1]])
        lowest_low = min([entry['min_value'] for entry in data[i - period + 1:i + 1]])
        
        kijun_sen = (highest_high + lowest_low) / 2
        kijun_sen_values.append(kijun_sen)

    return kijun_sen_values[0]

def tech_results(data, window):
    data = parse_data(data)
    window = min(window, len(data))
    last_transactions = np.array([x["last_transaction"] for x in data])
    result = dict()
    result["rsi"] = calculate_relative_strength_index(last_transactions, window)
    result["momentum"] = calculate_momentum(last_transactions, window)
    result["williams_percent_range"] = calculate_williams_percent_range(last_transactions, window)
    result["stochastic_oscillator"] = calculate_stochastic_oscillator(last_transactions, window)
    result["ultimate_oscillator"] = calculate_ultimate_oscillator(data)
    result["sma"] = calculate_sma(last_transactions, min(window, 10))
    result["ema"] = calculate_ema(last_transactions, min(window, 10))
    result["hull_moving_average"] = hull_moving_average(last_transactions, min(9, window))
    result["volume_weighted_average_price"] = volume_weighted_moving_average(data, window)
    result["ichimoku_base_line"] = ichimoku_base_line(data, window)
    return result