import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
from machine_learning_stuff.linear_regression import rolling_ols
from sklearn.preprocessing import MinMaxScaler


def percental_atr(df, period):
    df['A'] = ((df['High'] - df['Low'])/df['Low'])*100.0
    df['B'] = (((df['High'] - df.shift(1)['Close']).abs())/df['Close'])*100.0
    df['C'] = (((df['Low'] - df.shift(1)['Close']).abs())/df['Close'])*100.0
    df = df[1:-1]
    start_idx = df.index[0]
    df['TR'] = df[['A','B','C']].max(axis=1)
    # atr = np.zeros(len(df))
    df[f'%ATR{period}'] = np.nan
    # atr[period-1] = df['TR'][0:period].mean()
    df.loc[start_idx + period - 1, f'%ATR{period}'] = df['TR'][0:period].mean()
    for i in range(period, len(df)):
        df.loc[start_idx + i, f'%ATR{period}'] = (df.iloc[i-1][f'%ATR{period}']*(period-1) + df.iloc[i]['TR'])/float(period)
        # atr[i] = (atr[i-1]*(period-1) + df.iloc[i]['TR'])/float(period)
    df.drop(columns=['A', 'B', 'C', 'TR'], inplace=True)
    # df[f'%ATR{period}'] = pd.Series(data=atr)
    # df[f'%ATR{period}'] = pd.Series(atr)
    # print(atr[-5:])
    # print(df[f'%ATR{period}'].tail())

    return df


def average_volume_diff(df, period_fast, period_slow):
    volume1 = df['Volume'].rolling(period_fast).mean()
    volume2 = df['Volume'].rolling(period_slow).mean()
    df['VolDiff'] = ((volume1 - volume2)/volume2)*100.0
    return df


def zlsma(df, period):

    df['lsma1'] = rolling_ols(df, 'Close', period)
    df['lsma2'] = rolling_ols(df, 'lsma1', period)
    df[f'zlsma{period}'] = 2*df['lsma1'] - df['lsma2']
    df.drop(columns=['lsma1', 'lsma2'])

    return df


def volume_weighted_average(df, src, period):
    start_index = df.index[0]
    volume_sum = df['Volume'].rolling(period).sum()
    print(volume_sum.iloc[period-1])
    df[f'{src}_VWA{period}'] = np.nan
    for i in range(period, len(df)):
        weighted_sum = 0
        for j in range(period):
            weighted_sum += df.iloc[i - period + j][src]*df.iloc[i-period+j]['Volume']/volume_sum.iloc[i-1]
        df.loc[start_index + i, f'{src}_VWA{period}'] = weighted_sum
    return df


def williams_r_all(df, period):
    """
    The Goals is to algorithmically understand where is the stock price action in relation to the limits (high & low)

    Options:
    1. ((Highest High - Close)/(Highest High - Lowest Low))*-100.0 # Default
    2. ((Close - Lowest Low)/(Highest High - Lowest Low))*100.0
    3. ((Highest High - Median)/(Highest High - Lowest Low))*-100.0
    4. ((Median - Lowest Low)/(Highest High - Lowest Low))*100.0
    5. ((Highest High - Low)/(Highest High - Lowest Low))*-100.0
    6. ((High - Lowest Low)/(Highest High - Lowest Low))*100.0
    """
    highest_high = df['High'].rolling(period).max()
    lowest_low = df['Low'].rolling(period).min()
    median = (df['High'] + df['Low'])/2
    df[f'Williams_R%_High_{period}'] = ((highest_high - df['High'])/(highest_high - lowest_low))*-100.0
    df[f'Williams_R%_Close_{period}'] = ((highest_high - df['Close'])/(highest_high - lowest_low))*-100.0
    df[f'Williams_R%_Median_{period}'] = ((highest_high - median) / (
                highest_high - lowest_low)) * -100.0
    df[f'Williams_R%_Open_{period}'] = ((highest_high - df['Open']) / (
                highest_high - lowest_low)) * -100.0
    df[f'Williams_R%_Low_{period}'] = ((highest_high - df['Low']) / (highest_high - lowest_low)) * -100.0
    return df


def williams_r_all_v1(df, period):
    """
    The Goals is to algorithmically understand where is the stock price action in relation to the limits (high & low)

    Options:
    1. ((Highest High - Close)/(Highest High - Lowest Low))*-100.0 # Default
    2. ((Close - Lowest Low)/(Highest High - Lowest Low))*100.0
    3. ((Highest High - Median)/(Highest High - Lowest Low))*-100.0
    4. ((Median - Lowest Low)/(Highest High - Lowest Low))*100.0
    5. ((Highest High - Low)/(Highest High - Lowest Low))*-100.0
    6. ((High - Lowest Low)/(Highest High - Lowest Low))*100.0
    """
    highest_high = df['High'].rolling(period).max()
    lowest_low = df['Low'].rolling(period).min()
    median = (df['High'] + df['Low'])/2
    df[f'Williams_R%_High_{period}'] = ((highest_high - df['High'])/(highest_high - lowest_low))*-100.0
    df[f'Williams_R%_Close_{period}'] = ((highest_high - df['Close'])/(highest_high - lowest_low))*-100.0
    df[f'Williams_R%_Median_{period}'] = ((highest_high - median) / (
                highest_high - lowest_low)) * -100.0
    df[f'Williams_R%_Open_{period}'] = ((highest_high - df['Open']) / (
                highest_high - lowest_low)) * -100.0
    df[f'Williams_R%_Low_{period}'] = ((highest_high - df['Low']) / (highest_high - lowest_low)) * -100.0
    return df


