from datetime import datetime
import firebase_admin
import requests
from firebase_admin import credentials
from firebase_admin import db


def get_volume(pair, multiplier, timespan):
    if timespan == 'h':
        if multiplier == '1':
            if pair == 'AUDUSD':
                return {
                    '1663714800000': 1210,
                    '1663718400000': 3303,
                    '1663722000000': 3803,
                    '1663725600000': 2932,
                    '1663729200000': 2157,
                    '1663732800000': 2244
                }
            elif pair == 'EURUSD':
                return {
                    '1663714800000': 1612,
                    '1663718400000': 3677,
                    '1663722000000': 3433,
                    '1663725600000': 2355,
                    '1663729200000': 2092,
                    '1663732800000': 2132
                }
            elif pair == 'GBPUSD':
                return {
                    '1663714800000': 2544,
                    '1663718400000': 6280,
                    '1663722000000': 6951,
                    '1663725600000': 4303,
                    '1663729200000': 4766,
                    '1663732800000': 4202
                }
            elif pair == 'USDCAD':
                return {
                    '1663714800000': 2516,
                    '1663718400000': 4527,
                    '1663722000000': 4134,
                    '1663725600000': 3459,
                    '1663729200000': 2077,
                    '1663732800000': 2296
                }
            elif pair == 'USDJPY':
                return {
                    '1663714800000': 3803,
                    '1663718400000': 9316,
                    '1663722000000': 7882,
                    '1663725600000': 4850,
                    '1663729200000': 4248,
                    '1663732800000': 4913
                }
            elif pair == 'XAUUSD':
                return {
                    '1663714800000': 970,
                    '1663718400000': 2174,
                    '1663722000000': 3275,
                    '1663725600000': 2519,
                    '1663729200000': 2218,
                    '1663732800000': 1556
                }
            elif pair == 'GBPJPY':
                return {
                    '1663714800000': 4287,
                    '1663718400000': 9152,
                    '1663722000000': 8908,
                    '1663725600000': 5114,
                    '1663729200000': 5364,
                    '1663732800000': 5149
                }
            elif pair == 'EURGBP':
                return {
                    '1663714800000': 2309,
                    '1663718400000': 3166,
                    '1663722000000': 3794,
                    '1663725600000': 2190,
                    '1663729200000': 2121,
                    '1663732800000': 1677
                }
            elif pair == 'GBPCAD':
                return {
                    '1663686000000': 10187,
                    '1663689600000': 7469,
                    '1663693200000': 8856,
                    '1663696800000': 7766,
                    '1663700400000': 6041,
                    '1663704000000': 2864,
                    '1663707600000': 4013,
                    '1663711200000': 2221,
                    '1663714800000': 2616,
                    '1663718400000': 4643,
                    '1663722000000': 4644,
                    '1663725600000': 4322,
                    '1663729200000': 3419,
                    '1663732800000': 2817
                }
            elif pair == 'GBPAUD':
                return {
                    '1663686000000': 6368,
                    '1663689600000': 4456,
                    '1663693200000': 6457,
                    '1663696800000': 6100,
                    '1663700400000': 5565,
                    '1663704000000': 1597,
                    '1663707600000': 4753,
                    '1663711200000': 1946,
                    '1663714800000': 1982,
                    '1663718400000': 4833,
                    '1663722000000': 5139,
                    '1663725600000': 3976,
                    '1663729200000': 3728,
                    '1663732800000': 3691
                }
            elif pair == 'EURJPY':
                return {
                    '1663686000000': 9023,
                    '1663689600000': 7486,
                    '1663693200000': 7996,
                    '1663696800000': 8069,
                    '1663700400000': 7223,
                    '1663704000000': 3331,
                    '1663707600000': 10453,
                    '1663711200000': 3189,
                    '1663714800000': 5966,
                    '1663718400000': 9342,
                    '1663722000000': 9178,
                    '1663725600000': 7014,
                    '1663729200000': 6900,
                    '1663732800000': 6374
                }
            elif pair == 'AUDCAD':
                return {
                    '1663686000000': 4341,
                    '1663689600000': 2834,
                    '1663693200000': 3746,
                    '1663696800000': 3531,
                    '1663700400000': 3047,
                    '1663704000000': 1224,
                    '1663707600000': 424,
                    '1663711200000': 901,
                    '1663714800000': 1120,
                    '1663718400000': 3043,
                    '1663722000000': 2945,
                    '1663725600000': 2356,
                    '1663729200000': 1796,
                    '1663732800000': 1665
                }
            elif pair == 'EURAUD':
                return {
                    '1663686000000': 10132,
                    '1663689600000': 6893,
                    '1663693200000': 7266,
                    '1663696800000': 7075,
                    '1663700400000': 7054,
                    '1663704000000': 2713,
                    '1663707600000': 5642,
                    '1663711200000': 2208,
                    '1663714800000': 3149,
                    '1663718400000': 7166,
                    '1663722000000': 7555,
                    '1663725600000': 5237,
                    '1663729200000': 4636,
                    '1663732800000': 4612
                }
            elif pair == 'AUDJPY':
                return {
                    '1663686000000': 7334,
                    '1663689600000': 4856,
                    '1663693200000': 5598,
                    '1663696800000': 5793,
                    '1663700400000': 4912,
                    '1663704000000': 2563,
                    '1663707600000': 2438,
                    '1663711200000': 2951,
                    '1663714800000': 2933,
                    '1663718400000': 9310,
                    '1663722000000': 8634,
                    '1663725600000': 5024,
                    '1663729200000': 4669,
                    '1663732800000': 4807
                }
            elif pair == 'CADJPY':
                return {
                    '1663686000000': 4910,
                    '1663689600000': 2976,
                    '1663693200000': 4147,
                    '1663696800000': 3369,
                    '1663700400000': 2639,
                    '1663704000000': 2213,
                    '1663707600000': 2159,
                    '1663711200000': 2075,
                    '1663714800000': 2073,
                    '1663718400000': 6227,
                    '1663722000000': 5235,
                    '1663725600000': 2994,
                    '1663729200000': 2086,
                    '1663732800000': 2506
                }
            elif pair == 'EURCAD':
                return {
                    '1663686000000': 6970,
                    '1663689600000': 4275,
                    '1663693200000': 5323,
                    '1663696800000': 5147,
                    '1663700400000': 4533,
                    '1663704000000': 2040,
                    '1663707600000': 3179,
                    '1663711200000': 1208,
                    '1663714800000': 1260,
                    '1663718400000': 3698,
                    '1663722000000': 3292,
                    '1663725600000': 2804,
                    '1663729200000': 1871,
                    '1663732800000': 2259
                }


