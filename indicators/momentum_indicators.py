from ta.momentum import AwesomeOscillatorIndicator, RSIIndicator, StochasticOscillator, KAMAIndicator, ROCIndicator, WilliamsRIndicator
import math
from mathematical_functions.linear_regression import linreg
import ta


def awesome_oscillator(df, fast, slow):
    df["AO"] = AwesomeOscillatorIndicator(high=df["High"], low=df["Low"], window1=fast, window2=slow).awesome_oscillator()
    return df


def simple_moving_average(df, period):
    df[f'SMA{period}'] = df['Close'].rolling(period).mean()
    return df


def zero_lag_sma(df, period): # TradingView
    df = linreg(df, 'Close', period)
    df['lsma'] = df['linreg']
    df = linreg(df, 'linreg', period)
    df['eq'] = df['lsma'] - df['linreg']
    df['zlsma'] = df['lsma'] + df['eq']
    # df['zlsma'] = df['zlsma'].shift(-10)
    df.drop(columns=['lsma', 'linreg', 'eq'])
    return df


def kama(df, period, pow1, pow2): # Kaufman Adaptive Moving Average
    df[f'KAMA{period}_{pow1}_{pow2}'] = KAMAIndicator(df['Close'], period, pow1, pow2).kama()
    return df


def rate_of_change(df, period, inplace=True):
    roc = ROCIndicator(df['Close'], period).roc()
    if inplace:
        df[f'ROC{period}'] = roc
        return df
    return roc


def rsi(df, period):
    df[f"RSI{period}"] = RSIIndicator(close=df['Close'], window=period).rsi()
    return df


def stochastic(df, period):
    df[f"stoch{period}"] = StochasticOscillator(df['High'], df['Low'], df['Close'], period).stoch()
    return df


def williams_r(df, period):
    df[f'Williams_R%_{period}'] = WilliamsRIndicator(df['High'], df['Low'], df['Close'], period).williams_r()
    return df


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import numpy as np
    from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart


    ticker = 'DJI'
    df = pd.read_csv(download_stock_day(ticker))
    df = df[-1260:]

    pd.set_option('display.max_columns', None)

    df = simple_moving_average(df, 756)
    df = simple_moving_average(df, 504)
    df = simple_moving_average(df, 252)
    df = simple_moving_average(df, 200)
    df = simple_moving_average(df, 50)
    df = simple_moving_average(df, 20)

    print(df.tail())
    