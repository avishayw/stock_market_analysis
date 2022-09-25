from ta.trend import EMAIndicator, ADXIndicator, AroonIndicator
import math


def exponential_moving_average(df, src, period, inplace=True):
    ema = EMAIndicator(df[src], period).ema_indicator()
    if inplace:
        df[f'EMA{period}'] = ema
        return df
    return ema


def zero_lag_ema(df, period):
    lag = int(math.floor((period-1)/2))
    df['EMADATA'] = df['Close']*2 - df.shift(lag)['Close']
    df = exponential_moving_average(df, 'EMADATA', period)
    df[f'ZLEMA{period}'] = df[f'EMA{period}']
    df.drop(columns=['EMADATA', f'EMA{period}'], axis=1, inplace=True)
    return df


def average_directional_movement(df, period):
    adx = ADXIndicator(df['High'], df['Low'], df['Close'], period)
    df[f'ADX{period}'] = adx.adx()
    df[f'DI+{period}'] = adx.adx_pos()
    df[f'DI-{period}'] = adx.adx_neg()
    return df


def aroon(df, period):
    aroon = AroonIndicator(df['Close'], period)
    df['aroon'] = aroon.aroon_indicator()
    df['aroon_up'] = aroon.aroon_up()
    df['aroon_down'] = aroon.aroon_down()
    return df