if __name__ == '__main__':
    reference = '/' + 'EURCAD' + '_' + '1' + 'hour'
    currency = 'EUR/CAD'
    multiplier = '1'
    # min, h, day, week, month
    timespan = 'h'
    # My Timezone is +7 and API Timezone is +9 so the different is +2
    timezone = 2 * 3600000
    start_time = int(datetime.strptime('2022-09-20 22:00:00', '%Y-%m-%d %H:%M:%S').timestamp() * 1000) + timezone
    end_time = int(datetime.strptime('2022-09-21 12:00:00', '%Y-%m-%d %H:%M:%S').timestamp() * 1000) + timezone
    # use this if daily
    # start_date = '2022-09-01'
    # end_date = '2022-09-12'
    apikey = 'e120fbaf7bf44c358a6b228edbbc62f4'

    url = 'https://api.twelvedata.com/time_series?symbol=' + currency + '&interval=' + multiplier + timespan + \
          '&outputsize=24&apikey=' + apikey

    response = requests.get(url).json()

    json_file = response['values']

    cred = credentials.Certificate("key/firebase_admin.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://forex-bd746-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })
    ref = db.reference(reference)

    currency = currency.replace('/','')
    volume = get_volume(currency, multiplier, timespan)
    dataForex = {}
    for i in json_file:
        current_time = int(datetime.strptime(i['datetime'], '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
        if start_time < current_time <= end_time:
            current_time = (current_time - timezone) - 3600000
            data = {
                'o': float(i['open']),
                'h': float(i['high']),
                'l': float(i['low']),
                'c': float(i['close']),
                'v': volume.get(str(current_time))
            }
            ref.child(str(current_time)).set(data)
            # print(str(current_time) + ': ' + str(data))

