import os.path
import pandas as pd
import numpy as np
from datetime import datetime
from measurements.noise_measurements import efficiency_ratio, price_density
from indicators.momentum_indicators import simple_moving_average
from trade_managers._signal_trading_manager import signal_trading_manager_long
from utils.download_stock_csvs import download_stock_day
from utils.paths import save_under_results_path
import json
import yfinance as yf


def ma_roc_er_signals(df,
                      sma1_period=5,
                      sma2_period=20,
                      sma1_uptrend_roc_period=5,
                      sma2_uptrend_roc_period=5,
                      sma1_uptrend_roc_th=3.0,
                      sma2_uptrend_roc_th=2.0,
                      sma1_uptrend_er_th=0.5,
                      sma2_uptrend_er_th=0.5,
                      sma1_downtrend_roc_period=5,
                      sma1_downtrend_roc_th=-3.0,
                      sma1_downtrend_er_th=0.2):

    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

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

    return df


def ma_roc_er_signals_v6(df,
                         sma1_period=5,
                         sma2_period=20,
                         sma1_uptrend_roc_period=5,
                         sma2_uptrend_roc_period=5,
                         sma1_uptrend_roc_th=3.0,
                         sma2_uptrend_roc_th=2.0,
                         sma1_uptrend_er_th=0.5,
                         sma2_uptrend_er_th=0.5,
                         sma1_downtrend_roc_period=5,
                         sma1_downtrend_roc_th=-3.0,
                         sma1_downtrend_er_th=0.2):

    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

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

    df['Datetime'] = pd.to_datetime(df['Date'])
    df['max200'] = df['High'].rolling(200).max()
    df['min200'] = df['Low'].rolling(200).min()
    df['avg_high'] = df['High'].rolling(20).mean()
    df['avg_low'] = df['Low'].rolling(20).mean()
    df['bear'] = np.where(df['avg_high'] < df['max200'] * 0.8, True, False)
    df['bull'] = np.where(df['avg_low'] > df['min200'] * 1.2, True, False)

    spy_df = yf.Ticker('SPY').history(period='max', interval='1d').reset_index()
    spy_df['Datetime'] = pd.to_datetime(spy_df['Date'])
    df_first_datetime = df.iloc[0]['Datetime']
    df_last_datetime = df.iloc[-1]['Datetime']
    spy_df = spy_df.loc[(spy_df['Datetime'] >= df_first_datetime) & (spy_df['Datetime'] <= df_last_datetime)].copy()
    spy_df['max200'] = spy_df['High'].rolling(200).max()
    spy_df['min200'] = spy_df['Low'].rolling(200).min()
    spy_df['avg_high'] = spy_df['High'].rolling(20).mean()
    spy_df['avg_low'] = spy_df['Low'].rolling(20).mean()
    # spy_df['bear'] = np.where(spy_df['avg_high'] < spy_df['max200'] * 0.8, True, False)
    # spy_df['bull'] = np.where(spy_df['avg_low'] > spy_df['min200'] * 1.2, True, False)
    df['spy_bear'] = np.where(spy_df['avg_high'] < spy_df['max200'] * 0.8, True, False)
    df['spy_bull'] = np.where(spy_df['avg_low'] > spy_df['min200'] * 1.2, True, False)

    df['sell_signal'] = np.where((df[f'SMA{sma1_period}ROC{sma1_uptrend_roc_period}'] > sma1_uptrend_roc_th) &
                                 (df[f'SMA{sma2_period}ROC{sma2_uptrend_roc_period}'] > sma2_uptrend_roc_th) &
                                 (df[f'SMA{sma1_period}ER'] > sma1_uptrend_er_th) &
                                 (df[f'SMA{sma2_period}ER'] > sma2_uptrend_er_th), True, False)
    df['buy_signal'] = np.where((df[f'SMA{sma1_period}ROC{sma1_downtrend_roc_period}'] < sma1_downtrend_roc_th) &
                                (df[f'SMA{sma1_period}ER'] > sma1_downtrend_er_th), True, False)

    return df


def ma_roc_er_signals_v2(df,
                         sma1_period=5,
                         sma2_period=20,
                         sma1_uptrend_roc_period=5,
                         sma2_uptrend_roc_period=5,
                         sma1_uptrend_roc_th=3.0,
                         sma2_uptrend_roc_th=2.0,
                         sma1_uptrend_er_th=0.5,
                         sma2_uptrend_er_th=0.5,
                         sma1_downtrend_roc_period=5,
                         sma1_downtrend_roc_th=-3.0,
                         sma1_downtrend_er_th=0.2):

    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

    df = simple_moving_average(df, sma1_period)
    df = simple_moving_average(df, sma2_period)
    df = simple_moving_average(df, 100)
    df = simple_moving_average(df, 200)
    df['SMA200ROC5'] = ((df['SMA200'] - df.shift(5)['SMA200'])/df.shift(5)['SMA200'])*100.0
    df['SMA100ROC5'] = ((df['SMA100'] - df.shift(5)['SMA100']) / df.shift(5)['SMA100']) * 100.0
    df['close_sma200_ratio'] = ((df['Close'] - df['SMA200'])/df['SMA200'])*100.0
    df['close_sma100_ratio'] = ((df['Close'] - df['SMA100']) / df['SMA100']) * 100.0
    rolling_min = df['Low'].rolling(200).min()
    df['close_min200_ratio'] = ((df['Close'] - rolling_min)/rolling_min)*100.0
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
                                (df[f'SMA{sma1_period}ER'] > sma1_downtrend_er_th) &
                                (df['close_min200_ratio'] > 15.0) &
                                (((df['SMA100ROC5'] >= -11.15) & (df['SMA100ROC5'] <= -1.373)) |
                                 ((df['SMA100ROC5'] >= 0.56) & (df['SMA100ROC5'] <= 2.72)) |
                                 ((df['close_sma200_ratio'] >= -82.50) & (df['close_sma200_ratio'] <= -13.44)) |
                                 ((df['close_sma200_ratio'] >= 1.20) & (df['close_sma200_ratio'] <= 30.6)) |
                                 ((df['SMA200ROC5'] >= -5.81) & (df['SMA200ROC5'] <= -0.62)) |
                                 ((df['SMA200ROC5'] >= 0.1) & (df['SMA200ROC5'] <= 1.83)) |
                                 ((df['close_sma100_ratio'] >= -72.2) & (df['close_sma100_ratio'] <= -10.34)) |
                                 ((df['close_sma100_ratio'] >= -0.21) & (df['close_sma100_ratio'] <= 10.62))), True, False)

    return df


