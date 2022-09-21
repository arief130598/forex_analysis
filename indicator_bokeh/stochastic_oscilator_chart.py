import pandas as pd
from bokeh.models import HoverTool
from bokeh.plotting import figure
from math import pi


def stoch_chart(data, source, width, height, x_min, x_max):
    tools = "xpan,xwheel_zoom,crosshair"
    p3 = figure(x_axis_type="datetime", tools=tools, width=width, height=height, sizing_mode='stretch_width',
                x_range=(x_min, x_max), y_range=(0, 100))
    p3.background_fill_color = '#F5F5F5'
    p3.xgrid.grid_line_color = None
    p3.ygrid.grid_line_color = None
    p3.xaxis.reverse()
    p3.xaxis.major_label_overrides = {
        i: date.strftime('%d/%m %H:%M') for i, date in enumerate(pd.to_datetime(data["Time"]))
    }
    p3.line(source=source, x='index', y=80, line_width=1, color='black', line_dash='dotted')
    p3.line(source=source, x='index', y=20, line_width=1, color='black', line_dash='dotted')
    k_line = p3.line(source=source, x='index', y='K', line_width=1, color='blue')
    d_line = p3.line(source=source, x='index', y='D', line_width=1, color='orange')

    hover = HoverTool(
        renderers=[k_line],
        tooltips=[
            ('Time', '@Time{%Y-%m-%d %H:%M:%S}'),
            ('K', '@K{0.00000}'),
        ],
        formatters={
            '@Time': 'datetime'
        },
        mode='mouse'
    )
    p3.add_tools(hover)
    hover = HoverTool(
        renderers=[d_line],
        tooltips=[
            ('Time', '@Time{%Y-%m-%d %H:%M:%S}'),
            ('D', '@D{0.00000}'),
        ],
        formatters={
            '@Time': 'datetime'
        },
        mode='mouse'
    )
    p3.add_tools(hover)
    return p3
