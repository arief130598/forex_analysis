def calculate_ema(prices, days, smoothing=2):
    ema = [sum(prices[:days]) / days]
    for price in prices[days:]:
        ema.append((price * (smoothing / (1 + days))) + ema[-1] * (1 - (smoothing / (1 + days))))

    first_value = ema[0]
    for _ in range(days - 1):
        ema.insert(0, first_value)
    return ema


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


def get_best_single_ema(pair, multiplier, timespan):
    if timespan == 'hour':
        if multiplier == '1':
            if pair == 'AUDUSD':
                return [20, 8]
            elif pair == 'EURUSD':
                return [20, 12]
            elif pair == 'GBPUSD':
                return [20, 5]
            elif pair == 'USDCAD':
                return [50, 15]
            elif pair == 'USDJPY':
                return [120, 18]
            elif pair == 'XAUUSD':
                return [170, 9]
            elif pair == 'GBPJPY':
                return [60, 8]
            elif pair == 'EURGBP':
                return [50, 14]
            elif pair == 'GBPCAD':
                return [140, 7]
            elif pair == 'GBPAUD':
                return [100, 19]
            elif pair == 'EURJPY':
                return [30, 10]
            elif pair == 'AUDCAD':
                return [60, 18]
            elif pair == 'EURAUD':
                return [180, 12]
            elif pair == 'AUDJPY':
                return [40, 5]
            elif pair == 'CADJPY':
                return [70, 5]
            elif pair == 'EURCAD':  # 19F, 18T
                return [50, 5]


def get_best_double_ema(pair, multiplier, timespan):
    if timespan == 'hour':
        if multiplier == '1':
            if pair == 'AUDUSD':
                return [5, 60, 30]
            elif pair == 'EURUSD':
                return [15, 20, 70]
            elif pair == 'GBPUSD':
                return [15, 20, 50]
            elif pair == 'USDCAD':
                return [15, 20, 40]
            elif pair == 'USDJPY':
                return [5, 60, 30]
            elif pair == 'XAUUSD':
                return [15, 30, 30]
            elif pair == 'GBPJPY':
                return [15, 20, 50]
            elif pair == 'EURGBP':
                return [5, 40, 70]
            elif pair == 'GBPCAD':
                return [15, 20, 30]
            elif pair == 'GBPAUD':
                return [15, 50, 50]
            elif pair == 'EURJPY':
                return [15, 90, 30]
            elif pair == 'AUDCAD':
                return [10, 20, 30]
            elif pair == 'EURAUD':
                return [5, 40, 30]
            elif pair == 'AUDJPY':
                return [10, 30, 60]
            elif pair == 'CADJPY':
                return [10, 50, 90]
            elif pair == 'EURCAD':
                return [15, 20, 80]
