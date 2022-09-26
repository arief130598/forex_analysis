import itertools
import multiprocessing
from datetime import datetime
from math import pi
from multiprocessing import Queue, Process

import pandas as pd

from bokeh.layouts import column
from bokeh.models import HoverTool, CDSView, ColumnDataSource, BooleanFilter, LinearAxis, Range1d
from bokeh.plotting import figure, show

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from indicator import ema, stochastic_oscilator, bollinger_band
from strategi import ema_xcandle, ema2_xcandle, ema_xvolume
from indicator_bokeh import volume_chart, ema_chart, bollinger_band_chart, stochastic_oscilator_chart

if __name__ == '__main__':
    pair = 'EURCAD'
    multiplier = '1'
    # minute, hour, day, week, month, quarter, year
    timespan = 'hour'
    timezone = 7 * 3600000
    start_date = int(datetime.strptime('2022-01-01 00:00:00', '%Y-%m-%d %H:%M:%S').timestamp() * 1000) + timezone
    end_date = int(datetime.strptime('2022-09-30 23:00:00', '%Y-%m-%d %H:%M:%S').timestamp() * 1000) + timezone

    cred = credentials.Certificate("key/firebase_admin.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://forex-bd746-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

    reference = '/' + pair + '_' + multiplier + timespan
    ref = db.reference(reference)
    data = ref.order_by_key().start_at(str(start_date)).end_at(str(end_date)).get()
    df = pd.DataFrame(data).T
    df.reset_index(inplace=True)
    df = df.rename(columns={'index': 'Time'})
    df.rename(columns={'o': 'Open', 'c': 'Close', 'h': 'High', 'l': 'Low', 'n': 'Transaction', 'v': 'Volume',
                       'vw': 'VolumeWeight'}, inplace=True)
    df['Time'] = df['Time'].astype('int64')
    df['Time'] = df['Time'] + timezone  # Change Timezone
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')

    # find combination test
    data_test1 = ema_xcandle.fint_best_combine_multiprocessing(pair, df)
    data_test1 = data_test1.sort_values(by=['Pips'])
    data_test1.to_csv('test_data' + reference + '_ema_xcandle.csv', index=False, header=True, sep=';')

    data_test2 = ema2_xcandle.fint_best_combine_multiprocessing(pair, df)
    data_test2 = data_test2.sort_values(by=['Pips'])
    data_test2.to_csv('test_data' + reference + '_ema2_xcandle.csv', index=False, header=True, sep=';')

    # data_test3 = ema_xvolume.fint_best_combine_multiprocessing(pair, df)
    # data_test3 = data_test3.sort_values(by=['Pips'])
    # data_test3.to_csv('test_data' + reference + '_ema_xvolume.csv', index=False, header=True, sep=';')

    # EMA
    df['EMA'] = ema.calculate_ema(df['Open'], 30, 15)
    df['EMA2'] = ema.calculate_ema(df['Open'], 60, 15)
    #
    # # Bollinger Band
    data_band = bollinger_band.get_bollinger_bands(df['Close'], 30, 30)
    df['Band_Up'] = data_band['Up']
    df['Band_Mid'] = data_band['Mid']
    df['Band_Down'] = data_band['Down']
    #
    # # Stoch Oscilator
    data_stoch = stochastic_oscilator.calculate_stoch(df, 30, 10)
    df['K'] = data_stoch['%K']
    df['D'] = data_stoch['%D']

    # Calculate Result
    # testema = ema_xcandle.ema_xcandle(pair, df, 30,
    #                                   ema_xcandle.get_best_xcandle(pair, multiplier, timespan),
    #                                   ema_xvolume.get_reversal(pair, multiplier, timespan))
    # testema2 = ema2_xcandle.ema2_xcandle(pair, df, 60,
    #                                      ema_xcandle.get_best_xcandle(pair, multiplier, timespan),
    #                                      ema_xvolume.get_reversal(pair, multiplier, timespan))
    # testemavolume = ema_xvolume.emaclose_xvolume(pair, df, 60,
    #                                              ema_xvolume.get_best_min_ema(pair, multiplier, timespan),
    #                                              ema_xvolume.get_best_volumestart(pair, multiplier, timespan),
    #                                              ema_xvolume.get_best_volumeend(pair, multiplier, timespan),
    #                                              ema_xvolume.get_reversal(pair, multiplier, timespan))

    source = ColumnDataSource(data=df)

    # Create Candlestick Chart
    inc_b = source.data['Open'] > source.data['Close']
    inc = CDSView(source=source, filters=[BooleanFilter(inc_b)])
    dec_b = source.data['Close'] > source.data['Open']
    dec = CDSView(source=source, filters=[BooleanFilter(dec_b)])

    start_time = '2022-09-02 00:00:00'
    end_time = '2022-09-14 23:00:00'
    df_range = df.loc[(df['Time'] > start_time) & (df['Time'] <= end_time)]
    y_max = df_range['High'].max()
    y_min = df_range['Low'].min()
    x_min = df.loc[df['Time'] == start_time].index[0]
    x_max = df.loc[df['Time'] == end_time].index[0]

    TOOLS = "pan,wheel_zoom,xwheel_zoom,ywheel_zoom,box_zoom,crosshair"
    p = figure(x_axis_type="datetime", tools=TOOLS, width=1400, height=500, sizing_mode='scale_both', title=pair,
               x_range=(x_min, x_max), y_range=(y_min, y_max))
    p.background_fill_color = '#F5F5F5'
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    # p.yaxis.ticker = FixedTicker(ticks=list(np.arange(df['Low'].min(), df['High'].max(), 0.001)))
    p.xaxis.major_label_orientation = pi / 4
    # map dataframe indices to date strings and use as label overrides
    p.xaxis.major_label_overrides = {
        i: date.strftime('%d/%m %H:%M') for i, date in enumerate(pd.to_datetime(df["Time"]))
    }

    p_inc1 = p.vbar(source=source, view=inc, x='index', width=0.5, top='Open', bottom='Close',
                    fill_color="#FF2C2C", line_color="#FF2C2C")
    p_inc2 = p.vbar(source=source, view=inc, x='index', width=0.1, top='High', bottom='Low',
                    fill_color="#FF2C2C", line_color="#FF2C2C")
    p_dec1 = p.vbar(source=source, view=dec, x='index', width=0.5, top='Open', bottom='Close',
                    fill_color="#1FD655", line_color="#1FD655")
    p_dec2 = p.vbar(source=source, view=dec, x='index', width=0.1, top='High', bottom='Low',
                    fill_color="#1FD655", line_color="#1FD655")

    hover = HoverTool(
        renderers=[p_inc1, p_inc2, p_dec1, p_dec2],
        tooltips=[
            ('Time', '@Time{%Y-%m-%d %H:%M:%S}'),
            ('Open', '@Open{0.00000}'),
            ('High', '@High{0.00000}'),
            ('Low', '@Low{0.00000}'),
            ('Close', '@Close{0.00000}'),
            ('Volume', '@Volume{0}'),
            ('VW', '@VolumeWeight{0.00000}'),
        ],
        formatters={
            '@Time': 'datetime'
        },
        mode='mouse'
    )
    p.add_tools(hover)

    # Create EMA Line
    ema_chart.single_ema_chart(p, source)

    # Create Bollinger Band Line
    bollinger_band_chart.bollinger_band_chart(p, source)

    # Volume Chart
    p2 = volume_chart.volume_chart(df, source, inc, dec, 1400, 200, x_min, x_max)

    # Create Stoch Chart
    p3 = stochastic_oscilator_chart.stoch_chart(df, source, 1400, 200, x_min, x_max)

    show(column(p, p2, p3))
