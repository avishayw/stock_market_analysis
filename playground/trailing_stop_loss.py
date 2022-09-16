from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart
from utils.download_stock_csvs import download_stock_day
import pandas as pd
import numpy as np

ticker = 'ALGN'

df = pd.read_csv(download_stock_day(ticker))[-2016:].reset_index()

period = 50

df[f'min{period}'] = df['Close'].rolling(period).min()
df[f'max{period}'] = df['Close'].rolling(period).max()

fig = candlestick_chart_fig(df, ticker)
fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'min{period}'], f'min{period}')
fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'max{period}'], f'max{period}')

fig.show()
