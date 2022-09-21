import pandas as pd


def get_bollinger_bands(data, rate=20, std_multi=20):
    result = pd.DataFrame()
    result['Mid'] = sma = data.rolling(rate).mean()
    std = data.rolling(std_multi).std()
    result['Up'] = sma + std * 2
    result['Down'] = sma - std * 2
    return result
