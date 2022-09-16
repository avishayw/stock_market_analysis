from indicators.volatility_indicators import average_true_range
from finta import TA
import ta
import numpy as np


def floor_trader_pivot(df):
    df['P'] = (df.shift(1)['High'] + df.shift(1)['Low'] + df.shift(1)['Close'])/3
    df['R1'] = 2*df['P'] - df.shift(1)['Low']
    df['S1'] = 2*df['P'] - df.shift(1)['High']
    df['R2'] = df['P'] + df['R1'] - df['S1']
    df['S2'] = df['P'] - df['R1'] + df['S1']
    # df['R3'] = df['P'] - df['R2'] + df['S2']
    # df['S3'] = df['P'] - df['R2'] + df['S2']
    df['R3'] = df['P'] + df['R2'] - df['S1']
    df['S3'] = df['P'] - df['R2'] + df['S1']
    return df


def chandalier_exit_close(df, period, multiplier): # TradingView
    df[f'{period} Highest Close'] = df['Close'].rolling(period).max()
    df[f'{period} Lowest Close'] = df['Close'].rolling(period).min()
    df = average_true_range(df, period)
    df['CE_Long'] = df[f'{period} Highest Close'] - df['ATR']*multiplier
    df['CE_Short'] = df[f'{period} Lowest Close'] + df['ATR']*multiplier
    df['CE_Short_pervious'] = df.shift(1)['CE_Short']
    df['CE_Long_pervious'] = df.shift(1)['CE_Long']
    df['CE_Long'] = np.where(df.shift(1)['Close'] > df['CE_Long_pervious'], df[['CE_Long', 'CE_Long_pervious']].max(axis=1), df['CE_Long']) #update
    df['CE_Short'] = np.where(df.shift(1)['Close'] < df['CE_Short_pervious'],df[['CE_Short', 'CE_Short_pervious']].min(axis=1), df['CE_Short']) #update
    df['CE_BUY'] = np.where((df['Close'] > df['CE_Short']) & (df['Close'].shift(1) <= df['CE_Short'].shift(1)), True, False)
    df['CE_SELL'] = np.where((df['Close'] < df['CE_Long']) & (df['Close'].shift(1) >= df['CE_Long'].shift(1)), True, False)
    # conditions = [df['Close'] > df['CE_Short_pervious'], df['Close'] < df['CE_Long_pervious']]
    # values = [1, -1]
    # df['signal'] = np.select(conditions, values, default=np.nan)
    # df['CE_BUY'] = np.where((df['signal'] == 1) & (df.shift(1)['signal'] == -1), True, False)
    # df['CE_SELL'] = np.where((df['signal'] == -1) & (df.shift(1)['signal'] == 1), True, False)
    df.drop(columns=['ATR', f'{period} Highest Close', f'{period} Lowest Close', 'CE_Short_pervious', 'CE_Long_pervious'], axis=1, inplace=True)
    return df


def chandalier_exit_highest_high_lowest_low(df, period, multiplier): #Github 'python-algorithmic-trading'
    df[f'{period} Highest High'] = df['High'].rolling(period).max()
    df[f'{period} Lowest Low'] = df['Low'].rolling(period).min()
    df = average_true_range(df, period)
    df['CE_Long'] = df[f'{period} Highest High'] - df[f'ATR{period}'] * multiplier
    df['CE_Short'] = df[f'{period} Lowest Low'] + df[f'ATR{period}'] * multiplier
    df['CE_Short_pervious'] = df.shift(1)['CE_Short']
    df['CE_Long_pervious'] = df.shift(1)['CE_Long']
    df['CE_Long'] = np.where(df.shift(1)['Close'] > df['CE_Long_pervious'],df[['CE_Long', 'CE_Long_pervious']].max(axis=1), df['CE_Long'])  # update
    df['CE_Short'] = np.where(df.shift(1)['Close'] < df['CE_Short_pervious'],df[['CE_Short', 'CE_Short_pervious']].min(axis=1), df['CE_Short'])  # update
    df['CE_BUY'] = np.where((df['Close'] > df['CE_Short']) & (df['Close'].shift(1) <= df['CE_Short'].shift(1)), True, False)
    df['CE_SELL'] = np.where((df['Close'] < df['CE_Long']) & (df['Close'].shift(1) >= df['CE_Long'].shift(1)), True, False)
    df.drop(columns=[f'ATR{period}', f'{period} Highest High', f'{period} Lowest Low', 'CE_Short_pervious', 'CE_Long_pervious'], axis=1, inplace=True)
    return df


