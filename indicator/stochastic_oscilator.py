import pandas as pd


def calculate_stoch(data, k, d):
    stoch = pd.DataFrame()
    stoch['time'] = data['Time']
    stoch['high'] = data['High'].rolling(k).max()
    stoch['low'] = data['Low'].rolling(k).min()
    stoch['%K'] = (data['Close'] - stoch['low']) * 100 / (stoch['high'] - stoch['low'])
    stoch['%D'] = stoch['%K'].rolling(d).mean()
    return stoch