def ma_roc_er_trading_v2(ticker,
                                 df,
                                 sma1_period=5,
                                 sma2_period=20,
                                 sma1_uptrend_roc_period=5,
                                 sma2_uptrend_roc_period=5,
                                 sma1_uptrend_roc_th=3.0,
                                 sma2_uptrend_roc_th=2.0,
                                 sma1_uptrend_er_th=0.5,
                                 sma2_uptrend_er_th=0.5,
                                 sma1_downtrend_roc_period=5,
                                 sma1_downtrend_roc_th=-3.0,
                                 sma1_downtrend_er_th=0.2):

    df = ma_roc_er_signals_v2(df,
                           sma1_period=sma1_period,
                           sma2_period=sma2_period,
                           sma1_uptrend_roc_period=sma1_uptrend_roc_period,
                           sma2_uptrend_roc_period=sma2_uptrend_roc_period,
                           sma1_uptrend_roc_th=sma1_uptrend_roc_th,
                           sma2_uptrend_roc_th=sma2_uptrend_roc_th,
                           sma1_uptrend_er_th=sma1_uptrend_er_th,
                           sma2_uptrend_er_th=sma2_uptrend_er_th,
                           sma1_downtrend_roc_period=sma1_downtrend_roc_period,
                           sma1_downtrend_roc_th=sma1_downtrend_roc_th,
                           sma1_downtrend_er_th=sma1_downtrend_er_th)
    # For filtering
    df['VolumeAVG200'] = df['Volume'].rolling(200).mean()
    df['VolumeAVG5'] = df['Volume'].rolling(5).mean()
    df['VolumeRatio'] = ((df['VolumeAVG5'] - df['VolumeAVG200'])/df['VolumeAVG200'])*100.0
    all_time_max = df['High'].rolling(200).max()
    all_time_low = df['Low'].rolling(200).min()
    df['MaxCloseRatio'] = ((all_time_max - df['Close'])/df['Close'])*100.0
    df['CloseMinRatio'] = ((df['Close'] - all_time_low)/all_time_low)*100.0

    df['Datetime'] = pd.to_datetime(df['Date'])
    i = 0
    long_position = False
    enter_price = None
    enter_date = None
    cap = 100.0

    trades = []

    while i < len(df):
        if long_position:
            if df.iloc[i]['sell_signal']:
                exit_price = df.shift(-1).iloc[i]['Open']
                if np.isnan(exit_price):
                    break
                exit_date = df.shift(-1).iloc[i]['Date']
                if np.isnan(exit_price):
                    long_position = False
                    continue
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = pd.DataFrame.copy(df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                                                     (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))])
                period_df.reset_index(inplace=True)
                period_max = period_df['High'].max()
                max_date = period_df.iloc[period_df['High'].idxmax()]['Datetime'].strftime('%Y-%m-%d')
                period_min = period_df['Low'].min()
                min_date = period_df.iloc[period_df['Low'].idxmin()]['Datetime'].strftime('%Y-%m-%d')
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'period_max': period_max,
                              'period_max_date': max_date,
                              'period_min': period_min,
                              'period_min_date': min_date,
                              'volume_avg_200': volume_avg_200,
                              'volume_ratio': volume_ratio,
                              'max_close_ratio': max_close_ratio,
                              'close_min_ratio': close_min_ratio}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['buy_signal'] and df.shift(-1).iloc[i]['Open'] != 0.0:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            volume_avg_200 = df.iloc[i]['VolumeAVG200']
            volume_ratio = df.iloc[i]['VolumeRatio']
            max_close_ratio = df.iloc[i]['MaxCloseRatio']
            close_min_ratio = df.iloc[i]['CloseMinRatio']
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


def ma_roc_er_signals_v3(df,
                         sma1_period=5,
                         sma2_period=20,
                         sma1_uptrend_roc_period=5,
                         sma2_uptrend_roc_period=5,
                         sma1_uptrend_roc_th=3.0,
                         sma2_uptrend_roc_th=2.0,
                         sma1_uptrend_er_th=0.5,
                         sma2_uptrend_er_th=0.5,
                         sma1_downtrend_roc_period=5,
                         sma1_downtrend_roc_th=-3.0,
                         sma1_downtrend_er_th=0.2):

    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

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
    df[f'SMA{sma1_period}ER{sma1_uptrend_roc_period}'] = efficiency_ratio(df, f'SMA{sma1_period}', sma1_uptrend_roc_period, inplace=False)
    df[f'SMA{sma2_period}ER{sma2_uptrend_roc_period}'] = efficiency_ratio(df, f'SMA{sma2_period}', sma2_uptrend_roc_period, inplace=False)
    df[f'SMA{sma1_period}ER{sma1_downtrend_roc_period}'] = efficiency_ratio(df, f'SMA{sma1_period}',
                                                                          sma1_downtrend_roc_period, inplace=False)

    df['sell_signal'] = np.where((df[f'SMA{sma1_period}ROC{sma1_uptrend_roc_period}'] > sma1_uptrend_roc_th) &
                                 (df[f'SMA{sma2_period}ROC{sma2_uptrend_roc_period}'] > sma2_uptrend_roc_th) &
                                 (df[f'SMA{sma1_period}ER{sma1_uptrend_roc_period}'] > sma1_uptrend_er_th) &
                                 (df[f'SMA{sma2_period}ER{sma2_uptrend_roc_period}'] > sma2_uptrend_er_th), True, False)
    df['buy_signal'] = np.where((df[f'SMA{sma1_period}ROC{sma1_downtrend_roc_period}'] < sma1_downtrend_roc_th) &
                                (df[f'SMA{sma1_period}ER{sma1_downtrend_roc_period}'] > sma1_downtrend_er_th), True, False)

    return df


