import pandas as pd
from bokeh.models import HoverTool
from bokeh.plotting import figure
from math import pi


def volume_chart(data, source, inc, dec, width, height, x_min, x_max):
    tools = "xpan,xwheel_zoom,crosshair"
    p2 = figure(x_axis_type="datetime", tools=tools, width=width, height=height, sizing_mode='stretch_width',
                x_range=(x_min, x_max), y_range=(data.Volume.min(), data.Volume.max()))
    p2.background_fill_color = '#F5F5F5'
    p2.xgrid.grid_line_color = None
    p2.ygrid.grid_line_color = None
    # p2.xaxis.major_label_orientation = pi / 4
    # map dataframe indices to date strings and use as label overrides
    p2.xaxis.major_label_overrides = {
        i: date.strftime('%d/%m %H:%M') for i, date in enumerate(pd.to_datetime(data["Time"]))
    }
    p2.vbar(source=source, view=inc, x='index', width=0.5, top='Volume', bottom=0,
            fill_color="#FF2C2C", line_color="#FF2C2C")
    p2.vbar(source=source, view=dec, x='index', width=0.5, top='Volume', bottom=0,
            fill_color="#1FD655", line_color="#1FD655")

    hover = HoverTool(
        tooltips=[
            ('Time', '@Time{%Y-%m-%d %H:%M:%S}'),
            ('Volume', '@Volume{0}'),
            ('VW', '@VolumeWeight{0.00000}'),
        ],
        formatters={
            '@Time': 'datetime'
        },
        mode='mouse'
    )
    p2.add_tools(hover)
    return p2
