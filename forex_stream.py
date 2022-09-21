from datetime import datetime
import firebase_admin
import requests
from firebase_admin import credentials
from firebase_admin import db

if __name__ == '__main__':
    currency = 'EURCAD'
    multiplier = '1'
    # minute, hour, day, week, month, quarter, year
    timespan = 'hour'
    timezone = 7 * 3600000
    start_date = int(datetime.strptime('2022-09-01 00:00:00', '%Y-%m-%d %H:%M:%S').timestamp() * 1000) + timezone
    end_date = int(datetime.strptime('2022-09-30 23:00:00', '%Y-%m-%d %H:%M:%S').timestamp() * 1000) + timezone
    # use this if daily
    # start_date = '2022-09-01'
    # end_date = '2022-09-12'
    apikey = 'E95doEHvuPooHVl29ku9RbtfqRDfLFQl'

    url = 'https://api.polygon.io/v2/aggs/ticker/C:' + currency + '/range/' + multiplier + '/' + timespan + \
          '/' + str(start_date) + '/' + str(end_date) + '?&sort=asc&limit=50000&apiKey=' + apikey

    response = requests.get(url).json()

    json_file = response['results']

    cred = credentials.Certificate("key/firebase_admin.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://forex-bd746-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

    reference = '/' + currency + '_' + multiplier + timespan
    ref = db.reference(reference)

    dataForex = {}
    for i in json_file:
        time = i['t']
        i.pop('t')
        ref.child(str(time)).set(i)