def ma_roc_er_signals_v4(df,
                         sma1_period=5,
                         sma2_period=20,
                         sma1_uptrend_roc_period=5,
                         sma2_uptrend_roc_period=5,
                         sma1_uptrend_roc_th=3.0,
                         sma2_uptrend_roc_th=2.0,
                         sma1_uptrend_er_th=0.5,
                         sma2_uptrend_er_th=0.5,
                         sma1_downtrend_roc_period=5,
                         sma1_downtrend_roc_th=-3.0,
                         sma1_downtrend_er_th=0.2):

    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

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
    df[f'SMA{sma1_period}ER{sma1_uptrend_roc_period}'] = efficiency_ratio(df, f'SMA{sma1_period}', sma1_uptrend_roc_period, inplace=False)
    df[f'SMA{sma2_period}ER{sma2_uptrend_roc_period}'] = efficiency_ratio(df, f'SMA{sma2_period}', sma2_uptrend_roc_period, inplace=False)
    df[f'SMA{sma1_period}ER{sma1_downtrend_roc_period}'] = efficiency_ratio(df, f'SMA{sma1_period}',
                                                                          sma1_downtrend_roc_period, inplace=False)

    df['sell_signal'] = np.where((df[f'SMA{sma1_period}ROC{sma1_uptrend_roc_period}'] > sma1_uptrend_roc_th) &
                                 (df[f'SMA{sma2_period}ROC{sma2_uptrend_roc_period}'] > sma2_uptrend_roc_th) &
                                 (df[f'SMA{sma1_period}ER{sma1_uptrend_roc_period}'] > sma1_uptrend_er_th) &
                                 (df[f'SMA{sma2_period}ER{sma2_uptrend_roc_period}'] > sma2_uptrend_er_th), True, False)
    df['buy_signal'] = np.where((df[f'SMA{sma1_period}ROC{sma1_downtrend_roc_period}'] < sma1_downtrend_roc_th) &
                                (df[f'SMA{sma1_period}ER{sma1_downtrend_roc_period}'] > sma1_downtrend_er_th), True, False)

    return df


def ma_roc_er_trading_v3(ticker,
                                 df,
                                 sma1_period=5,
                                 sma2_period=20,
                                 sma1_uptrend_roc_period=5,
                                 sma2_uptrend_roc_period=5,
                                 sma1_uptrend_roc_th=3.0,
                                 sma2_uptrend_roc_th=2.0,
                                 sma1_uptrend_er_th=0.5,
                                 sma2_uptrend_er_th=0.5,
                                 sma1_downtrend_roc_period=5,
                                 sma1_downtrend_roc_th=-3.0,
                                 sma1_downtrend_er_th=0.2):

    df = ma_roc_er_signals_v3(df,
                           sma1_period=sma1_period,
                           sma2_period=sma2_period,
                           sma1_uptrend_roc_period=sma1_uptrend_roc_period,
                           sma2_uptrend_roc_period=sma2_uptrend_roc_period,
                           sma1_uptrend_roc_th=sma1_uptrend_roc_th,
                           sma2_uptrend_roc_th=sma2_uptrend_roc_th,
                           sma1_uptrend_er_th=sma1_uptrend_er_th,
                           sma2_uptrend_er_th=sma2_uptrend_er_th,
                           sma1_downtrend_roc_period=sma1_downtrend_roc_period,
                           sma1_downtrend_roc_th=sma1_downtrend_roc_th,
                           sma1_downtrend_er_th=sma1_downtrend_er_th)
    # For filtering
    df['PriceDensity5'] = price_density(df, 5, inplace=False)
    df['PriceDensity20'] = price_density(df, 20, inplace=False)
    df['PriceDensity200'] = price_density(df, 200, inplace=False)

    df['Datetime'] = pd.to_datetime(df['Date'])
    i = 0
    long_position = False
    enter_price = None
    enter_date = None
    cap = 100.0

    trades = []

    while i < len(df):
        if long_position:
            if df.iloc[i]['sell_signal']:
                exit_price = df.shift(-1).iloc[i]['Open']
                if np.isnan(exit_price):
                    break
                exit_date = df.shift(-1).iloc[i]['Date']
                if np.isnan(exit_price):
                    long_position = False
                    continue
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = pd.DataFrame.copy(df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                                                     (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))])
                period_df.reset_index(inplace=True)
                period_max = period_df['High'].max()
                max_date = period_df.iloc[period_df['High'].idxmax()]['Datetime'].strftime('%Y-%m-%d')
                period_min = period_df['Low'].min()
                min_date = period_df.iloc[period_df['Low'].idxmin()]['Datetime'].strftime('%Y-%m-%d')
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'period_max': period_max,
                              'period_max_date': max_date,
                              'period_min': period_min,
                              'period_min_date': min_date,
                              'price_density_5': price_density_5,
                              'price_density_20': price_density_20,
                              'price_density_200': price_density_200}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['buy_signal'] and df.shift(-1).iloc[i]['Open'] != 0.0:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            price_density_5 = df.iloc[i]['PriceDensity5']
            price_density_20 = df.iloc[i]['PriceDensity20']
            price_density_200 = df.iloc[i]['PriceDensity200']
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


