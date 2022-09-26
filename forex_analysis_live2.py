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
            if pair_data == 'GBPCAD':
                return 14711
            elif pair_data == 'GBPAUD':
                return 15420
            elif pair_data == 'EURJPY':
                return 27798
            elif pair_data == 'AUDCAD':
                return 3585
            elif pair_data == 'EURAUD':
                return 17361
            elif pair_data == 'AUDJPY':
                return 21531
            elif pair_data == 'CADJPY':
                return 16984
            elif pair_data == 'EURCAD':
                return 9225


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
    ema_combine = ema.get_best_single_ema(pair, multiplier, timespan)
    data['EMA'] = ema.calculate_ema(data['Open'], ema_combine[0], ema_combine[1])
    data1 = emax.ema_xcandle(pair, data, ema_combine[0],
                             emax.get_best_xcandle(pair, multiplier, timespan),
                             emax.get_reversal(pair, multiplier, timespan),
                             notify_ref)

    ema_combine = ema.get_best_double_ema(pair, multiplier, timespan)
    data['EMA'] = ema.calculate_ema(data['Open'], ema_combine[1], ema_combine[0])
    data['EMA2'] = ema.calculate_ema(data['Open'], ema_combine[2], ema_combine[0])
    data2 = ema2.ema2_xcandle(pair, data, ema_combine[2],
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

    call_api('GBP/CAD')
    data_gbpcad = calculate_data('GBPCAD')
    call_api('GBP/AUD')
    data_gbpaud = calculate_data('GBPAUD')
    call_api('EUR/JPY')
    data_eurjpy = calculate_data('EURJPY')
    call_api('AUD/CAD')
    data_audcad = calculate_data('AUDCAD')
    call_api('EUR/AUD')
    data_euraud = calculate_data('EURAUD')
    call_api('AUD/JPY')
    data_audjpy = calculate_data('AUDJPY')
    call_api('CAD/JPY')
    data_cadjpy = calculate_data('CADJPY')
    call_api('EUR/CAD')
    data_eurcad = calculate_data('EURCAD')

