"""
Major 1 trend - 10-25 years avg.
Major 2 trend - 5-10 years avg.
Primary trend - 2-3 years avg.
Intermediate trend - 5-12 months avg.
Minor trend - 4-12 weeks avg.
"""
from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart
from machine_learning_stuff.linear_regression import backward_linear_regression
from utils.download_stock_csvs import download_stock_day
import pandas as pd
import numpy as np

ticker = 'AMD'
df = pd.read_csv(download_stock_day(ticker)).reset_index()
df['Datetime'] = pd.to_datetime(df['Date'])
df['epoch'] = df['Datetime'].apply(lambda x: x.timestamp())
idx = len(df)-252

fig = candlestick_chart_fig(df, ticker)
# Major
periods = [x*252 for x in [5, 10, 15, 20, 25]]
for period in periods:
    if len(df) > period:
        roc, coef, intercept, score = backward_linear_regression(df, 'Close', idx, period)
        df[f'{int(period/252)}y major trend'] = df[idx-period:idx]['epoch']*coef + intercept
        fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'{int(period/252)}y major trend'], f'{int(period/252)}y major trend')

# Primary
periods = [x*252 for x in [1, 2, 3]]
for period in periods:
    if len(df) > period:
        roc, coef, intercept, score = backward_linear_regression(df, 'Close', idx, period)
        df[f'{int(period/252)}y primary trend'] = df[idx-period:idx]['epoch']*coef + intercept
        fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'{int(period/252)}y primary trend'], f'{int(period/252)}y primary trend')

# Intermediate
periods = [x*21 for x in [5, 9, 12]]
for period in periods:
    if len(df) > period:
        roc, coef, intercept, score = backward_linear_regression(df, 'Close', idx, period)
        df[f'{int(period/21)}m intermediate trend'] = df[idx-period:idx]['epoch']*coef + intercept
        fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'{int(period/21)}m intermediate trend'], f'{int(period/21)}m intermediate trend')

# Minor
periods = [x*5 for x in [4, 8, 12]]
for period in periods:
    if len(df) > period:
        roc, coef, intercept, score = backward_linear_regression(df, 'Close', idx, period)
        df[f'{int(period/5)}w minor trend'] = df[idx-period:idx]['epoch']*coef + intercept
        fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'{int(period/5)}w minor trend'], f'{int(period/5)}w minor trend')

fig.show()