def ma_roc_er_trading_v4(ticker,
                                 df,
                                 sma1_period=5,
                                 sma2_period=20,
                                 sma1_uptrend_roc_period=5,
                                 sma2_uptrend_roc_period=5,
                                 sma1_uptrend_roc_th=3.0,
                                 sma2_uptrend_roc_th=2.0,
                                 sma1_uptrend_er_th=0.5,
                                 sma2_uptrend_er_th=0.5,
                                 sma1_downtrend_roc_period=5,
                                 sma1_downtrend_roc_th=-3.0,
                                 sma1_downtrend_er_th=0.2):
    from machine_learning_stuff.linear_regression import backward_linear_regression
    from indicators.my_indicators import volume_profile

    df = ma_roc_er_signals_v4(df,
                           sma1_period=sma1_period,
                           sma2_period=sma2_period,
                           sma1_uptrend_roc_period=sma1_uptrend_roc_period,
                           sma2_uptrend_roc_period=sma2_uptrend_roc_period,
                           sma1_uptrend_roc_th=sma1_uptrend_roc_th,
                           sma2_uptrend_roc_th=sma2_uptrend_roc_th,
                           sma1_uptrend_er_th=sma1_uptrend_er_th,
                           sma2_uptrend_er_th=sma2_uptrend_er_th,
                           sma1_downtrend_roc_period=sma1_downtrend_roc_period,
                           sma1_downtrend_roc_th=sma1_downtrend_roc_th,
                           sma1_downtrend_er_th=sma1_downtrend_er_th)

    """
    The 4 conditions for a trade: market condition, area of value, entry trigger & trade management
    
    For market condition I will add SPY regression analysis of 3 periods: 20, 50 and 200.
    For area of value I will add the volume profile, taking the 5 mean prices with the most volume 200 periods back.
    For each of these prices I will calculate the percentage from the current close price.
    For entry trigger I would use reverse patterns, but more work needed in detecting those so I will leave it for
    later.
    
    """
    spy_df = yf.Ticker('SPY').history(period='max', interval='1d').reset_index()
    spy_df['Datetime'] = pd.to_datetime(spy_df['Date'])
    df['Datetime'] = pd.to_datetime(df['Date'])
    i = 0
    long_position = False
    enter_price = None
    enter_date = None
    cap = 100.0

    trades = []

    while i < len(df):
        if long_position:
            if df.iloc[i]['sell_signal']:
                exit_price = df.shift(-1).iloc[i]['Open']
                # if np.isnan(exit_price):
                #     break
                exit_date = df.shift(-1).iloc[i]['Date']
                if np.isnan(exit_price):
                    long_position = False
                    continue
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = pd.DataFrame.copy(df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                                                     (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))])
                period_df.reset_index(inplace=True)
                period_max = period_df['High'].max()
                try:
                    max_date = period_df.iloc[period_df['High'].idxmax()]['Datetime'].strftime('%Y-%m-%d')
                except ValueError as e:
                    print(e)
                    print(enter_date)
                    print(exit_date)
                    exit()
                period_min = period_df['Low'].min()
                min_date = period_df.iloc[period_df['Low'].idxmin()]['Datetime'].strftime('%Y-%m-%d')
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'period_max': period_max,
                              'period_max_date': max_date,
                              'period_min': period_min,
                              'period_min_date': min_date}
                trade_dict.update(stock_linreg)
                trade_dict.update(spy_linreg)
                if value_indicator:
                    trade_dict.update(volume_levels)
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['buy_signal'] and df.shift(-1).iloc[i]['Open'] > 1.0:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']

            # stock linreg
            linreg_df = df.loc[df['Datetime'] <= df.iloc[i]['Datetime']].copy()
            if len(linreg_df) < 50:
                i += 1
                continue
            linreg_periods = [5, 20, 50]
            linreg_df = df.loc[df['Datetime'] <= df.iloc[i]['Datetime']].copy()
            stock_linreg = {}
            for period in linreg_periods:
                try:
                    roc, coefficient, score, model = backward_linear_regression(linreg_df, 'Close', len(linreg_df), period)
                    stock_linreg[f'stock_linear_roc_{period}'] = roc
                    stock_linreg[f'stock_linear_score_{period}'] = score
                except ValueError as e:
                    print(e)

            # SPY (market condition)
            spy = spy_df.loc[spy_df['Datetime'] <= df.iloc[i]['Datetime']].copy()
            linreg_periods = [20, 50, 200]
            spy_linreg = {}
            for period in linreg_periods:
                try:
                    roc, coefficient, score, model = backward_linear_regression(spy, 'Close', len(spy), period)
                    spy_linreg[f'spy_linear_roc_{period}'] = roc
                    spy_linreg[f'spy_linear_score_{period}'] = score
                except TypeError as e:
                    print(e)

            # Volume Profile (area of value)
            sample_df = df.loc[df['Datetime'] <= df.iloc[i]['Datetime']].copy()
            if len(sample_df) > 200:
                value_indicator = True
                current_close = df.iloc[i]['Close']
                volume_dict = volume_profile(sample_df, len(sample_df), 200)
                volume_levels = {}
                volume_columns = []
                for j, volume in enumerate(volume_dict.keys()):
                    current_volume = volume_dict[volume][0]
                    volume_columns.append(f'high_volume_{j}')
                    volume_levels[f'high_volume_{j}'] = current_volume
                    volume_levels[f'high_volume_{j}_ratio'] = ((current_close - current_volume)/current_volume)*100.0
                    if j == 4:
                        break
            else:
                value_indicator = False
            long_position = True
        i += 1

    print(ticker, cap)
    return trades, cap


