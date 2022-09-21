import pandas as pd
from bokeh.models import HoverTool
from bokeh.plotting import figure
from math import pi


def bollinger_band_chart(fig_band, source):
    p_mid = fig_band.line(source=source, x='index', y='Band_Mid', line_width=1, color='blue')
    hover_ema = HoverTool(
        renderers=[p_mid],
        tooltips=[
            ('Time', '@Time{%Y-%m-%d %H:%M:%S}'),
            ('Band_Mid', '@Band_Mid{0.00000}'),
        ],
        formatters={
            '@Time': 'datetime'
        },
        mode='mouse'
    )
    fig_band.add_tools(hover_ema)

    p_up = fig_band.line(source=source, x='index', y='Band_Up', line_width=1, color='#59bfff')
    hover_ema = HoverTool(
        renderers=[p_up],
        tooltips=[
            ('Time', '@Time{%Y-%m-%d %H:%M:%S}'),
            ('Band_Up', '@Band_Up{0.00000}'),
        ],
        formatters={
            '@Time': 'datetime'
        },
        mode='mouse'
    )
    fig_band.add_tools(hover_ema)

    p_down = fig_band.line(source=source, x='index', y='Band_Down', line_width=1, color='#59bfff')
    hover_ema = HoverTool(
        renderers=[p_down],
        tooltips=[
            ('Time', '@Time{%Y-%m-%d %H:%M:%S}'),
            ('Band_Down', '@Band_Down{0.00000}'),
        ],
        formatters={
            '@Time': 'datetime'
        },
        mode='mouse'
    )
    fig_band.add_tools(hover_ema)
