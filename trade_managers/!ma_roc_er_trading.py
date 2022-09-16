import os.path

import pandas as pd
import numpy as np
from datetime import datetime
from measurements.noise_measurements import efficiency_ratio
from indicators.momentum_indicators import simple_moving_average
from trade_managers.signal_trading_manager import signal_trading_manager_long
import json


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


def ma_roc_er_trading(ticker,
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
                         sma2_downtrend_roc_period=5,
                         sma1_downtrend_roc_th=-3.0,
                         sma2_downtrend_roc_th=-2.0,
                         sma1_downtrend_er_th=0.2,
                         sma2_downtrend_er_th=0.2):

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
    df[f'SMA{sma1_period}ER'] = efficiency_ratio(df, f'SMA{sma1_period}', sma1_uptrend_roc_period, inplace=False)
    df[f'SMA{sma2_period}ER'] = efficiency_ratio(df, f'SMA{sma2_period}', sma2_uptrend_roc_period, inplace=False)

    df['sell_signal'] = np.where((df[f'SMA{sma1_period}ROC{sma1_uptrend_roc_period}'] > sma1_uptrend_roc_th) &
                                 (df[f'SMA{sma2_period}ROC{sma2_uptrend_roc_period}'] > sma2_uptrend_roc_th) &
                                 (df[f'SMA{sma1_period}ER'] > sma1_uptrend_er_th) &
                                 (df[f'SMA{sma2_period}ER'] > sma2_uptrend_er_th), True, False)
    df['buy_signal'] = np.where((df[f'SMA{sma1_period}ROC{sma1_downtrend_roc_period}'] < sma1_downtrend_roc_th) &
                                (df[f'SMA{sma2_period}ER'] > sma2_downtrend_er_th), 1, 0)

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
                         sma2_downtrend_roc_period=5,
                         sma1_downtrend_roc_th=-3.0,
                         sma2_downtrend_roc_th=-2.0,
                         sma1_downtrend_er_th=0.2,
                         sma2_downtrend_er_th=0.2):

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
                              sma2_downtrend_roc_period=sma2_downtrend_roc_period,
                              sma1_downtrend_roc_th=sma1_downtrend_roc_th,
                              sma2_downtrend_roc_th=sma2_downtrend_roc_th,
                              sma1_downtrend_er_th=sma1_downtrend_er_th,
                              sma2_downtrend_er_th=sma2_downtrend_er_th)

    return signal_trading_manager_long(ticker, df)