def ma_roc_er_trading_v5(ticker,
                         sma1_period=5,
                         sma2_period=20,
                         sma1_uptrend_roc_period=5,
                         sma2_uptrend_roc_period=5,
                         sma1_uptrend_roc_th=3.0,
                         sma2_uptrend_roc_th=2.0,
                         sma1_uptrend_er_th=0.5,
                         sma2_uptrend_er_th=0.5,
                         sma1_downtrend_roc_period=5,
                         sma1_downtrend_roc_th=-3.0,
                         sma1_downtrend_er_th=0.2):
    df = pd.read_csv(download_stock_day(ticker))
    df = ma_roc_er_signals_v4(df,
                              sma1_period=sma1_period,
                              sma2_period=sma2_period,
                              sma1_uptrend_roc_period=sma1_uptrend_roc_period,
                              sma2_uptrend_roc_period=sma2_uptrend_roc_period,
                              sma1_uptrend_roc_th=sma1_uptrend_roc_th,
                              sma2_uptrend_roc_th=sma2_uptrend_roc_th,
                              sma1_uptrend_er_th=sma1_uptrend_er_th,
                              sma2_uptrend_er_th=sma2_uptrend_er_th,
                              sma1_downtrend_roc_period=sma1_downtrend_roc_period,
                              sma1_downtrend_roc_th=sma1_downtrend_roc_th,
                              sma1_downtrend_er_th=sma1_downtrend_er_th)

    """
    The 4 conditions for a trade: market condition, area of value, entry trigger & trade management

    For market condition I will add SPY regression analysis of 3 periods: 20, 50 and 200.
    For area of value I will add the volume profile, taking the 5 mean prices with the most volume 200 periods back.
    For each of these prices I will calculate the percentage from the current close price.
    For entry trigger I would use reverse patterns, but more work needed in detecting those so I will leave it for
    later.

    """
    spy_df = yf.Ticker('SPY').history(period='max', interval='1d').reset_index()
    spy_df['Datetime'] = pd.to_datetime(spy_df['Date'])
    spy_df['max200'] = spy_df['High'].rolling(200).max()
    spy_df['min200'] = spy_df['Low'].rolling(200).min()
    spy_df['avg_high'] = spy_df['High'].rolling(20).mean()
    spy_df['avg_low'] = spy_df['Low'].rolling(20).mean()
    spy_df['bear'] = np.where(spy_df['avg_high'] < spy_df['max200']*0.8, True, False)
    spy_df['bull'] = np.where(spy_df['avg_low'] > spy_df['min200']*1.2, True, False)

    stock = yf.Ticker(ticker)
    stock_info = stock.info
    shares_outstanding = None
    if "marketCap" in stock_info.keys():
        today_market_cap = stock_info["marketCap"]
        shares_outstanding = int(np.floor(stock.history(period='max', interval='1d').iloc[-1]['Close'] / today_market_cap))

    df['Datetime'] = pd.to_datetime(df['Date'])
    df['max200'] = df['High'].rolling(200).max()
    df['min200'] = df['Low'].rolling(200).min()
    df['avg_high'] = df['High'].rolling(20).mean()
    df['avg_low'] = df['Low'].rolling(20).mean()
    df['bear'] = np.where(df['avg_high'] < df['max200']*0.8, True, False)
    df['bull'] = np.where(df['avg_low'] > df['min200']*1.2, True, False)

    stochastic_period = 14
    stochastic_fast = 5
    stochastic_slow = 20
    high = df['High'].rolling(stochastic_period).max()
    low = df['Low'].rolling(stochastic_period).min()
    df['%K'] = ((df['Close'] - low) / (high - low)) * 100.0
    df['%DF'] = df['%K'].rolling(stochastic_fast).mean()
    df['%DS'] = df['%K'].rolling(stochastic_slow).mean()
    df['%DF>%DS'] = df['%DF'] > df['%DS']

    i = 0
    long_position = False
    cap = 100.0

    trades = []

    while i < len(df):
        if long_position:
            if df.iloc[i]['sell_signal']:
                exit_price = df.shift(-1).iloc[i]['Open']
                # if np.isnan(exit_price):
                #     break
                exit_date = df.shift(-1).iloc[i]['Date']
                if np.isnan(exit_price):
                    long_position = False
                    continue
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = pd.DataFrame.copy(df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                                                     (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))])
                period_df.reset_index(inplace=True)
                period_max = period_df['High'].max()
                max_date = period_df.iloc[period_df['High'].idxmax()]['Datetime'].strftime('%Y-%m-%d')
                period_min = period_df['Low'].min()
                min_date = period_df.iloc[period_df['Low'].idxmin()]['Datetime'].strftime('%Y-%m-%d')
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'period_max': period_max,
                              'period_max_date': max_date,
                              'period_min': period_min,
                              'period_min_date': min_date,
                              'stochastic_df': stochastic_df,
                              'stochastic_ds': stochastic_ds,
                              'df>ds': stochastic_inequality,
                              'stock_bull': stock_bull,
                              'stock_bear': stock_bear,
                              'market_bull': market_bull,
                              'market_bear': market_bear}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['buy_signal'] and df.shift(-1).iloc[i]['Open'] > 1.0:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            stock_bull = df.iloc[i]['bull']
            stock_bear = df.iloc[i]['bear']
            signal_datetime = df.iloc[i]['Datetime']
            signal_spy_df = spy_df.loc[spy_df['Datetime'] == signal_datetime].copy()
            stochastic_df = df.iloc[i]['%DF']
            stochastic_ds = df.iloc[i]['%DS']
            stochastic_inequality = df.iloc[i]['%DF>%DS']
            if not signal_spy_df.empty:
                market_bull = signal_spy_df.iloc[0]['bull']
                market_bear = signal_spy_df.iloc[0]['bear']
            else:
                market_bull = None
                market_bear = None
            long_position = True
        i += 1

    print(ticker, cap)
    return trades, cap