def chandalier_exit_highest_high_lowest_high(df, period, multiplier): #Github 'python-algorithmic-trading'
    df[f'{period} Highest High'] = df['High'].rolling(period).max()
    df[f'{period} Lowest High'] = df['High'].rolling(period).min()
    df = average_true_range(df, period)
    df['CE_Long'] = df[f'{period} Highest High'] - df['ATR'] * multiplier
    df['CE_Short'] = df[f'{period} Lowest High'] + df['ATR'] * multiplier
    df['CE_Short_pervious'] = df.shift(1)['CE_Short']
    df['CE_Long_pervious'] = df.shift(1)['CE_Long']
    df['CE_Long'] = np.where(df.shift(1)['Close'] > df['CE_Long_pervious'],df[['CE_Long', 'CE_Long_pervious']].max(axis=1), df['CE_Long'])  # update
    df['CE_Short'] = np.where(df.shift(1)['Close'] < df['CE_Short_pervious'],df[['CE_Short', 'CE_Short_pervious']].min(axis=1), df['CE_Short'])  # update
    df['CE_BUY'] = np.where((df['Close'] > df['CE_Short']) & (df['Close'].shift(1) <= df['CE_Short'].shift(1)), True, False)
    df['CE_SELL'] = np.where((df['Close'] < df['CE_Long']) & (df['Close'].shift(1) >= df['CE_Long'].shift(1)), True, False)
    df.drop(columns=['ATR', f'{period} Highest High', f'{period} Lowest High', 'CE_Short_pervious', 'CE_Long_pervious'], axis=1, inplace=True)
    return df


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart
    from indicators.momentum_indicators import simple_moving_average, kama
    from indicators.trend_indicators import zero_lag_ema
    import pandas as pd
    import numpy as np
    from plotly.graph_objects import *


    ticker = 'KMX'
    df = pd.read_csv(download_stock_day(ticker))
    df = df[-500:]

    period = 1
    multiplier = 1.85

    df = chandalier_exit_highest_high_lowest_low(df, period, multiplier)

    stock_dict = df.reset_index().to_dict(orient='list')
    stock_dict.pop('index')
    stock_dict['x'] = stock_dict.pop('Date')

    trace1 = stock_dict.copy()
    trace1['type'] = 'candlestick'
    trace1.pop('Volume')
    trace1.pop('Dividends')
    trace1.pop('Stock Splits')
    trace1.pop('CE_BUY')
    trace1.pop('CE_SELL')
    trace1.pop('CE_Long')
    trace1.pop('CE_Short')
    trace1['xaxis'] = 'x1'
    trace1['yaxis'] = 'y1'
    trace1['high'] = trace1.pop('High')
    trace1['low'] = trace1.pop('Low')
    trace1['close'] = trace1.pop('Close')
    trace1['open'] = trace1.pop('Open')

    buy_df = df.loc[df['CE_BUY'] == True]
    stock_dict = buy_df.reset_index().to_dict(orient='list')
    stock_dict.pop('index')
    stock_dict['x'] = stock_dict.pop('Date')

    trace2 = stock_dict.copy()
    trace2.pop('Open')
    trace2.pop('Close')
    trace2.pop('High')
    trace2.pop('Low')
    trace2.pop('Volume')
    trace2.pop('Dividends')
    trace2.pop('Stock Splits')
    trace2.pop('CE_BUY')
    trace2.pop('CE_SELL')
    trace2.pop('CE_Short')
    trace2['name'] = 'BUY'
    trace2['mode'] = 'markers'
    trace2['type'] = 'scatter'
    trace2['y'] = trace2.pop('CE_Long')
    trace2['xaxis'] = 'x1'
    trace2['yaxis'] = 'y1'
    trace2['marker'] = {'size': 12, 'color': 'green'}

    sell_df = df.loc[df['CE_SELL'] == True]
    stock_dict = sell_df.reset_index().to_dict(orient='list')
    stock_dict.pop('index')
    stock_dict['x'] = stock_dict.pop('Date')

    trace3 = stock_dict.copy()
    trace3.pop('Open')
    trace3.pop('Close')
    trace3.pop('High')
    trace3.pop('Low')
    trace3.pop('Volume')
    trace3.pop('Dividends')
    trace3.pop('Stock Splits')
    trace3.pop('CE_BUY')
    trace3.pop('CE_SELL')
    trace3.pop('CE_Long')
    trace3['name'] = 'SELL'
    trace3['mode'] = 'markers'
    trace3['type'] = 'scatter'
    trace3['y'] = trace3.pop('CE_Short')
    trace3['xaxis'] = 'x1'
    trace3['yaxis'] = 'y1'
    trace3['marker'] = {'size': 12, 'color': 'red'}

    fast = 4
    medium = 6
    slow = 21

    df = simple_moving_average(df, fast)

    stock_dict = df.reset_index().to_dict(orient='list')
    stock_dict.pop('index')
    stock_dict['x'] = stock_dict.pop('Date')

    trace4 = stock_dict.copy()
    trace4.pop('Open')
    trace4.pop('Close')
    trace4.pop('High')
    trace4.pop('Low')
    trace4.pop('Volume')
    trace4.pop('Dividends')
    trace4.pop('Stock Splits')
    trace4.pop('CE_BUY')
    trace4.pop('CE_SELL')
    trace4.pop('CE_Long')
    trace4.pop('CE_Short')
    trace4['name'] = f'SMA{fast}'
    trace4['type'] = 'scatter'
    trace4['y'] = trace4.pop(f'SMA{fast}')
    trace4['xaxis'] = 'x1'
    trace4['yaxis'] = 'y1'
    trace4['marker'] = {'size': 5, 'color': 'yellow'}

    df = simple_moving_average(df, medium)

    stock_dict = df.reset_index().to_dict(orient='list')
    stock_dict.pop('index')
    stock_dict['x'] = stock_dict.pop('Date')

    trace5 = stock_dict.copy()
    trace5.pop('Open')
    trace5.pop('Close')
    trace5.pop('High')
    trace5.pop('Low')
    trace5.pop('Volume')
    trace5.pop('Dividends')
    trace5.pop('Stock Splits')
    trace5.pop('CE_BUY')
    trace5.pop('CE_SELL')
    trace5.pop('CE_Long')
    trace5.pop('CE_Short')
    trace5.pop(f'SMA{fast}')
    trace5['name'] = f'SMA{medium}'
    trace5['type'] = 'scatter'
    trace5['y'] = trace5.pop(f'SMA{medium}')
    trace5['xaxis'] = 'x1'
    trace5['yaxis'] = 'y1'
    trace5['marker'] = {'size': 5, 'color': 'blue'}

    df = simple_moving_average(df, slow)

    stock_dict = df.reset_index().to_dict(orient='list')
    stock_dict.pop('index')
    stock_dict['x'] = stock_dict.pop('Date')

    trace6 = stock_dict.copy()
    trace6.pop('Open')
    trace6.pop('Close')
    trace6.pop('High')
    trace6.pop('Low')
    trace6.pop('Volume')
    trace6.pop('Dividends')
    trace6.pop('Stock Splits')
    trace6.pop('CE_BUY')
    trace6.pop('CE_SELL')
    trace6.pop('CE_Long')
    trace6.pop('CE_Short')
    trace6.pop(f'SMA{fast}')
    trace6.pop(f'SMA{medium}')
    trace6['name'] = f'SMA{slow}'
    trace6['type'] = 'scatter'
    trace6['y'] = trace6.pop(f'SMA{slow}')
    trace6['xaxis'] = 'x1'
    trace6['yaxis'] = 'y1'
    trace6['marker'] = {'size': 5, 'color': 'purple'}

    zlema_period = 32
    df = zero_lag_ema(df, zlema_period)

    stock_dict = df.reset_index().to_dict(orient='list')
    stock_dict.pop('index')
    stock_dict['x'] = stock_dict.pop('Date')

    trace7 = stock_dict.copy()
    trace7.pop('Open')
    trace7.pop('Close')
    trace7.pop('High')
    trace7.pop('Low')
    trace7.pop('Volume')
    trace7.pop('Dividends')
    trace7.pop('Stock Splits')
    trace7.pop('CE_BUY')
    trace7.pop('CE_SELL')
    trace7.pop('CE_Long')
    trace7.pop('CE_Short')
    trace7.pop(f'SMA{fast}')
    trace7.pop(f'SMA{medium}')
    trace7.pop(f'SMA{slow}')
    trace7['name'] = f'ZLEMA{zlema_period}'
    trace7['type'] = 'scatter'
    trace7['y'] = trace7.pop(f'ZLEMA{zlema_period}')
    trace7['xaxis'] = 'x1'
    trace7['yaxis'] = 'y1'
    trace7['marker'] = {'size': 5, 'color': 'pink'}


    fig = Figure(data=[trace1, trace2, trace3, trace4, trace5, trace6, trace7])

    fig.show()

    # fig = candlestick_chart_fig(df)
    # fig = add_line_to_candlestick_chart(fig, df['Date'], df['BUY'])
    # fig = add_line_to_candlestick_chart(fig, df['Date'], df['SELL'])

    # fig.show()