def ma_roc_er_trading_strategy_test_v2(tickers,
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
                                       sma2_downtrend_roc_period=5,
                                       sma1_downtrend_roc_th=-3.0,
                                       sma2_downtrend_roc_th=-2.0,
                                       sma1_downtrend_er_th=0.2,
                                       sma2_downtrend_er_th=0.2):

    strategy_name = f'ma_roc_and_efficiency_ratio_trading_v2'
    strategy_parameters = {'sma1_period': sma1_period,
                           'sma2_period': sma2_period,
                           'sma1_uptrend_roc_period': sma1_uptrend_roc_period,
                           'sma2_uptrend_roc_period': sma2_uptrend_roc_period,
                           'sma1_uptrend_roc_th': sma1_uptrend_roc_th,
                           'sma2_uptrend_roc_th': sma2_uptrend_roc_th,
                           'sma1_uptrend_er_th': sma1_uptrend_er_th,
                           'sma2_uptrend_er_th': sma2_uptrend_er_th,
                           'sma1_downtrend_roc_period': sma1_downtrend_roc_period,
                           'sma2_downtrend_roc_period': sma2_downtrend_roc_period,
                           'sma1_downtrend_roc_th': sma1_downtrend_roc_th,
                           'sma2_downtrend_roc_th': sma2_downtrend_roc_th,
                           'sma1_downtrend_er_th': sma1_downtrend_er_th,
                           'sma2_downtrend_er_th': sma2_downtrend_er_th,
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


def count_strategy_signals_for_each_month_v2(tickers,
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
                                             sma2_downtrend_roc_period=5,
                                             sma1_downtrend_roc_th=-3.0,
                                             sma2_downtrend_roc_th=-2.0,
                                             sma1_downtrend_er_th=0.2,
                                             sma2_downtrend_er_th=0.2):
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

    with open(save_under_results_path(f'{strategy_name}_{run_time}.json'), 'w') as f:
        json.dump(strategy_parameters, f, indent=4)

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
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, \
        get_all_dow_jones_industrial_stocks, get_all_nyse_composite_stocks
    from utils.download_stock_csvs import download_stock_day, download_stock_minute_data
    from utils.paths import save_under_results_path
    from indicators.momentum_indicators import rate_of_change, simple_moving_average
    from trade_managers.signal_trading_manager import signal_trading_manager_long, signal_trading_manager_short
    from plotting.candlestick_chart import multiple_windows_chart, add_markers_to_candlestick_chart
    import pandas as pd
    import numpy as np
    from datetime import datetime
    import json
    import time
    import yfinance as yf
    import json
    import glob
    import random

    # start_time = time.time()

    # tickers = list(set(get_all_nasdaq_100_stocks() + get_all_dow_jones_industrial_stocks() + ['SPY'] + get_all_nyse_composite_stocks()))

    # tickers = get_all_nasdaq_100_stocks()

    # count_strategy_signals_for_each_month(tickers=tickers,
    #                                       dataframe_length=252)

    # v2_path = ma_roc_er_trading_strategy_test_v2(tickers, 2016)
    # v1_path = ma_roc_er_trading_strategy_test(tickers, 2016)

    # print(v1_path, v2_path)
    # print(time.time() - start_time)

    sma1_period_list = list(range(2, 6, 1))
    sma2_period_list = list(range(3, 11, 1))
    sma1_uptrend_roc_period_list = list(range(2, 7, 1))
    sma2_uptrend_roc_period_list = list(range(2, 7, 1))
    sma1_uptrend_roc_th_list = list(np.arange(0.2, 1.0, 0.1))
    sma2_uptrend_roc_th_list = list(np.arange(0.2, 1.0, 0.1))
    sma1_uptrend_er_th_list = list(np.arange(0.2, 1.0, 0.1))
    sma2_uptrend_er_th_list = list(np.arange(0.2, 1.0, 0.1))
    sma1_downtrend_roc_period_list = list(range(2, 6, 1))
    sma1_downtrend_roc_th_list = list(np.arange(-1.0, -0.2, 0.1))
    sma1_downtrend_er_th_list = list(np.arange(0.2, 1.0, 0.1))

    total_loops = len(sma1_period_list)*len(sma2_period_list)*len(sma1_uptrend_roc_period_list)*len(sma2_uptrend_roc_period_list)*len(sma1_uptrend_roc_th_list)* \
        len(sma2_uptrend_roc_th_list)*len(sma1_uptrend_er_th_list)*len(sma2_uptrend_er_th_list)*len(sma1_downtrend_roc_period_list)*\
        len(sma1_downtrend_roc_th_list)*len(sma1_downtrend_er_th_list)

    print(f'num loops: {total_loops}')

    for sma1_period in sma1_period_list:
        for sma2_period in sma2_period_list:
            for sma1_uptrend_roc_period in sma1_uptrend_roc_period_list:
                for sma2_uptrend_roc_period in sma2_uptrend_roc_period_list:
                    for sma1_uptrend_roc_th in sma1_uptrend_roc_th_list:
                        for sma2_uptrend_roc_th in sma2_uptrend_roc_th_list:
                            for sma1_uptrend_er_th in sma1_uptrend_er_th_list:
                                for sma2_uptrend_er_th in sma2_uptrend_er_th_list:
                                    for sma1_downtrend_roc_period in sma1_downtrend_roc_period_list:
                                        for sma1_downtrend_roc_th in sma1_downtrend_roc_th_list:
                                            for sma1_downtrend_er_th in sma1_downtrend_er_th_list:

                                                # sma1_period = 3
                                                # sma2_period = 5
                                                # sma1_uptrend_roc_period = 5
                                                # sma2_uptrend_roc_period = 5
                                                # sma1_uptrend_roc_th = 0.5
                                                # sma2_uptrend_roc_th = 0.5
                                                # sma1_uptrend_er_th = 0.5
                                                # sma2_uptrend_er_th = 0.5
                                                # sma1_downtrend_roc_period = 5
                                                # sma1_downtrend_roc_th = -0.5
                                                # sma1_downtrend_er_th = 0.8

                                                dataframe_length = None

                                                strategy_name = f'ma_roc_and_efficiency_ratio_trading_minute_timeframe'
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

                                                tickers = get_all_nasdaq_100_stocks()

                                                all_trades = []
                                                ticker_returns = []

                                                for ticker in tickers:
                                                    df = pd.read_csv(download_stock_minute_data(ticker))
                                                    if df.empty:
                                                        continue
                                                    df['Datetime'] = pd.to_datetime(df['Datetime'])
                                                    df['Date'] = pd.to_datetime(df['Datetime'])
                                                    df = ma_roc_er_signals(df, sma1_period=3, sma2_period=5)
                                                    # df.to_csv(save_under_results_path(f'{ticker}_minute_ma_roc_er.csv'))
                                                    trades, final_cap = signal_trading_manager_long(ticker, df)
                                                    pd.DataFrame(all_trades).to_csv(
                                                        save_under_results_path(f'{strategy_name}_{run_time}_all_trades.csv'))
                                                    pd.DataFrame(ticker_returns).to_csv(
                                                        save_under_results_path(f'{strategy_name}_{run_time}_ticker_returns.csv'))

        # df['buy_markers'] = np.where(df['buy_signal'], df['Low']*0.95, np.nan)
        # df['sell_markers'] = np.where(df['sell_signal'], df['High']*1.05, np.nan)
        # chart_dict = {(1, 'stam'): ['SMA5', 'SMA20'],
        #               (2, 'Rate of Change'): ['SMA5ROC5', 'SMA20ROC5'],
        #               (3, 'Efficiency Ratio'): ['SMA5ER', 'SMA20ER']}
        # fig = multiple_windows_chart(ticker, df, chart_dict)
        # fig = add_markers_to_candlestick_chart(fig, df['Date'], df['buy_markers'], 'BUY', 1)
        # fig = add_markers_to_candlestick_chart(fig, df['Date'], df['sell_markers'], 'SELL', 0)
        # fig.write_html(fr"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\ma_roc_er_charts\{ticker}_minute.html")

    # Checking on delisted stocks
    # sma1_period = 5
    # sma2_period = 20
    # sma1_uptrend_roc_period = 5
    # sma2_uptrend_roc_period = 5
    # sma1_uptrend_roc_th = 3.0
    # sma2_uptrend_roc_th = 2.0
    # sma1_uptrend_er_th = 0.5
    # sma2_uptrend_er_th = 0.5
    # sma1_downtrend_roc_period = 5
    # sma1_downtrend_roc_th = -3.0
    # sma1_downtrend_er_th = 0.2
    #
    # dataframe_length = None
    #
    # strategy_name = f'ma_roc_and_efficiency_ratio_trading_minute_timeframe'
    # strategy_parameters = {'sma1_period': sma1_period,
    #                        'sma2_period': sma2_period,
    #                        'sma1_uptrend_roc_period': sma1_uptrend_roc_period,
    #                        'sma2_uptrend_roc_period': sma2_uptrend_roc_period,
    #                        'sma1_uptrend_roc_th': sma1_uptrend_roc_th,
    #                        'sma2_uptrend_roc_th': sma2_uptrend_roc_th,
    #                        'sma1_uptrend_er_th': sma1_uptrend_er_th,
    #                        'sma2_uptrend_er_th': sma2_uptrend_er_th,
    #                        'sma1_downtrend_roc_period': sma1_downtrend_roc_period,
    #                        'sma1_downtrend_roc_th': sma1_downtrend_roc_th,
    #                        'sma1_downtrend_er_th': sma1_downtrend_er_th,
    #                        'dataframe_length': dataframe_length}
    #
    # run_time = datetime.now().strftime('%d-%m-%Y-%H-%M-%S')
    #
    # tickers = get_all_nasdaq_100_stocks()
    #
    # with open(save_under_results_path(f'{strategy_name}_{run_time}.json'), 'w') as f:
    #     json.dump(strategy_parameters, f, indent=4)
    #
    # all_trades = []
    # ticker_returns = []
    #
    # for ticker in tickers:
    #     try:
    #         # df = pd.read_csv(download_stock_day(ticker)).reset_index()
    #         # df = yf.Ticker(ticker).history(period='max', interval='1d')
    #         df = pd.read_csv(download_stock_minute_data(ticker))
    #         # if len(df) > dataframe_length:
    #         #     df = df[-dataframe_length:].reset_index()
    #         # else:
    #         #     df = df.reset_index()
    #     except ValueError:
    #         continue
    #     df['Datetime'] = pd.to_datetime(df['Datetime'])
    #     df['Date'] = pd.to_datetime(df['Datetime'])
    #     trades, final_cap = ma_roc_er_trading(ticker,
    #                                           df,
    #                                           sma1_period=sma1_period,
    #                                           sma2_period=sma2_period,
    #                                           sma1_uptrend_roc_period=sma1_uptrend_roc_period,
    #                                           sma2_uptrend_roc_period=sma2_uptrend_roc_period,
    #                                           sma1_uptrend_roc_th=sma1_uptrend_roc_th,
    #                                           sma2_uptrend_roc_th=sma2_uptrend_roc_th,
    #                                           sma1_uptrend_er_th=sma1_uptrend_er_th,
    #                                           sma2_uptrend_er_th=sma2_uptrend_er_th,
    #                                           sma1_downtrend_roc_period=sma1_downtrend_roc_period,
    #                                           sma1_downtrend_roc_th=sma1_downtrend_roc_th,
    #                                           sma1_downtrend_er_th=sma1_downtrend_er_th)
    #
    #     all_trades = all_trades + trades
    #     ticker_returns.append(
    #         {'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0})
    #     pd.DataFrame(all_trades).to_csv(
    #         save_under_results_path(f'{strategy_name}_{run_time}_all_trades.csv'))
    #     pd.DataFrame(ticker_returns).to_csv(
    #         save_under_results_path(f'{strategy_name}_{run_time}_ticker_returns.csv'))

    # delisted_stock_csv_dir = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\stocks_minute_history\minute_to_day_conversion"
    #
    # delisted_stock_csvs = glob.glob(delisted_stock_csv_dir + '/*.csv')
    #
    # random_hundred_stocks = random.choices(delisted_stock_csvs, k=100)
    #
    # all_trades = []
    # ticker_returns = []
    #
    # for stock in random_hundred_stocks:
    #     ticker = str(os.path.basename(stock)).replace('.csv', '')
    #     df = pd.read_csv(stock)
    #     df = ma_roc_er_signals(df)
    #
    #     trades, final_cap = signal_trading_manager_long(ticker, df)
    #
    #     all_trades = all_trades + trades
    #     ticker_returns.append(
    #         {'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0})
    #     pd.DataFrame(all_trades).to_csv(
    #         save_under_results_path(f'{strategy_name}_{run_time}_all_trades.csv'))
    #     pd.DataFrame(ticker_returns).to_csv(
    #         save_under_results_path(f'{strategy_name}_{run_time}_ticker_returns.csv'))