def ma_roc_er_charting(ticker,
                       df,
                       sma1_period=5,
                       sma2_period=20,
                       sma1_uptrend_roc_period=5,
                       sma2_uptrend_roc_period=5,
                       sma1_uptrend_roc_th=3.0,
                       sma2_uptrend_roc_th=2.0,
                       sma1_uptrend_er_th=0.5,
                       sma2_uptrend_er_th=0.5,
                       sma1_downtrend_roc_period=5,
                       sma1_downtrend_roc_th=-3.0,
                       sma1_downtrend_er_th=0.2):
    from plotting.candlestick_chart import multiple_windows_chart, add_markers_to_candlestick_chart
    from dateutil.relativedelta import relativedelta
    from indicators.momentum_indicators import simple_moving_average, rsi, williams_r

    df = ma_roc_er_signals(df,
                           sma1_period=sma1_period,
                           sma2_period=sma2_period,
                           sma1_uptrend_roc_period=sma1_uptrend_roc_period,
                           sma2_uptrend_roc_period=sma2_uptrend_roc_period,
                           sma1_uptrend_roc_th=sma1_uptrend_roc_th,
                           sma2_uptrend_roc_th=sma2_uptrend_roc_th,
                           sma1_uptrend_er_th=sma1_uptrend_er_th,
                           sma2_uptrend_er_th=sma2_uptrend_er_th,
                           sma1_downtrend_roc_period=sma1_downtrend_roc_period,
                           sma1_downtrend_roc_th=sma1_downtrend_roc_th,
                           sma1_downtrend_er_th=sma1_downtrend_er_th)

    df = simple_moving_average(df, 200)
    df = rsi(df, 200)
    df = rsi(df, 50)
    df = rsi(df, 20)
    df = williams_r(df, 200)
    df = williams_r(df, 50)
    df = williams_r(df, 20)
    df[f'Williams_R%_200'] = df[f'Williams_R%_200'] + 100.0
    df[f'Williams_R%_50'] = df[f'Williams_R%_50'] + 100.0
    df[f'Williams_R%_20'] = df[f'Williams_R%_20'] + 100.0
    df[f'SMA{sma1_period}ROC_th'] = sma1_uptrend_roc_th
    df[f'SMA{sma2_period}ROC_th'] = sma2_uptrend_roc_th
    df[f'SMA{sma1_period}ER_UP_th'] = sma1_uptrend_er_th
    df[f'SMA{sma2_period}ER_UP_th'] = sma2_uptrend_er_th
    df[f'SMA{sma1_period}ER_DOWN_th'] = sma1_downtrend_er_th

    df[f'SMA200ROC5'] = ((df['SMA200'] - df.shift(5)['SMA200']) / df.shift(5)['SMA200']) * 100.0
    df[f'SMA200ER5'] = efficiency_ratio(df, 'SMA200', 5, inplace=False)
    df = simple_moving_average(df, 100)
    df[f'SMA100ROC5'] = ((df['SMA100'] - df.shift(5)['SMA100']) / df.shift(5)['SMA100']) * 100.0
    df[f'SMA100ER5'] = efficiency_ratio(df, 'SMA100', 5, inplace=False)

    df['Datetime'] = pd.to_datetime(df['Date'])
    i = 0
    long_position = False
    enter_price = None
    enter_date = None
    cap = 100.0

    trades = []

    while i < len(df):
        if long_position:
            if df.iloc[i]['sell_signal']:
                exit_price = df.shift(-1).iloc[i]['Open']
                if np.isnan(exit_price):
                    break
                exit_date = df.shift(-1).iloc[i]['Date']
                if np.isnan(exit_price):
                    long_position = False
                    continue
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = pd.DataFrame.copy(df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                                                     (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))])
                period_df.reset_index(inplace=True)
                period_max = period_df['High'].max()
                max_date = period_df.iloc[period_df['High'].idxmax()]['Datetime'].strftime('%Y-%m-%d')
                period_min = period_df['Low'].min()
                min_date = period_df.iloc[period_df['Low'].idxmin()]['Datetime'].strftime('%Y-%m-%d')
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'period_max': period_max,
                              'period_max_date': max_date,
                              'period_min': period_min,
                              'period_min_date': min_date,
                              'sma200roc': sma200roc,
                              'sma200er': sma200er,
                              'sma100roc': sma100roc,
                              'sma100er': sma100er,
                              'close_sma200_ratio': close_sma_200_ratio,
                              'close_sma100_ratio': close_sma_100_ratio}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False

                # Chart
                days_spacing = 5
                trade_period = (datetime.strptime(exit_date, '%Y-%m-%d') - datetime.strptime(enter_date, '%Y-%m-%d')).days
                chart_start = datetime.strptime(enter_date, '%Y-%m-%d') - relativedelta(days=days_spacing)
                chart_end = datetime.strptime(exit_date, '%Y-%m-%d') + relativedelta(days=days_spacing)
                chart_df = df.loc[(df['Datetime'] >= chart_start) & (df['Datetime'] <= chart_end)].copy()
                chart_df['Date'] = pd.to_datetime(chart_df['Date'])
                chart_dict = {(1, ''): [f'SMA{sma1_period}',
                                        f'SMA{sma2_period}',
                                        'SMA200'],
                              (2, 'Rate of Change'): [f'SMA{sma1_period}ROC{sma1_uptrend_roc_period}',
                                                      f'SMA{sma2_period}ROC{sma2_uptrend_roc_period}',
                                                      f'SMA{sma1_period}ROC_th',
                                                      f'SMA{sma2_period}ROC_th'],
                              (3, 'Efficiency Ratio'): [f'SMA{sma1_period}ER',
                                                        f'SMA{sma2_period}ER',
                                                        f'SMA{sma1_period}ER_UP_th',
                                                        f'SMA{sma2_period}ER_UP_th',
                                                        f'SMA{sma1_period}ER_DOWN_th'],
                              (4, 'Williams R% & RSI'): [f'Williams_R%_200',
                                                         f'Williams_R%_50',
                                                         f'Williams_R%_20',
                                                         'RSI200',
                                                         'RSI50',
                                                         'RSI20']}
                chart_df['sell_markers'] = np.where(chart_df['sell_signal'], chart_df['High']*1.001, np.nan)
                chart_df['buy_markers'] = np.where(chart_df['buy_signal'], chart_df['Low']*0.999, np.nan)
                fig = multiple_windows_chart(ticker, chart_df, chart_dict)
                fig = add_markers_to_candlestick_chart(fig, chart_df['Date'], chart_df['buy_markers'], 'BUY', 1)
                fig = add_markers_to_candlestick_chart(fig, chart_df['Date'], chart_df['sell_markers'], 'SELL', 0)
                fig.add_vline(x=enter_date, line_width=1, line_dash='dash')
                fig.add_vline(x=exit_date, line_width=1, line_dash='dash')
                fig.write_html(fr"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\ma_roc_er_charts\{ticker}_{enter_date}_to_{exit_date}_total_{trade_period}.html")
        elif df.iloc[i]['buy_signal'] and df.shift(-1).iloc[i]['Open'] != 0.0:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            sma200roc = df.iloc[i]['SMA200ROC5']
            sma200er = df.iloc[i]['SMA200ER5']
            sma100roc = df.iloc[i]['SMA100ROC5']
            sma100er = df.iloc[i]['SMA100ER5']
            close_sma_200_ratio = ((df.iloc[i]['Close'] - df.iloc[i]['SMA200']) / df.iloc[i]['SMA200']) * 100.0
            close_sma_100_ratio = ((df.iloc[i]['Close'] - df.iloc[i]['SMA100']) / df.iloc[i]['SMA100']) * 100.0
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


