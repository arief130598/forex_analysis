def calculate_ema(prices, days, smoothing=2):
    ema = [sum(prices[:days]) / days]
    for price in prices[days:]:
        ema.append((price * (smoothing / (1 + days))) + ema[-1] * (1 - (smoothing / (1 + days))))

    first_value = ema[0]
    for _ in range(days - 1):
        ema.insert(0, first_value)
    return ema


def calculate_ema_multiprocessing_n(input, output):
    for params in iter(input.get, 'STOP'):
        pair = params[0]
        data = params[1]
        prices = data['Open']
        days = params[2][0]
        smoothing = params[2][1]
        data['EMA'] = calculate_ema(prices, days, smoothing)
        output.put([pair, days, smoothing, data])


def calculate_ema_multiprocessing(params):
    pair = params[0]
    data = params[1]
    prices = data['Open']
    days = params[2][0]
    smoothing = params[2][1]

    data['EMA'] = calculate_ema(prices, days, smoothing)
    return [pair, days, smoothing, data]


def calculate_double_ema_multiprocessing(params):
    pair = params[0]
    data = params[1]
    prices = data['Open']
    smoothing = params[2][0]
    days_1 = params[2][1]
    days_2 = params[2][2]

    data['EMA'] = calculate_ema(prices, days_1, smoothing)
    data['EMA2'] = calculate_ema(prices, days_2, smoothing)
    return [pair, smoothing, days_1, days_2, data]
