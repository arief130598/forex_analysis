import itertools
import multiprocessing

import pandas as pd
import time

from firebase_admin import db

from indicator import ema
from lib import pair_decimal as pair_decimal


def get_best_min_ema(pair, multiplier, timespan):
    if timespan == 'hour':
        if multiplier == '1':
            if pair == 'GBPUSD':
                return 55
            elif pair == 'USDJPY':
                return 70
            elif pair == 'AUDUSD':
                return 60
            elif pair == 'EURUSD':
                return 40
            elif pair == 'USDCAD':
                return 20
            elif pair == 'GBPJPY':
                return 20
            elif pair == 'EURGBP':
                return 20
            elif pair == 'GBPCAD':
                return 25
            elif pair == 'GBPAUD':
                return 20
            elif pair == 'EURJPY':
                return 50
            elif pair == 'AUDCAD':
                return 25
            elif pair == 'EURAUD':
                return 20
            elif pair == 'AUDJPY':
                return 40
            elif pair == 'CADJPY':
                return 20
            elif pair == 'EURCAD':
                return 25


def get_best_volumestart(pair, multiplier, timespan):
    if timespan == 'hour':
        if multiplier == '1':
            if pair == 'GBPUSD':
                return 2000
            elif pair == 'USDJPY':
                return 4000
            elif pair == 'AUDUSD':
                return 3000
            elif pair == 'EURUSD':
                return 4000
            elif pair == 'USDCAD':
                return 5000
            elif pair == 'GBPJPY':
                return 5000
            elif pair == 'EURGBP':
                return 13000
            elif pair == 'GBPCAD':
                return 12000
            elif pair == 'GBPAUD':
                return 8000
            elif pair == 'EURJPY':
                return 3000
            elif pair == 'AUDCAD':
                return 5000
            elif pair == 'EURAUD':
                return 9000
            elif pair == 'AUDJPY':
                return 8000
            elif pair == 'CADJPY':
                return 5000
            elif pair == 'EURCAD':
                return 9000


def get_best_volumeend(pair, multiplier, timespan):
    if timespan == 'hour':
        if multiplier == '1':
            if pair == 'GBPUSD':
                return 2000
            elif pair == 'USDJPY':
                return 8000
            elif pair == 'AUDUSD':
                return 2000
            elif pair == 'EURUSD':
                return 8000
            elif pair == 'USDCAD':
                return 3000
            elif pair == 'GBPJPY':
                return 5000
            elif pair == 'EURGBP':
                return 3000
            elif pair == 'GBPCAD':
                return 2000
            elif pair == 'GBPAUD':
                return 6000
            elif pair == 'EURJPY':
                return 3000
            elif pair == 'AUDCAD':
                return 5000
            elif pair == 'EURAUD':
                return 7000
            elif pair == 'AUDJPY':
                return 5000
            elif pair == 'CADJPY':
                return 8000
            elif pair == 'EURCAD':
                return 7000


def get_reversal(pair, multiplier, timespan):
    if timespan == 'hour':
        if multiplier == '1':
            if pair == 'GBPUSD':
                return False
            elif pair == 'USDJPY':
                return False
            elif pair == 'AUDUSD':
                return False
            elif pair == 'EURUSD':
                return False
            elif pair == 'USDCAD':
                return False
            elif pair == 'GBPJPY':
                return False
            elif pair == 'EURGBP':
                return False
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
                return True
            elif pair == 'CADJPY':
                return False
            elif pair == 'EURCAD':
                return False


def calculate_xvolume_multiprocessing(params):
    pair = params[0][0]
    ema_test = params[0][1]
    smoothing = params[0][2]
    data = params[0][3]
    min_ema = params[1]
    volume_start = params[2]
    volume_end = params[3]
    boolean = params[4]
    result = emaclose_xvolume(pair, data, ema_test, min_ema, volume_start, volume_end, boolean)
    return ([[ema_test, smoothing, min_ema, volume_start, volume_end, boolean], result[2].sum(), (result[2] > 0).sum(),
             (result[2] < 0).sum(), ((result[2] > 0).sum() - (result[2] < 0).sum()), result[2].max(), result[2].min()])


def fint_best_combine_multiprocessing(pair, data):
    pool = multiprocessing.Pool(processes=4)

    ema1_loop = range(20, 200, 10)
    smooth_loop = range(3, 20)
    param = list(itertools.product(ema1_loop, smooth_loop))
    param_final = [(pair, data, param) for param in map(list, param)]
    listema = pool.map(ema.calculate_ema_multiprocessing, param_final)

    min_ema_loop = range(20, 100, 5)
    volume_start_loop = range(2000, 14000, 1000)
    volume_end_loop = range(2000, 10000, 1000)
    boolean_loop = [True, False]
    param_final = list(itertools.product(listema, min_ema_loop, volume_start_loop, volume_end_loop, boolean_loop))
    data_test1 = pool.map(calculate_xvolume_multiprocessing, param_final)

    data = pd.DataFrame(data_test1)
    data = data.rename(columns={0: 'Combine', 1: 'Pips', 2: 'Profit', 3: 'Loss', 4: 'Diff', 5: 'Max', 6: 'Min'})
    return data