def ma_roc_er_trading(ticker,
                                 sma1_period=5,
                                 sma2_period=20,
                                 sma1_uptrend_roc_period=5,
                                 sma2_uptrend_roc_period=5,
                                 sma1_uptrend_roc_th=3.0,
                                 sma2_uptrend_roc_th=2.0,
                                 sma1_uptrend_er_th=0.5,
                                 sma2_uptrend_er_th=0.5,
                                 sma1_downtrend_roc_period=5,
                                 sma1_downtrend_roc_th=-3.0,
                                 sma1_downtrend_er_th=0.2):

    df = pd.read_csv(download_stock_day(ticker))

    df = ma_roc_er_signals(df,
                           sma1_period=sma1_period,
                           sma2_period=sma2_period,
                           sma1_uptrend_roc_period=sma1_uptrend_roc_period,
                           sma2_uptrend_roc_period=sma2_uptrend_roc_period,
                           sma1_uptrend_roc_th=sma1_uptrend_roc_th,
                           sma2_uptrend_roc_th=sma2_uptrend_roc_th,
                           sma1_uptrend_er_th=sma1_uptrend_er_th,
                           sma2_uptrend_er_th=sma2_uptrend_er_th,
                           sma1_downtrend_roc_period=sma1_downtrend_roc_period,
                           sma1_downtrend_roc_th=sma1_downtrend_roc_th,
                           sma1_downtrend_er_th=sma1_downtrend_er_th)

    df['Datetime'] = pd.to_datetime(df['Date'])

    return signal_trading_manager_long(ticker, df)


