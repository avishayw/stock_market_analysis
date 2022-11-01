import datetime as dt
import yfinance as yf
import pandas as pd
import numpy as np
from utils.download_stock_csvs import download_stock_day
from indicators.volatility_indicators import average_true_range
import plotly.graph_objects as go


def construct_renko_values_fixed_pct(df, pct=2.0, price='Close'):
    renko_df = df[['Date', price]]
    start_idx = renko_df.index[0]
    i = 0
    current_high = renko_df.iloc[0][price]
    current_low = renko_df.iloc[0][price]
    while i < len(renko_df):
        up_target_price = current_high*(1+pct/100)
        down_target_price = current_low*(1-pct/100)
        if renko_df.iloc[i][price] >= up_target_price:
            renko_df.loc[start_idx + i, 'renko_open'] = current_high
            renko_df.loc[start_idx + i, 'renko_close'] = up_target_price
            renko_df.loc[start_idx + i, 'renko_low'] = current_high
            renko_df.loc[start_idx + i, 'renko_high'] = up_target_price
            current_low = current_high
            current_high = up_target_price
        elif renko_df.iloc[i][price] <= down_target_price:
            renko_df.loc[start_idx + i, 'renko_open'] = current_low
            renko_df.loc[start_idx + i, 'renko_close'] = down_target_price
            renko_df.loc[start_idx + i, 'renko_low'] = down_target_price
            renko_df.loc[start_idx + i, 'renko_high'] = current_low
            current_high = current_low
            current_low = down_target_price

        i += 1
    renko_df.dropna(inplace=True)
    return renko_df[['Date', 'renko_high', 'renko_low', 'renko_close', 'renko_open']]


def construct_renko_values_fixed_point(df, point=50.0, price='Close'):
    renko_df = df[['Date', price]]
    start_idx = renko_df.index[0]
    i = 0
    current_high = renko_df.iloc[0][price]
    current_low = renko_df.iloc[0][price]
    while i < len(renko_df):
        up_target_price = current_high + point
        down_target_price = current_low - point
        if renko_df.iloc[i][price] >= up_target_price:
            renko_df.loc[start_idx + i, 'renko_open'] = current_high
            renko_df.loc[start_idx + i, 'renko_close'] = up_target_price
            renko_df.loc[start_idx + i, 'renko_low'] = current_high
            renko_df.loc[start_idx + i, 'renko_high'] = up_target_price
            current_low = current_high
            current_high = up_target_price
        elif renko_df.iloc[i][price] <= down_target_price:
            renko_df.loc[start_idx + i, 'renko_open'] = current_low
            renko_df.loc[start_idx + i, 'renko_close'] = down_target_price
            renko_df.loc[start_idx + i, 'renko_low'] = down_target_price
            renko_df.loc[start_idx + i, 'renko_high'] = current_low
            current_high = current_low
            current_low = down_target_price

        i += 1
    renko_df.dropna(inplace=True)
    return renko_df[['Date', 'renko_high', 'renko_low', 'renko_close', 'renko_open']]


def construct_renko_values_fixed_atr(df, atr_length=14, price='Close'):
    df = average_true_range(df, atr_length)
    renko_df = df[['Date', price, f'ATR{atr_length}']]
    start_idx = renko_df.index[0]
    i = 0
    current_high = renko_df.iloc[0][price]
    current_low = renko_df.iloc[0][price]
    while i < len(renko_df):
        up_target_price = current_high + renko_df.shift(1).iloc[i][f'ATR{atr_length}']
        down_target_price = current_low - renko_df.shift(1).iloc[i][f'ATR{atr_length}']
        if renko_df.iloc[i][price] >= up_target_price:
            renko_df.loc[start_idx + i, 'renko_open'] = current_high
            renko_df.loc[start_idx + i, 'renko_close'] = up_target_price
            renko_df.loc[start_idx + i, 'renko_low'] = current_high
            renko_df.loc[start_idx + i, 'renko_high'] = up_target_price
            current_low = current_high
            current_high = up_target_price
        elif renko_df.iloc[i][price] <= down_target_price:
            renko_df.loc[start_idx + i, 'renko_open'] = current_low
            renko_df.loc[start_idx + i, 'renko_close'] = down_target_price
            renko_df.loc[start_idx + i, 'renko_low'] = down_target_price
            renko_df.loc[start_idx + i, 'renko_high'] = current_low
            current_high = current_low
            current_low = down_target_price

        i += 1
    renko_df.dropna(inplace=True)
    return renko_df[['Date', 'renko_high', 'renko_low', 'renko_close', 'renko_open']]


def renko_chart(ticker, renko_df):
    fig = go.Figure(go.Candlestick(x=renko_df['Date'],
                                   open=renko_df['renko_open'],
                                   high=renko_df['renko_high'],
                                   low=renko_df['renko_low'],
                                   close=renko_df['renko_close'], name=ticker, yaxis='y1')).update_layout(
        xaxis_rangeslider_visible=False)
    return fig


if __name__ == '__main__':
    from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart
    import matplotlib
    import mplfinance as mpf

    ticker = 'META'
    df = pd.read_csv(download_stock_day(ticker))
    renko_df = construct_renko_values_fixed_atr(df)
    renko_df['SMA'] = renko_df['renko_close'].rolling(10).mean()
    fig = renko_chart(ticker, renko_df)
    fig = add_line_to_candlestick_chart(fig, renko_df['Date'], renko_df['SMA'], 'SMA')
    fig.show()

    # fig = candlestick_chart_fig(df, ticker)
    # fig.show()

    # df['Datetime'] = pd.to_datetime(df['Date'], utc=True)
    # df.index = pd.DatetimeIndex(df['Datetime'])
    # mpf.plot(df, type='renko')