def fint_best_combine(pair, data, ema):
    listtest = []
    for i in range(20, 100, 5):
        for j in range(2000, 14000, 1000):
            for k in range(2000, 10000, 1000):
                temp1 = emaclose_xvolume(pair, data, ema, i, j, k, True)
                if temp1.empty:
                    pass
                else:
                    listtest.append([[i, j, k, True], temp1[2].sum(), (temp1[2] > 0).sum(), (temp1[2] < 0).sum(),
                                 ((temp1[2] > 0).sum() - (temp1[2] < 0).sum()), temp1[2].max(), temp1[2].min()])
                temp2 = emaclose_xvolume(pair, data, ema, i, j, k, False)
                if temp2.empty:
                    pass
                else:
                    listtest.append([[i, j, k, False], temp2[2].sum(), (temp2[2] > 0).sum(), (temp2[2] < 0).sum(),
                                     ((temp2[2] > 0).sum() - (temp2[2] < 0).sum()), temp2[2].max(), temp2[2].min()])

    data = pd.DataFrame(listtest)
    data = data.rename(columns={0: 'Combine', 1: 'Pips', 2: 'Profit', 3: 'Loss', 4: 'Diff', 5: 'Max', 6: 'Min'})
    return data


def sendnotify(notify, type_trade, pair, price):
    ref = db.reference(notify)
    current_time_ms = round(time.time() * 1000)
    messages = type_trade.capitalize() + ' ' + pair + ' at ' + str(price) + ', strategi : ema_xvolume'
    print(messages)
    ref.child(str(current_time_ms)).set({
        'messages': messages
    })


def emaclose_xvolume(pair, data, ema, min_ema_diff, volumestart, volumeend, reversal=True, notify=''):
    listtest = []
    candle = 0
    startprice = 0
    closeprice = 0
    type_trade = ''  # buy or sell
    starttime = ''
    d_value = pair_decimal.get_pair_decimal(pair)
    decimal_multiplier = pow(10, d_value)

    for i, row in data.iterrows():
        if i > ema:
            if type_trade == '':
                if row['Volume'] >= volumestart:
                    ema_diff = row['Close'] - row['EMA']
                    if ema_diff < 0:
                        ema_diff = ema_diff * -1

                    ema_diff = ema_diff * decimal_multiplier
                    if ema_diff >= min_ema_diff:
                        if row['Open'] > row['Close']:
                            starttime = row['Time']
                            startprice = row['Close']
                            type_trade = 'sell'
                            candle += 1

                            if notify != '':
                                if i == (data.index.stop - 1):
                                    sendnotify(notify, type_trade, pair, startprice)
                        else:
                            starttime = row['Time']
                            startprice = row['Close']
                            type_trade = 'buy'
                            candle += 1

                            if notify != '':
                                if i == (data.index.stop - 1):
                                    sendnotify(notify, type_trade, pair, startprice)
            else:
                if row['Volume'] <= volumeend:
                    closeprice = row['Close']
                    if type_trade == 'buy':
                        profit = (closeprice - startprice)
                    else:
                        profit = (startprice - closeprice)

                    profit = profit * decimal_multiplier
                    listtest.append([starttime, row['Time'], int(profit)])
                    type_trade = ''

                    if notify != '':
                        if i == (data.index.stop - 1):
                            sendnotify(notify, 'Close', pair, closeprice)
                else:
                    if reversal:
                        if type_trade == 'sell':
                            if row['Close'] > startprice:
                                closeprice = row['Close']
                                if type_trade == 'buy':
                                    profit = (closeprice - startprice)
                                else:
                                    profit = (startprice - closeprice)

                                profit = profit * decimal_multiplier
                                listtest.append([starttime, row['Time'], int(profit)])
                                type_trade = ''

                                if notify != '':
                                    if i == (data.index.stop - 1):
                                        sendnotify(notify, 'Close', pair, closeprice)
                        else:
                            if row['Close'] < startprice:
                                closeprice = row['Close']
                                if type_trade == 'buy':
                                    profit = (closeprice - startprice)
                                else:
                                    profit = (startprice - closeprice)

                                profit = profit * decimal_multiplier
                                listtest.append([starttime, row['Time'], int(profit)])
                                type_trade = ''

                                if notify != '':
                                    if i == (data.index.stop - 1):
                                        sendnotify(notify, 'Close', pair, closeprice)
    return pd.DataFrame(listtest)
