from ta.momentum import AwesomeOscillatorIndicator, RSIIndicator, StochRSIIndicator, StochasticOscillator
import math



def awesome_oscillator(df, fast, slow):
    df["AO"] = AwesomeOscillatorIndicator(high=df["High"], low=df["Low"], window1=fast, window2=slow).awesome_oscillator()
    return df


def awesome_oscillator_alt(df, metric_high, metric_low, fast, slow):
    df["AO"] = AwesomeOscillatorIndicator(high=df[metric_high], low=df[metric_low], window1=fast, window2=slow).awesome_oscillator()
    return df


def simple_moving_average(df, period):
    df[f'SMA{period}'] = df['Close'].rolling(period).mean()
    return df


def simple_moving_average_alt(df, metric, period):
    df[f'SMA{period}'] = df[metric].rolling(period).mean()
    return df


def zero_lag_sma(df, period):
    lag = int(math.floor((period-1)/2))
    df['SMA_DATA'] = df['Close']*2 - df.shift(lag)['Close']
    df['ZLSMA'] = df['SMA_DATA'].rolling(period).mean()
    df.drop('SMA_DATA', axis=1, inplace=True)
    df.dropna(inplace=True)
    # sma = simple_moving_average(df, period)[f'SMA{period}']
    # sma.dropna(inplace=True)
    # sma_data = 2*sma - sma.shift(lag)
    # df['ZLSMA'] = simple_moving_average_alt(sma_data, f'SMA{period}', period)
    return df


def rsi(df, period):
    df["RSI"] = RSIIndicator(close=df['Close'], window=period).rsi()
    return df


def rsi_alt(df, metric, period):
    df["RSI"] = RSIIndicator(close=df[metric], window=period).rsi()
    return df


def rsi_median(df, period):
    df["RSI"] = RSIIndicator(close=(df['High'] + df['Low'])/2, window=period).rsi()
    return df


def stoch_rsi(df, period):
    df["StochRSI"] = StochRSIIndicator(close=df['Close'], window=period).stochrsi()
    return df


def stoch_rsi_alt(df, metric, period):
    df["StochRSI"] = StochRSIIndicator(close=df[metric], window=period).stochrsi()
    return df


def stoch_rsi_median(df, period):
    df["StochRSI"] = StochRSIIndicator(close=(df['High'] + df['Low'])/2, window=period).stochrsi()
    return df


# def stoch_oscillator(df, period):
#     df[]


if __name__=="__main__":
    from utils.get_all_snp_companies import get_all_snp_companies
    from utils.download_stock_csvs import download_stock
    from utils.paths import save_under_results_path
    import pandas as pd
    import numpy as np


    ticker = 'AAPL'
    df = pd.read_csv(download_stock(ticker))
    df = df[-365:]

    period = 50

    df = zero_lag_sma(df, period)

    df.to_csv(save_under_results_path(f'{ticker}_ZLSMA.csv'))