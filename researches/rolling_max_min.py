from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart
from utils.download_stock_csvs import download_stock_day
from indicators.momentum_indicators import simple_moving_average
import pandas as pd

ticker = 'MTCH'

df = pd.read_csv(download_stock_day(ticker))

df = df[-2016:]
fig = candlestick_chart_fig(df)

periods = [3, 10, 20, 50, 100, 200]

for period in periods:
    df = simple_moving_average(df, period)
    fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'SMA{period}'], f'sma{period}')
    df[f'max{period}'] = df['High'].rolling(period).max()
    fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'max{period}'], f'max{period}')
    df[f'min{period}'] = df['Low'].rolling(period).min()
    fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'min{period}'], f'min{period}')

# period = 10
#
# for level in ['High', 'Close', 'Open', 'Low']:
#     df[f'max_{level.lower()}'] = df[level].rolling(period).max()
#     fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'max_{level.lower()}'], f'max_{level.lower()}')
#     df[f'min_{level.lower()}'] = df[level].rolling(period).min()
#     fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'min_{level.lower()}'], f'min_{level.lower()}')

fig.show()