def ma_roc_er_trading_strategy_test(tickers,
                                    dataframe_length,
                                    sma1_period=5,
                                    sma2_period=20,
                                    sma1_uptrend_roc_period=5,
                                    sma2_uptrend_roc_period=5,
                                    sma1_uptrend_roc_th=3.0,
                                    sma2_uptrend_roc_th=2.0,
                                    sma1_uptrend_er_th=0.5,
                                    sma2_uptrend_er_th=0.5,
                                    sma1_downtrend_roc_period=5,
                                    sma1_downtrend_roc_th=-3.0,
                                    sma1_downtrend_er_th=0.2):

    strategy_name = f'ma_roc_and_efficiency_ratio_trading'
    strategy_parameters = {'sma1_period': sma1_period,
                           'sma2_period': sma2_period,
                           'sma1_uptrend_roc_period': sma1_uptrend_roc_period,
                           'sma2_uptrend_roc_period': sma2_uptrend_roc_period,
                           'sma1_uptrend_roc_th': sma1_uptrend_roc_th,
                           'sma2_uptrend_roc_th': sma2_uptrend_roc_th,
                           'sma1_uptrend_er_th': sma1_uptrend_er_th,
                           'sma2_uptrend_er_th': sma2_uptrend_er_th,
                           'sma1_downtrend_roc_period': sma1_downtrend_roc_period,
                           'sma1_downtrend_roc_th': sma1_downtrend_roc_th,
                           'sma1_downtrend_er_th': sma1_downtrend_er_th,
                           'dataframe_length': dataframe_length}

    run_time = datetime.now().strftime('%d-%m-%Y-%H-%M-%S')

    with open(save_under_results_path(f'{strategy_name}_{run_time}.json'), 'w') as f:
        json.dump(strategy_parameters, f, indent=4)

    all_trades = []
    ticker_returns = []

    for ticker in tickers:
        try:
            # df = pd.read_csv(download_stock_day(ticker)).reset_index()
            df = yf.Ticker(ticker).history(period='max', interval='1d')
            if len(df) > dataframe_length:
                df = df[-dataframe_length:].reset_index()
            else:
                df = df.reset_index()
        except ValueError:
            continue

        trades, final_cap = ma_roc_er_trading(ticker,
                                              df,
                                              sma1_period=sma1_period,
                                              sma2_period=sma2_period,
                                              sma1_uptrend_roc_period=sma1_uptrend_roc_period,
                                              sma2_uptrend_roc_period=sma2_uptrend_roc_period,
                                              sma1_uptrend_roc_th=sma1_uptrend_roc_th,
                                              sma2_uptrend_roc_th=sma2_uptrend_roc_th,
                                              sma1_uptrend_er_th=sma1_uptrend_er_th,
                                              sma2_uptrend_er_th=sma2_uptrend_er_th,
                                              sma1_downtrend_roc_period=sma1_downtrend_roc_period,
                                              sma1_downtrend_roc_th=sma1_downtrend_roc_th,
                                              sma1_downtrend_er_th=sma1_downtrend_er_th)

        all_trades = all_trades + trades
        ticker_returns.append(
            {'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0})
        pd.DataFrame(all_trades).to_csv(
            save_under_results_path(f'{strategy_name}_{run_time}_all_trades.csv'))
        pd.DataFrame(ticker_returns).to_csv(
            save_under_results_path(f'{strategy_name}_{run_time}_ticker_returns.csv'))

    return save_under_results_path(f'{strategy_name}_{run_time}_all_trades.csv')


def count_strategy_signals_for_each_month(tickers,
                                    dataframe_length,
                                    sma1_period=5,
                                    sma2_period=20,
                                    sma1_uptrend_roc_period=5,
                                    sma2_uptrend_roc_period=5,
                                    sma1_uptrend_roc_th=3.0,
                                    sma2_uptrend_roc_th=2.0,
                                    sma1_uptrend_er_th=0.5,
                                    sma2_uptrend_er_th=0.5,
                                    sma1_downtrend_roc_period=5,
                                    sma1_downtrend_roc_th=-3.0,
                                    sma1_downtrend_er_th=0.2):
    """
    I checked and there are too many entry signals. For example: between ~01-07-2022 and ~09-09-2022 there were
    more than 1700 entry signals.
    So given the good results and the fact that filtering entry signals shouldn't affect the results much, I want
    to find a qualitative filter that will increase my winning rate and profit factor. So I have this function
    to verify that I did decrease the number of entry signals.
    Also, this could show the fact that there are a lot of entry signals when there is a bear market just like now.
    """

    strategy_name = f'ma_roc_and_efficiency_ratio_trading'
    strategy_parameters = {'sma1_period': sma1_period,
                           'sma2_period': sma2_period,
                           'sma1_uptrend_roc_period': sma1_uptrend_roc_period,
                           'sma2_uptrend_roc_period': sma2_uptrend_roc_period,
                           'sma1_uptrend_roc_th': sma1_uptrend_roc_th,
                           'sma2_uptrend_roc_th': sma2_uptrend_roc_th,
                           'sma1_uptrend_er_th': sma1_uptrend_er_th,
                           'sma2_uptrend_er_th': sma2_uptrend_er_th,
                           'sma1_downtrend_roc_period': sma1_downtrend_roc_period,
                           'sma1_downtrend_roc_th': sma1_downtrend_roc_th,
                           'sma1_downtrend_er_th': sma1_downtrend_er_th,
                           'dataframe_length': dataframe_length}

    run_time = datetime.now().strftime('%d-%m-%Y-%H-%M-%S')

    month_year_total_signals_counter = {}

    for ticker in tickers:
        try:
            # df = pd.read_csv(download_stock_day(ticker)).reset_index()
            df = yf.Ticker(ticker).history(period='max', interval='1d')
            if len(df) > dataframe_length:
                df = df[-dataframe_length:].reset_index()
            else:
                df = df.reset_index()
        except ValueError:
            continue

        df = ma_roc_er_signals(df,
                               sma1_period=sma1_period,
                               sma2_period=sma2_period,
                               sma1_uptrend_roc_period=sma1_uptrend_roc_period,
                               sma2_uptrend_roc_period=sma2_uptrend_roc_period,
                               sma1_uptrend_roc_th=sma1_uptrend_roc_th,
                               sma2_uptrend_roc_th=sma2_uptrend_roc_th,
                               sma1_uptrend_er_th=sma1_uptrend_er_th,
                               sma2_uptrend_er_th=sma2_uptrend_er_th,
                               sma1_downtrend_roc_period=sma1_downtrend_roc_period,
                               sma1_downtrend_roc_th=sma1_downtrend_roc_th,
                               sma1_downtrend_er_th=sma1_downtrend_er_th)

        df['Datetime'] = pd.to_datetime(df['Date'])
        df['month_year'] = df['Datetime'].dt.strftime('%m-%Y')
        month_year_list = df['month_year'].unique().tolist()

        for month_year in month_year_list:

            month_year_datetime = datetime.strptime(month_year, '%m-%Y')
            if month_year_datetime not in month_year_total_signals_counter.keys():
                month_year_total_signals_counter[month_year_datetime] = {'buy_signals': 0,
                                                                      'sell_signals': 0}

            month_df = df.loc[df['month_year'] == month_year].copy()
            buy_signals = len(month_df.loc[month_df['buy_signal']])
            sell_signals = len(month_df.loc[month_df['sell_signal']])
            print(ticker, month_year, buy_signals, sell_signals)

            month_year_total_signals_counter[month_year_datetime]['buy_signals'] += buy_signals
            month_year_total_signals_counter[month_year_datetime]['sell_signals'] += sell_signals

    month_year_total_signals_dict = {'month_year': [], 'buy_signals': [], 'sell_signals': []}
    for month_year_datetime in month_year_total_signals_counter.keys():
        month_year_total_signals_dict['month_year'].append(month_year_datetime)
        month_year_total_signals_dict['buy_signals'].append(
            month_year_total_signals_counter[month_year_datetime]['buy_signals'])
        month_year_total_signals_dict['sell_signals'].append(
            month_year_total_signals_counter[month_year_datetime]['sell_signals'])

    pd.DataFrame(month_year_total_signals_dict).to_csv(
        save_under_results_path(f'{strategy_name}_{run_time}_signals_per_month.csv'))


if __name__ == "__main__":
    from utils.get_all_stocks import in_sample_tickers, large_cap_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    from strategy_statistics.strategy_statistics import all_statistics_dict
    import itertools
    import yfinance as yf
    import json
    import concurrent.futures
    from datetime import datetime
    from itertools import repeat

    def days_available(ticker):
        """
        Returns the 1h timeframe with maxiumum days available
        """
        max_days = False
        current_max = 730
        step = int(np.ceil(current_max/2))
        while not max_days:
            # print('current max', current_max)
            # print('current step', step)
            df = yf.Ticker(ticker).history(period=f'{current_max}d', interval='1h').reset_index()
            if df.empty:
                current_max = current_max - step
                step = int(np.ceil(step / 2))
            else:
                last_available_max = current_max
                if last_available_max == 730:
                    max_days = True
                elif not step == 1:
                    current_max = current_max + step
                    step = int(np.ceil(step / 2))
                else:
                    max_days = True
        return df


    tickers = in_sample_tickers()
    all_trades = []

    sma1_period = 5
    sma2_period = 10
    sma1_uptrend_roc_period = 3
    sma2_uptrend_roc_period = 3
    sma1_uptrend_roc_th = 2.0
    sma2_uptrend_roc_th = 10.0
    sma1_uptrend_er_th = 0.5
    sma2_uptrend_er_th = 0.8
    sma1_downtrend_roc_period = 15
    sma1_downtrend_roc_th = -5.0
    sma1_downtrend_er_th = 0.2

    combination_str = f'{sma1_period}_{sma2_period}_{sma1_uptrend_roc_period}_{sma2_uptrend_roc_period}_{sma1_uptrend_roc_th}_{sma2_uptrend_roc_th}_{sma1_uptrend_er_th}_{sma2_uptrend_er_th}_{sma1_downtrend_roc_period}_{sma1_downtrend_roc_th}_{sma1_downtrend_er_th}'

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(ma_roc_er_trading,
                               tickers,
                               repeat(sma1_period),
                               repeat(sma2_period),
                               repeat(sma1_uptrend_roc_period),
                               repeat(sma2_uptrend_roc_period),
                               repeat(sma1_uptrend_roc_th),
                               repeat(sma2_uptrend_roc_th),
                               repeat(sma1_uptrend_er_th),
                               repeat(sma2_uptrend_er_th),
                               repeat(sma1_downtrend_roc_period),
                               repeat(sma1_downtrend_roc_th),
                               repeat(sma1_downtrend_er_th))

        for result in results:
            all_trades = all_trades + result[0]

    pd.DataFrame(all_trades).to_csv(save_under_results_path(f'ma_roc_er_trading_optimized_{combination_str}_all_trades.csv'))
