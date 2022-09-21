from datetime import datetime
import firebase_admin
import pandas as pd
import requests
from firebase_admin import credentials
from firebase_admin import db

from indicator import ema as ema
from indicator import stochastic_oscilator as stoch

from strategi import ema_xcandle as emax
from strategi import ema2_xcandle as ema2
from strategi import ema_xvolume as emavolume


def get_volume(pair_data, multiplier_data, timespan_data):
    if timespan_data == 'h':
        if multiplier_data == '1':
            if pair_data == 'AUDUSD':
                return 7826
            elif pair_data == 'EURUSD':
                return 13207
            elif pair_data == 'GBPUSD':
                return 15498
            elif pair_data == 'USDCAD':
                return 8729
            elif pair_data == 'USDJPY':
                return 14991
            elif pair_data == 'XAUUSD':
                return 9652
            elif pair_data == 'GBPJPY':
                return 22234
            elif pair_data == 'EURGBP':
                return 10405


def call_api(currency):
    apikey = 'e120fbaf7bf44c358a6b228edbbc62f4'
    # My Timezone is +7 and API Timezone is +9 so the different is +3
    timezone_api = 3 * 3600000
    multiplier_api = '1'
    # min, h, day, week, month
    timespan_api = 'h'
    # minute, hour, day, week, month, quarter, year
    timespan_db = 'hour'

    url = 'https://api.twelvedata.com/time_series?symbol=' + currency + '&interval=' + multiplier_api + timespan_api + \
          '&outputsize=2&apikey=' + apikey
    response = requests.get(url).json()
    json_file = response['values'][1]

    reference = '/' + currency.replace('/', '') + '_' + str(multiplier_api) + timespan_db
    ref = db.reference(reference)

    current_time = int(datetime.strptime(json_file['datetime'], '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
    current_time = (current_time - timezone_api)
    data_db = {
        'o': float(json_file['open']),
        'h': float(json_file['high']),
        'l': float(json_file['low']),
        'c': float(json_file['close']),
        'v': get_volume(currency.replace('/', ''), multiplier_api, timespan_api)
    }
    ref.child(str(current_time)).set(data_db)

    data_temp = {
        'Time': datetime.fromtimestamp(current_time / 1000).strftime('%Y-%m-%d %H:%M:%S'),
        'Open': float(json_file['open']),
        'High': float(json_file['high']),
        'Low': float(json_file['low']),
        'Close': float(json_file['close']),
        'Volume': get_volume(currency.replace('/', ''), multiplier_api, timespan_api)
    }
    return data_temp


def read_data(reference):
    ref = db.reference(reference)
    data_temp = ref.order_by_key().start_at(str(start_date)).end_at(str(end_date)).get()
    df = pd.DataFrame(data_temp).T
    df.reset_index(inplace=True)
    df = df.rename(columns={'index': 'Time'})
    df.rename(columns={'o': 'Open', 'c': 'Close', 'h': 'High', 'l': 'Low', 'n': 'Transaction', 'v': 'Volume',
                       'vw': 'VolumeWeight'}, inplace=True)
    df['Time'] = df['Time'].astype('int64')
    df['Time'] = df['Time'] + timezone  # Change Timezone
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    return df


def calculate_data(pair):
    data = read_data('/' + pair + '_' + multiplier + timespan)
    notify_ref = '/' + pair + '_' + multiplier + timespan + '_Trade'
    data['EMA'] = ema.calculate_ema(data['Open'], 30, 15)
    data['EMA2'] = ema.calculate_ema(data['Open'], 60, 15)
    data1 = emax.ema_xcandle(pair, data, 30,
                             emax.get_best_xcandle(pair, multiplier, timespan),
                             emax.get_reversal(pair, multiplier, timespan),
                             notify_ref)
    data2 = ema2.ema2_xcandle(pair, data, 60,
                              ema2.get_best_xcandle(pair, multiplier, timespan),
                              ema2.get_reversal(pair, multiplier, timespan),
                              notify_ref)

    data3 = pd.DataFrame()
    # if pair != 'XAUUSD':
    # data3 = emavolume.emaclose_xvolume(pair, data, 60,
    #                                    emavolume.get_best_min_ema(pair, multiplier, timespan),
    #                                    emavolume.get_best_volumestart(pair, multiplier, timespan),
    #                                    emavolume.get_best_volumeend(pair, multiplier, timespan),
    #                                    emavolume.get_reversal(pair, multiplier, timespan),
    #                                    notify_ref)
    return [data1, data2, data3]


if __name__ == '__main__':
    cred = credentials.Certificate("key/firebase_admin.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://forex-bd746-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })
    multiplier = '1'
    timespan = 'hour'
    timezone = 7 * 3600000
    start_date = int(datetime.strptime('2022-01-01 00:00:00', '%Y-%m-%d %H:%M:%S').timestamp() * 1000) + timezone
    end_date = int(datetime.strptime('2022-09-30 23:00:00', '%Y-%m-%d %H:%M:%S').timestamp() * 1000) + timezone

    call_api('AUD/USD')
    data_audusd = calculate_data('AUDUSD')
    call_api('EUR/USD')
    data_eurusd = calculate_data('EURUSD')
    call_api('GBP/USD')
    data_gbpusd = calculate_data('GBPUSD')
    call_api('USD/CAD')
    data_usdcad = calculate_data('USDCAD')
    call_api('USD/JPY')
    data_usdjpy = calculate_data('USDJPY')
    call_api('XAU/USD')
    data_xauusd = calculate_data('XAUUSD')
    call_api('EUR/GBP')
    data_eurgbp = calculate_data('EURGBP')
    call_api('GBP/JPY')
    data_gbpjpy = calculate_data('GBPJPY')
