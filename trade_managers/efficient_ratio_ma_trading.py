import pandas as pd
import numpy as np
from measurements.noise_measurements import efficiency_ratio
from indicators.momentum_indicators import simple_moving_average


def efficient_ratio_ma_trading(ticker, df, sma1_period, sma2_period, sma1_uptrend_roc_period,
                                   sma2_uptrend_roc_period, sma1_uptrend_roc_th, sma2_uptrend_roc_th,
                                   sma1_uptrend_er_th, sma2_uptrend_er_th, sma1_downtrend_roc_period,
                                   sma1_downtrend_roc_th, sma1_downtrend_er_th):

    df = simple_moving_average(df, sma1_period)
    df = simple_moving_average(df, sma2_period)
    df[f'SMA{sma1_period}ROC{sma1_uptrend_roc_period}'] = ((df[f'SMA{sma1_period}'] - df.shift(sma1_uptrend_roc_period)[
        f'SMA{sma1_period}']) /
                                                           df.shift(sma1_uptrend_roc_period)[
                                                               f'SMA{sma1_period}']) * 100.0
    df[f'SMA{sma1_period}ROC{sma1_downtrend_roc_period}'] = ((df[f'SMA{sma1_period}'] -
                                                              df.shift(sma1_downtrend_roc_period)[
                                                                  f'SMA{sma1_period}']) /
                                                             df.shift(sma1_downtrend_roc_period)[
                                                                 f'SMA{sma1_period}']) * 100.0
    df[f'SMA{sma2_period}ROC{sma2_uptrend_roc_period}'] = ((df[f'SMA{sma2_period}'] - df.shift(sma2_uptrend_roc_period)[
        f'SMA{sma2_period}']) /
                                                           df.shift(sma2_uptrend_roc_period)[
                                                               f'SMA{sma2_period}']) * 100.0
    df[f'SMA{sma1_period}ER'] = efficiency_ratio(df, f'SMA{sma1_period}', sma1_period, inplace=False)
    df[f'SMA{sma2_period}ER'] = efficiency_ratio(df, f'SMA{sma2_period}', sma2_period, inplace=False)

    df['sell_signal'] = np.where((df[f'SMA{sma1_period}ROC{sma1_uptrend_roc_period}'] > sma1_uptrend_roc_th) &
                                 (df[f'SMA{sma2_period}ROC{sma2_uptrend_roc_period}'] > sma2_uptrend_roc_th) &
                                 (df[f'SMA{sma1_period}ER'] > sma1_uptrend_er_th) &
                                 (df[f'SMA{sma2_period}ER'] > sma2_uptrend_er_th), True, False)
    df['buy_signal'] = np.where((df[f'SMA{sma1_period}ROC{sma1_downtrend_roc_period}'] < sma1_downtrend_roc_th) &
                                (df[f'SMA{sma1_period}ER'] > sma1_downtrend_er_th), True, False)