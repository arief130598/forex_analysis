import itertools
import multiprocessing
import time
from multiprocessing import Process, Queue

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
                return 27
            elif pair == 'GBPUSD':
                return 14
            elif pair == 'USDCAD':
                return 24
            elif pair == 'USDJPY':
                return 25
            elif pair == 'XAUUSD':
                return 28
            elif pair == 'GBPJPY':
                return 28
            elif pair == 'EURGBP':
                return 15
            elif pair == 'GBPCAD':
                return 16
            elif pair == 'GBPAUD':
                return 29
            elif pair == 'EURJPY':
                return 27
            elif pair == 'AUDCAD':
                return 28
            elif pair == 'EURAUD':
                return 24
            elif pair == 'AUDJPY':
                return 18
            elif pair == 'CADJPY':
                return 28
            elif pair == 'EURCAD':
                return 12


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
                return True
            elif pair == 'XAUUSD':
                return False
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
                return True
            elif pair == 'AUDJPY':
                return False
            elif pair == 'CADJPY':
                return True
            elif pair == 'EURCAD':
                return False


def calculate_xcandle_multiprocessing(params):
    pair = params[0][0]
    ema_test = params[0][1]
    smoothing = params[0][2]
    data = params[0][3]
    candle = params[1]
    boolean = params[2]
    result = ema_xcandle(pair, data, ema_test, candle, boolean)
    return ([[ema_test, smoothing, candle, boolean], result[2].sum(), (result[2] > 0).sum(), (result[2] < 0).sum(),
             ((result[2] > 0).sum() - (result[2] < 0).sum()), result[2].max(), result[2].min()])


def fint_best_combine_multiprocessing(pair, data):
    pool = multiprocessing.Pool(processes=4)

    ema1_loop = range(20, 200, 10)
    smooth_loop = range(3, 20)
    param = list(itertools.product(ema1_loop, smooth_loop))
    param_final = [(pair, data, param) for param in map(list, param)]
    listema = pool.map(ema.calculate_ema_multiprocessing, param_final)

    xcandle_loop = range(3, 30)
    boolean_loop = [True, False]
    param_final = list(itertools.product(listema, xcandle_loop, boolean_loop))
    data_test1 = pool.map(calculate_xcandle_multiprocessing, param_final)

    data = pd.DataFrame(data_test1)
    data = data.rename(columns={0: 'Combine', 1: 'Pips', 2: 'Profit', 3: 'Loss', 4: 'Diff', 5: 'Max', 6: 'Min'})
    return data


def fint_best_combine(pair, data):
    listtest = []
    for i in range(20, 200, 10):
        for j in range(3, 20):
            data['EMA'] = ema.calculate_ema(data['Open'], i, j)
            for k in range(3, 30):
                temp1 = ema_xcandle(pair, data, i, k, True)
                listtest.append([[i, j, k, True], temp1[2].sum(), (temp1[2] > 0).sum(), (temp1[2] < 0).sum(),
                                 ((temp1[2] > 0).sum() - (temp1[2] < 0).sum()), temp1[2].max(), temp1[2].min()])
                temp2 = ema_xcandle(pair, data, i, k, False)
                listtest.append([[i, j, k, False], temp2[2].sum(), (temp2[2] > 0).sum(), (temp2[2] < 0).sum(),
                                 ((temp2[2] > 0).sum() - (temp2[2] < 0).sum()), temp2[2].max(), temp2[2].min()])

    data = pd.DataFrame(listtest)
    data = data.rename(columns={0: 'Combine', 1: 'Pips', 2: 'Profit', 3: 'Loss', 4: 'Diff', 5: 'Max', 6: 'Min'})
    return data


def check_cross(data, ema):
    list_cross = []
    for i, row in data.iterrows():
        if i > ema:
            if row['Open'] > row['Close']:
                if row['Close'] < row['EMA'] < row['Open']:
                    list_cross.append(True)
                else:
                    list_cross.append(False)
            else:
                if row['Open'] < row['EMA'] < row['Close']:
                    list_cross.append(True)
                else:
                    list_cross.append(False)
    return list_cross


def sendnotify(notify, type_trade, pair, price):
    ref = db.reference(notify)
    current_time_ms = round(time.time() * 1000)
    messages = type_trade.capitalize() + ' ' + pair + ' at ' + str(price) + ', strategi : ema_xcandle'
    print(messages)
    ref.child(str(current_time_ms)).set({
        'messages': messages
    })
    send_notif("test", pair, messages)


def ema_xcandle(pair, data, ema, max_candle=3, reversal=True, notify=''):
    listtest = []
    candle = 0
    startprice = 0
    closeprice = 0
    type_trade = ''  # buy or sell
    starttime = ''
    for i, row in data.iterrows():
        if i > ema:
            if candle == 0:
                if row['Open'] > row['Close']:
                    if row['Close'] < row['EMA'] < row['Open']:
                        starttime = row['Time']
                        startprice = row['Close']
                        type_trade = 'sell'
                        candle += 1

                        if notify != '':
                            if i == (data.index.stop - 1):
                                sendnotify(notify, type_trade, pair, startprice)
                else:
                    if row['Open'] < row['EMA'] < row['Close']:
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


def ema_xcandle_stoch(pair, data, stoch, ema, max_candle=3, reversal=True):
    listtest = []
    candle = 0
    startprice = 0
    type_trade = ''  # buy or sell
    starttime = ''
    k = 0
    d = 0
    for i, row in data.iterrows():
        if i > ema:
            if candle == 0:
                if row['Open'] > row['Close']:
                    if row['Close'] < row['EMA'] < row['Open']:
                        if (80 <= stoch['%K'][i] <= stoch['%D'][i]) or (20 >= stoch['%K'][i] >= stoch['%D'][i]):
                            starttime = row['Time']
                            k = stoch['%K'][i]
                            d = stoch['%D'][i]
                            startprice = row['Close']
                            type_trade = 'sell'
                            candle += 1
                else:
                    if row['Open'] < row['EMA'] < row['Close']:
                        if (80 <= stoch['%K'][i] <= stoch['%D'][i]) or (20 >= stoch['%K'][i] >= stoch['%D'][i]):
                            starttime = row['Time']
                            k = stoch['%K'][i]
                            d = stoch['%D'][i]
                            startprice = row['Close']
                            type_trade = 'buy'
                            candle += 1
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
                    listtest.append([starttime, int(profit), k, d])
                    candle = 0
    return pd.DataFrame(listtest)
