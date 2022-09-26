import itertools
import multiprocessing
import time

import pandas as pd
from firebase_admin import db

from indicator import ema
from lib import pair_decimal as pair_decimal
from lib.fcm import send_notif


def get_best_xcandle(pair, multiplier, timespan):
    if timespan == 'hour':
        if multiplier == '1':
            if pair == 'AUDUSD':
                return 20
            elif pair == 'EURUSD':
                return 23
            elif pair == 'GBPUSD':
                return 19
            elif pair == 'USDCAD':
                return 11
            elif pair == 'USDJPY':
                return 29
            elif pair == 'XAUUSD':
                return 16
            elif pair == 'GBPJPY':
                return 21
            elif pair == 'EURGBP':
                return 15
            elif pair == 'GBPCAD':
                return 23
            elif pair == 'GBPAUD':
                return 25
            elif pair == 'EURJPY':
                return 27
            elif pair == 'AUDCAD':
                return 28
            elif pair == 'EURAUD':
                return 23
            elif pair == 'AUDJPY':
                return 14
            elif pair == 'CADJPY':
                return 28
            elif pair == 'EURCAD':
                return 11


def get_reversal(pair, multiplier, timespan):
    if timespan == 'hour':
        if multiplier == '1':
            if pair == 'AUDUSD':
                return False
            elif pair == 'EURUSD':
                return False
            elif pair == 'GBPUSD':
                return True
            elif pair == 'USDCAD':
                return False
            elif pair == 'USDJPY':
                return False
            elif pair == 'XAUUSD':
                return True
            elif pair == 'GBPJPY':
                return True
            elif pair == 'EURGBP':
                return True
            elif pair == 'GBPCAD':
                return False
            elif pair == 'GBPAUD':
                return False
            elif pair == 'EURJPY':
                return False
            elif pair == 'AUDCAD':
                return False
            elif pair == 'EURAUD':
                return False
            elif pair == 'AUDJPY':
                return False
            elif pair == 'CADJPY':
                return True
            elif pair == 'EURCAD':
                return True


def check_cross(data, ema2):
    list_cross = []
    for i, row in data.iterrows():
        if i > ema2:
            if row['Open'] > row['Close']:
                if row['Close'] < row['EMA'] < row['Open'] and row['Close'] < row['EMA2'] < row['Open']:
                    list_cross.append(True)
                else:
                    list_cross.append(False)
            else:
                if row['Open'] < row['EMA'] < row['Close'] and row['Open'] < row['EMA2'] < row['Close']:
                    list_cross.append(True)
                else:
                    list_cross.append(False)
    return list_cross


def calculate_ema2_xcandle_multiprocessing(params):
    pair = params[0][0]
    smoothing = params[0][1]
    ema1_test = params[0][2]
    ema2_test = params[0][3]
    data = params[0][4]
    candle = params[1]
    boolean = params[2]
    result = ema2_xcandle(pair, data, ema2_test, candle, boolean)
    return ([[smoothing, ema1_test, ema2_test, candle, boolean], result[2].sum(), (result[2] > 0).sum(), (result[2] < 0).sum(),
             ((result[2] > 0).sum() - (result[2] < 0).sum()), result[2].max(), result[2].min()])


def fint_best_combine_multiprocessing(pair, data):
    pool = multiprocessing.Pool(processes=4)

    smooth_loop = range(5, 20, 5)
    ema1_loop = range(20, 100, 10)
    ema2_loop = range(30, 100, 10)
    param = list(itertools.product(smooth_loop, ema1_loop, ema2_loop))
    param_final = [(pair, data, param) for param in map(list, param)]
    listema = pool.map(ema.calculate_double_ema_multiprocessing, param_final)

    xcandle_loop = range(3, 30)
    boolean_loop = [True, False]
    param_final = list(itertools.product(listema, xcandle_loop, boolean_loop))
    data_test1 = pool.map(calculate_ema2_xcandle_multiprocessing, param_final)

    data = pd.DataFrame(data_test1)
    data = data.rename(columns={0: 'Combine', 1: 'Pips', 2: 'Profit', 3: 'Loss', 4: 'Diff', 5: 'Max', 6: 'Min'})
    return data


