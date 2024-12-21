import numpy as np


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
    if window > 1:
        avg_gain = np.convolve(gain, np.ones(window), 'valid') / window
        avg_loss = np.convolve(loss, np.ones(window), 'valid') / window
    else:
        result = 0
    if avg_loss[0] == 0:
        result = 0
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        result = round(rsi[0], 3)

    if result == 0:
        return result, "neutral"
    elif result <= 20:
        return result, "strong_buy"
    elif result <= 40:
        return result, "buy"
    elif result <= 60:
        return result, "neutral"
    elif result <= 80:
        return result, "sell"
    else:
        return result, "strong_sell"


def calculate_momentum(data, window):
    result = round((data[0]-data[window-1])/data[window-1]*100, 3)

    if result == 0:
        return result, "neutral"
    elif result <= -5:
        return result, "strong_sell"
    elif result <= -1:
        return result, "sell"
    elif result <= 1:
        return result, "neutral"
    elif result <= 5:
        return result, "buy"
    else:
        return result, "strong_buy"


def calculate_williams_percent_range(data, window):
    window = 1
    highest_high = max(data[:window])
    lowest_low = min(data[:window])
    if highest_high == lowest_low:
        result = 0
    else:
        result = round(-100 * (highest_high -
                               data[0]) / (highest_high - lowest_low), 3)

    if result == 0:
        return result, "neutral"
    elif result <= -80:
        return result, "strong_buy"
    elif result <= -60:
        return result, "buy"
    elif result <= -40:
        return result, "neutral"
    elif result <= -20:
        return result, "sell"
    else:
        return result, "strong_sell"


def calculate_stochastic_oscillator(data, window):
    highest_high = max(data[:window])
    lowest_low = min(data[:window])
    if highest_high == lowest_low:
        result = 0
    else:
        result = round(100 * (data[0] - lowest_low) /
                       (highest_high - lowest_low), 3)

    if result == 0:
        return result, "neutral"
    elif result <= 20:
        return result, "strong_buy"
    elif result <= 40:
        return result, "buy"
    elif result <= 60:
        return result, "neutral"
    elif result <= 80:
        return result, "sell"
    else:
        return result, "strong_sell"


def calculate_ultimate_oscillator(data):
    def rolling_sum(values, window):
        """Helper function to calculate the rolling sum for a given window size."""
        if len(values) < window:
            return 0
        return sum(values[-window:])

    last_transaction = [x["last_transaction"] for x in data]
    min_value = [x["min_value"] for x in data]
    max_value = [x["max_value"] for x in data]

    buying_pressure = [last - min_ for last,
                       min_ in zip(last_transaction, min_value)]
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

    result = round(ultimate_oscillator, 3)

    if result == 0:
        return result, "neutral"
    elif result <= 30:
        return result, "strong_buy"
    elif result <= 45:
        return result, "buy"
    elif result <= 55:
        return result, "neutral"
    elif result <= 70:
        return result, "sell"
    else:
        return result, "strong_sell"


def calculate_sma(data, window):
    return round(sum(data[:window]) / window, 3)


def calculate_ema(data, window):
    data = data[::-1]
    alpha = 2 / (window + 1.0)
    alpha_rev = 1-alpha
    n = data.shape[0]

    pows = alpha_rev**(np.arange(n+1))

    scale_arr = 1/pows[:-1]
    offset = data[0]*pows[1:]
    pw0 = alpha*alpha_rev**(n-1)

    mult = data*pw0*scale_arr
    cumsums = mult.cumsum()
    out = offset + cumsums*scale_arr[::-1]

    return round(out[window-1], 3)


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
    return round(hma[-1], 3)


def volume_weighted_moving_average(data, window):
    weighted_price_sum = 0
    volume_sum = 0

    for entry in data[:window]:
        price = entry['last_transaction']
        volume = entry['volume']

        weighted_price_sum += price * volume
        volume_sum += volume

    vwma = weighted_price_sum / volume_sum if volume_sum != 0 else 0
    return round(vwma, 3)


