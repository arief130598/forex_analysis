import pandas as pd
from bokeh.models import HoverTool
from bokeh.plotting import figure
from math import pi


def single_ema_chart(fig_ema, source):
    p_ema = fig_ema.line(source=source, x='index', y='EMA', line_width=1, color='orange')
    hover_ema = HoverTool(
        renderers=[p_ema],
        tooltips=[
            ('Time', '@Time{%Y-%m-%d %H:%M:%S}'),
            ('EMA', '@EMA{0.00000}'),
        ],
        formatters={
            '@Time': 'datetime'
        },
        mode='mouse'
    )
    fig_ema.add_tools(hover_ema)


def double_ema_chart(fig_ema, source):
    p_ema = fig_ema.line(source=source, x='index', y='EMA', line_width=1, color='blue')
    hover_ema = HoverTool(
        renderers=[p_ema],
        tooltips=[
            ('Time', '@Time{%Y-%m-%d %H:%M:%S}'),
            ('EMA', '@EMA{0.00000}'),
        ],
        formatters={
            '@Time': 'datetime'
        },
        mode='mouse'
    )
    fig_ema.add_tools(hover_ema)

    p_ema2 = fig_ema.line(source=source, x='index', y='EMA2', line_width=1, color='#59bfff')
    hover_ema = HoverTool(
        renderers=[p_ema2],
        tooltips=[
            ('Time', '@Time{%Y-%m-%d %H:%M:%S}'),
            ('EMA2', '@EMA2{0.00000}'),
        ],
        formatters={
            '@Time': 'datetime'
        },
        mode='mouse'
    )
    fig_ema.add_tools(hover_ema)