def fint_best_combine(pair, data):
    listtest = []

    for s in range(3, 20):
        for i in range(20, 200, 10):
            for j in range(30, 200, 10):
                data['EMA'] = ema.calculate_ema(data['Open'], i, s)
                data['EMA2'] = ema.calculate_ema(data['Open'], j, s)
                for k in range(3, 30):
                    temp1 = ema2_xcandle(pair, data, j, k, True)
                    listtest.append([[s, i, j, k, True], temp1[2].sum(), (temp1[2] > 0).sum(), (temp1[2] < 0).sum(),
                                     ((temp1[2] > 0).sum()-(temp1[2] < 0).sum()), temp1[2].max(), temp1[2].min()])
                    temp2 = ema2_xcandle(pair, data, j, k, False)
                    listtest.append([[s, i, j, k, False], temp2[2].sum(), (temp2[2] > 0).sum(), (temp2[2] < 0).sum(),
                                     ((temp2[2] > 0).sum()-(temp2[2] < 0).sum()), temp2[2].max(), temp2[2].min()])

    data = pd.DataFrame(listtest)
    data = data.rename(columns={0: 'Combine', 1: 'Pips', 2: 'Profit', 3: 'Loss', 4: 'Diff', 5: 'Max', 6: 'Min'})
    return data


def sendnotify(notify, type_trade, pair, price):
    ref = db.reference(notify)
    current_time_ms = round(time.time() * 1000)
    messages = type_trade.capitalize() + ' ' + pair + ' at ' + str(price) + ', strategi : ema2_xcandle'
    print(messages)
    ref.child(str(current_time_ms)).set({
        'messages': messages
    })
    send_notif("test", pair, messages)


def ema2_xcandle(pair, data, ema2, max_candle=3, reversal=True, notify=''):
    listtest = []
    candle = 0
    startprice = 0
    type_trade = ''  # buy or sell
    starttime = ''
    for i, row in data.iterrows():
        if i > ema2:
            if candle == 0:
                if row['Open'] > row['Close']:
                    if row['Close'] < row['EMA'] < row['Open'] and row['Close'] < row['EMA2'] < row['Open']:
                        starttime = row['Time']
                        startprice = row['Close']
                        type_trade = 'sell'
                        candle += 1

                        if notify != '':
                            if i == (data.index.stop - 1):
                                sendnotify(notify, type_trade, pair, startprice)
                else:
                    if row['Open'] < row['EMA'] < row['Close'] and row['Open'] < row['EMA2'] < row['Close']:
                        starttime = row['Time']
                        startprice = row['Close']
                        type_trade = 'buy'
                        candle += 1

                        if notify != '':
                            if i == (data.index.stop - 1):
                                sendnotify(notify, type_trade, pair, startprice)

            else:
                # validating if next candle is reversal
                if reversal:
                    if candle == 1:
                        if type_trade == 'buy':
                            if startprice > row['Close']:
                                candle = max_candle
                        else:
                            if startprice < row['Close']:
                                candle = max_candle

                # check if finish
                if candle <= max_candle:
                    candle += 1
                else:
                    closeprice = row['Close']
                    if type_trade == 'buy':
                        profit = (closeprice - startprice)
                    else:
                        profit = (startprice - closeprice)

                    d_value = pair_decimal.get_pair_decimal(pair)
                    decimal_multiplier = pow(10, d_value)
                    profit = profit * decimal_multiplier
                    listtest.append([starttime, row['Time'], int(profit)])
                    candle = 0

                    if notify != '':
                        if i == (data.index.stop - 1):
                            sendnotify(notify, 'Close', pair, closeprice)

    return pd.DataFrame(listtest)