def range_moving_average(df, period):
    start_idx = df.index[0]
    df[f'range_moving_average_{period}'] = np.nan
    for row in range(period, len(df)):
        prices = []
        for i in range(period):
            high = df.iloc[row-i]['High']
            low = df.iloc[row-i]['Low']
            prices = prices + list(np.arange(low, high, .01))
        df.loc[start_idx + row, f'range_moving_average_{period}'] = np.mean(prices)
    return df


if __name__=="__main__":
    from utils.get_all_stocks import get_all_nasdaq_100_stocks, get_all_nyse_composite_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    from indicators.momentum_indicators import rate_of_change, williams_r, rsi
    from indicators.trend_indicators import exponential_moving_average
    from machine_learning_stuff.linear_regression import rolling_ols
    from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import pandas as pd
    import yfinance as yf
    import json
    import random
    import time

    start = time.time()

    ticker = 'NXPI'
    df = pd.read_csv(download_stock_day(ticker))

    periods = [5, 9, 20, 31, 63, 126, 252]

    for period in periods:
        df = rate_of_change(df, period)
        df = percental_atr(df, period)
        df = exponential_moving_average(df, 'High', period)
        df[f'EMA{period}High'] = df[f'EMA{period}']
        df = exponential_moving_average(df, 'Low', period)
        df[f'EMA{period}Low'] = df[f'EMA{period}']
        df = exponential_moving_average(df, 'Close', period)
        df = williams_r(df, period)
        df = rsi(df, period)

    df = df[-2016:]


    # Create subplots and mention plot grid size
    fig = make_subplots(rows=5, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, subplot_titles=(f'{ticker}','Williams R%', 'RSI', '%ATR', 'ROC'),
                        row_width=[0.2, 0.2, 0.2, 0.2, 0.5])

    # Plot OHLC on 1st row
    fig.add_trace(go.Candlestick(x=df["Date"], open=df["Open"], high=df["High"],
                                 low=df["Low"], close=df["Close"], name="OHLC"),
                  row=1, col=1)

    for period in periods:
        fig.add_trace(go.Scatter(x=df['Date'], y=df[f'EMA{period}'],
                                 name=f'EMA{period}'),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df[f'EMA{period}High'],
                                 name=f'EMA{period}High'),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df[f'EMA{period}Low'],
                                 name=f'EMA{period}Low'),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df[f'Williams_R%_{period}'],
                                 name=f'Williams_R%_{period}'),
                      row=2, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df[f'RSI{period}'],
                                 name=f'RSI{period}'),
                      row=3, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df[f'%ATR{period}'],
                                 name=f'%ATR{period}'),
                      row=4, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df[f'ROC{period}'],
                                 name=f'ROC{period}'),
                      row=5, col=1)

    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.show()

    print(time.time() - start)

    # ticker = 'UPST'
    # df = pd.read_csv(download_stock_day(ticker))[-1008:]
    #
    # period1 = 50
    # period2 = 200
    # df = volume_weighted_average(df, 'Close', period1)
    # df = volume_weighted_average(df, 'High', period1)
    # df = volume_weighted_average(df, 'Low', period1)
    # # df = volume_weighted_average(df, 'Close', period2)
    #
    # fig = candlestick_chart_fig(df, ticker)
    # fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'Close_VWA{period1}'], name=f'Close_VWA{period1}')
    # fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'High_VWA{period1}'], name=f'High_VWA{period1}')
    # fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'Low_VWA{period1}'], name=f'Low_VWA{period1}')
    #
    # fig.show()

    # roc_period = 5
    # df = rate_of_change(df, roc_period)
    #
    # atr_period = 5
    # df = percental_atr(df, atr_period)
    # df['%atr_average'] = df[f'%ATR{atr_period}'].rolling(200).mean()
    #
    # df = average_volume_diff(df, 20, 200)
    # df['vol_diff_avg'] = df['VolDiff'].rolling(5).mean()
    # # df.to_csv(save_under_results_path(f'{ticker}_avg_vol_diff.csv'))
    #
    # # Create subplots and mention plot grid size
    # fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
    #                     vertical_spacing=0.03, subplot_titles=(f'{ticker}', 'VolDiff', '%ATR', 'ROC'),
    #                     row_width=[0.2, 0.2, 0.2, 0.7])
    #
    # # Plot OHLC on 1st row
    # fig.add_trace(go.Candlestick(x=df["Date"], open=df["Open"], high=df["High"],
    #                              low=df["Low"], close=df["Close"], name="OHLC"),
    #               row=1, col=1)
    #
    # fig.add_trace(go.Scatter(x=df['Date'], y=df['VolDiff'], name='VolDiff'),
    #               row=2, col=1)
    #
    # fig.add_trace(go.Scatter(x=df['Date'], y=df['vol_diff_avg'], name='vol_diff_avg'),
    #               row=2, col=1)
    #
    # fig.add_trace(go.Scatter(x=df['Date'], y=df[f'%ATR{atr_period}'], name=f'%ATR{atr_period}'),
    #               row=3, col=1)
    #
    # fig.add_trace(go.Scatter(x=df['Date'], y=df['%atr_average'], name='%atr_average'),
    #               row=3, col=1)
    #
    # fig.add_trace(go.Scatter(x=df['Date'], y=df[f'ROC{roc_period}'], name=f'ROC{roc_period}'),
    #               row=4, col=1)
    #
    # fig.update(layout_xaxis_rangeslider_visible=False)
    # fig.show()