def ichimoku_base_line(data, period):
    if len(data) < period:
        return 0, "neutral"

    data = data[::-1]

    try:
        highest_high = max([entry['max_value'] for entry in data[:period]])
        lowest_low = min([entry['min_value'] for entry in data[:period]])

        base_line = (highest_high + lowest_low) / 2

        current_price = data[0]['last_transaction']

        if base_line == 0:
            return 0, "neutral"

        percent_diff = ((current_price - base_line) / base_line) * 100

        if abs(percent_diff) < 1:
            signal = "neutral"
        elif percent_diff <= -10:
            signal = "strong_sell"
        elif percent_diff < 0:
            signal = "sell"
        elif percent_diff <= 10:
            signal = "buy"
        else:
            signal = "strong_buy"

        return round(base_line, 3), signal

    except (KeyError, IndexError, ZeroDivisionError):
        return 0, "neutral"


def compare_moving_averages(price: float, sma: float, ema: float, hma: float, vwma: float) -> str:
    if price == 0 or sma == 0:
        return "neutral"
    
    signals = [
        price > sma,
        price > ema,
        price > hma,
        price > vwma
    ]
    above_count = sum(signals)

    trending_up = hma > ema > sma
    trending_down = hma < ema < sma

    if above_count >= 3 and trending_up:
        return "strong_buy"
    elif above_count >= 2:
        return "buy"
    elif above_count == 2:
        return "neutral"
    elif above_count == 1:
        return "sell"
    elif above_count == 0 and trending_down:
        return "strong_sell"
    else:
        return "sell"


def get_overall_signal(data: dict) -> str:
    period_data = data

    signals = {
        "strong_sell": 0,
        "sell": 0,
        "neutral": 0,
        "buy": 0,
        "strong_buy": 0
    }

    current_price = period_data.get("last_transaction", period_data["sma"])

    signals[period_data["rsi"][1]] += 1
    signals[period_data["momentum"][1]] += 1
    signals[period_data["williams_percent_range"][1]] += 1
    signals[period_data["stochastic_oscillator"][1]] += 1
    signals[period_data["ultimate_oscillator"][1]] += 1
    signals[compare_moving_averages(
        current_price,
        period_data["sma"],
        period_data["ema"],
        period_data["hull_moving_average"],
        period_data["volume_weighted_average_price"]
    )] += 1
    signals[period_data["ichimoku_base_line"][1]] += 1

    max_signal = max(signals.items(), key=lambda x: x[1])

    if list(signals.values()).count(max_signal[1]) > 1:
        return "neutral"

    return max_signal[0]


def tech_results(data, window):
    data = parse_data(data)
    window = min(window, len(data))
    last_transactions = np.array([x["last_transaction"] for x in data])
    result = dict()
    result["rsi"] = calculate_relative_strength_index(
        last_transactions, window)
    result["momentum"] = calculate_momentum(last_transactions, window)
    result["williams_percent_range"] = calculate_williams_percent_range(
        last_transactions, window)
    result["stochastic_oscillator"] = calculate_stochastic_oscillator(
        last_transactions, window)
    result["ultimate_oscillator"] = calculate_ultimate_oscillator(data)
    result["sma"] = calculate_sma(last_transactions, min(window, 10))
    result["ema"] = calculate_ema(last_transactions, min(window, 10))
    result["hull_moving_average"] = hull_moving_average(
        last_transactions, min(9, window))
    result["volume_weighted_average_price"] = volume_weighted_moving_average(
        data, window)
    result["ma_comparison"] = compare_moving_averages(last_transactions[0], calculate_sma(last_transactions, min(window, 10)), calculate_ema(
        last_transactions, min(window, 10)), hull_moving_average(last_transactions, min(9, window)), volume_weighted_moving_average(data, window))
    result["ichimoku_base_line"] = ichimoku_base_line(data, window)
    result["overall_signal"] = get_overall_signal(result)
    return result
