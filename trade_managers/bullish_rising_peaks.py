import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from detectors.peaks_and_toughs import is_peak_loose, is_tough_loose, is_peak_definitive, is_tough_definitive
from indicators.momentum_indicators import simple_moving_average, rsi, stochastic, awesome_oscillator
from utils.download_stock_csvs import download_stock_week
import pandas as pd
import numpy as np


def bullish_rising_peaks_v1(ticker, df, peaks_ratio=1.05):

    df['max14'] = df['High'].rolling(14).max()
    df['min14'] = df['Low'].rolling(14).min()
    df['Datetime'] = pd.to_datetime(df['Date'])

    first_peak = None
    second_peak = None
    tough = None
    peak_tough_peak = False
    long_position = False
    stop_loss = None

    cap = 100.0
    trades = []

    i = 0
    while i < len(df)-2:
        if long_position:
            if df.iloc[i]['Low'] < stop_loss:
                if df.iloc[i]['Open'] < stop_loss:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = stop_loss
                exit_date = df.iloc[i]['Date']
                long_position = False
                peak_tough_peak = False
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'stop_loss': stop_loss,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'period_max': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                              (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['High'].max(),
                              'period_min': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['Low'].min(),
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
        if peak_tough_peak:
            if not long_position:
                if second_peak['Price'] <= df.iloc[i]['High']:
                    # TODO: remove print
                    # print(f'peak tough peak: {first_peak} {tough} {second_peak}')
                    if second_peak['Price'] <= df.iloc[i]['Open']:
                        enter_price = df.iloc[i]['Open']
                    else:
                        enter_price = second_peak['Price']
                    enter_date = df.iloc[i]['Date']
                    stop_loss = tough['Price']*0.98
                    long_position = True
                    peak_tough_peak = False
                    first_peak = None
                    second_peak = None
                    tough = None
            else:
                stop_loss = tough['Price']*0.98
                # TODO: remove print
                # print(f'new stop_loss: {stop_loss} {tough["Date"]}')
                peak_tough_peak = False
        elif is_peak_definitive(df, i):
            current_peak = df.iloc[i]['High']
            current_peak_date = df.iloc[i]['Date']
            if first_peak is None:
                first_peak = {'Date': current_peak_date, 'Price': current_peak}
            elif current_peak >= first_peak['Price']*peaks_ratio and tough is not None and second_peak is None:
                second_peak = {'Date': current_peak_date, 'Price': current_peak}
                peak_tough_peak = True
            else:
                first_peak = None
                second_peak = None
                tough = None
        elif is_tough_definitive(df, i):
            current_tough = df.iloc[i]['Low']
            current_tough_date = df.iloc[i]['Date']
            if tough is None and first_peak is not None and current_tough > df.iloc[i]['min14']:
                if current_tough < first_peak['Price']:
                    tough = {'Date': current_tough_date, 'Price': current_tough}
                else:
                    first_peak = None
                    second_peak = None
                    tough = None
            else:
                first_peak = None
                second_peak = None
                tough = None
        i += 1

    print(ticker, cap)
    return trades, cap


def bullish_rising_peaks_v1_refined(ticker, df, peaks_ratio=1.05):

    df['max14'] = df['High'].rolling(14).max()
    df['min14'] = df['Low'].rolling(14).min()
    df['Datetime'] = pd.to_datetime(df['Date'])

    first_peak = None
    second_peak = None
    tough = None
    peak_tough_peak = False
    long_position = False
    stop_loss = None
    risky_position = False

    cap = 100.0
    trades = []

    i = 0
    while i < len(df)-2:
        if long_position:
            if df.iloc[i]['Low'] < stop_loss:
                if df.iloc[i]['Open'] < stop_loss:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = stop_loss
                exit_date = df.iloc[i]['Date']
                long_position = False
                peak_tough_peak = False
                # Position management
                if risky_position:
                    cap = 0.5*cap + 0.5*cap * (1.0 + ((exit_price - enter_price) / enter_price))
                else:
                    cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                risky_position = False
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'initial_stop_loss_risk': initial_stop_loss_risk,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'period_max': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                              (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['High'].max(),
                              'period_min': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['Low'].min(),
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
        if peak_tough_peak:
            if not long_position:
                if second_peak['Price'] <= df.iloc[i]['High']:
                    # TODO: remove print
                    # print(f'peak tough peak: {first_peak} {tough} {second_peak}')
                    if second_peak['Price'] <= df.iloc[i]['Open']:
                        enter_price = df.iloc[i]['Open']
                    else:
                        enter_price = second_peak['Price']
                    enter_date = df.iloc[i]['Date']
                    stop_loss = tough['Price']*0.98
                    initial_stop_loss_risk = ((stop_loss - enter_price)/enter_price)*100.0
                    if initial_stop_loss_risk < -11.0:
                        risky_position = True
                    long_position = True
                    peak_tough_peak = False
                    first_peak = None
                    second_peak = None
                    tough = None
            else:
                stop_loss = tough['Price']*0.98
                # TODO: remove print
                # print(f'new stop_loss: {stop_loss} {tough["Date"]}')
                peak_tough_peak = False
        elif is_peak_definitive(df, i):
            current_peak = df.iloc[i]['High']
            current_peak_date = df.iloc[i]['Date']
            if first_peak is None:
                first_peak = {'Date': current_peak_date, 'Price': current_peak}
            elif current_peak >= first_peak['Price']*peaks_ratio and tough is not None and second_peak is None:
                second_peak = {'Date': current_peak_date, 'Price': current_peak}
                peak_tough_peak = True
            else:
                first_peak = None
                second_peak = None
                tough = None
        elif is_tough_definitive(df, i):
            current_tough = df.iloc[i]['Low']
            current_tough_date = df.iloc[i]['Date']
            if tough is None and first_peak is not None and current_tough > df.iloc[i]['min14']:
                if current_tough < first_peak['Price']:
                    tough = {'Date': current_tough_date, 'Price': current_tough}
                else:
                    first_peak = None
                    second_peak = None
                    tough = None
            else:
                first_peak = None
                second_peak = None
                tough = None
        i += 1

    print(ticker, cap)
    return trades, cap


def bullish_rising_peaks_v2(ticker, df, peaks_ratio=1.05):  # Depracted because 'is_peak/tough_definitive' were changed

    df['max14'] = df['High'].rolling(14).max()
    df['min14'] = df['Low'].rolling(14).min()
    df['Datetime'] = pd.to_datetime(df['Date'])

    first_peak = None
    second_peak = None
    tough = None
    peak_tough_peak = False
    long_position = False
    stop_loss = None
    take_partial_profit = None
    took_partial_profit = False
    partial_exit_price = None
    partial_exit_date = None

    cap = 100.0
    trades = []

    i = 0
    while i < len(df)-2:
        if long_position:
            if df.iloc[i]['Low'] < stop_loss:
                if df.iloc[i]['Open'] < stop_loss:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = stop_loss
                exit_date = df.iloc[i]['Date']
                if took_partial_profit:
                    cap = 0.5*cap*1.1 + 0.5*cap*(1.0 + ((exit_price - enter_price) / enter_price))
                    change = 55.0 + 50.0*(1.0 + ((exit_price - enter_price) / enter_price)) -100.0
                else:
                    cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                    change = ((exit_price - enter_price) / enter_price) * 100
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'partial_exit_price': partial_exit_price,
                              'partial_exit_date': partial_exit_date,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'period_max': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d') - relativedelta(days=3)) &
                              (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['High'].max(),
                              'period_min': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d') - relativedelta(days=3)) &
                                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['Low'].min(),
                              'win': change > 0,
                              'change%': change}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
                peak_tough_peak = False
                took_partial_profit = False
                partial_exit_price = None
                partial_exit_date = None
            elif df.iloc[i]['High'] > take_partial_profit:
                if df.iloc[i]['Open'] > take_partial_profit:
                    partial_exit_price = df.iloc[i]['Open']
                else:
                    partial_exit_price = take_partial_profit
                partial_exit_date = df.iloc[i]['Date']
                took_partial_profit = True
        if peak_tough_peak:
            if not long_position:
                if second_peak['Price'] <= df.iloc[i]['High']:
                    # TODO: remove print
                    # print(f'peak tough peak: {first_peak} {tough} {second_peak}')
                    if second_peak['Price'] <= df.iloc[i]['Open']:
                        enter_price = df.iloc[i]['Open']
                    else:
                        enter_price = second_peak['Price']
                    enter_date = df.iloc[i]['Date']
                    stop_loss = tough['Price']*0.98
                    take_partial_profit = enter_price*1.095
                    long_position = True
                    peak_tough_peak = False
                    first_peak = None
                    second_peak = None
                    tough = None
            else:
                stop_loss = tough['Price']*0.98
                # TODO: remove print
                # print(f'new stop_loss: {stop_loss} {tough["Date"]}')
                peak_tough_peak = False
        elif is_peak_definitive(df, i):
            current_peak = df.shift(2).iloc[i]['High']
            if first_peak is None:
                first_peak = {'Date': df.shift(2).iloc[i]['Date'], 'Price': current_peak}
            elif current_peak >= first_peak['Price']*peaks_ratio and tough is not None and second_peak is None:
                second_peak = {'Date': df.shift(2).iloc[i]['Date'], 'Price': current_peak}
                peak_tough_peak = True
            else:
                first_peak = None
                second_peak = None
                tough = None
        elif is_tough_definitive(df, i):
            current_tough = df.shift(2).iloc[i]['Low']
            if tough is None and first_peak is not None and current_tough > df.iloc[i]['min14']:
                if current_tough < first_peak['Price']:
                    tough = {'Date': df.shift(2).iloc[i]['Date'], 'Price': current_tough}
                else:
                    first_peak = None
                    second_peak = None
                    tough = None
            else:
                first_peak = None
                second_peak = None
                tough = None
        i += 1

    print(ticker, cap)
    return trades, cap


def bullish_rising_peaks_v3(ticker, df, peaks_ratio=1.05):  # Depracted because 'is_peak/tough_definitive' were changed

    df['max14'] = df['High'].rolling(14).max()
    df['min14'] = df['Low'].rolling(14).min()
    df['Datetime'] = pd.to_datetime(df['Date'])

    first_peak = None
    second_peak = None
    tough = None
    peak_tough_peak = False
    long_position = False
    stop_loss = None
    take_profit = None

    cap = 100.0
    trades = []

    i = 0
    while i < len(df)-2:
        if long_position:
            if df.iloc[i]['Low'] < stop_loss:
                if df.iloc[i]['Open'] < stop_loss:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = stop_loss
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                change = ((exit_price - enter_price) / enter_price) * 100
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'period_max': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d') - relativedelta(days=3)) &
                              (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['High'].max(),
                              'period_min': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d') - relativedelta(days=3)) &
                                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['Low'].min(),
                              'win': change > 0,
                              'change%': change}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
                peak_tough_peak = False
                took_partial_profit = False
                partial_exit_price = None
                partial_exit_date = None
            elif df.iloc[i]['High'] > take_profit:
                if df.iloc[i]['Open'] > take_profit:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = take_profit
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                change = ((exit_price - enter_price) / enter_price) * 100
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'period_max': df.loc[(df['Datetime'] >= datetime.strptime(enter_date,
                                                                                        '%Y-%m-%d')) &
                                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))][
                                  'High'].max(),
                              'period_min': df.loc[(df['Datetime'] >= datetime.strptime(enter_date,
                                                                                        '%Y-%m-%d')) &
                                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))][
                                  'Low'].min(),
                              'win': change > 0,
                              'change%': change}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
                peak_tough_peak = False
                take_profit = None
        if peak_tough_peak:
            if not long_position:
                if second_peak['Price'] <= df.iloc[i]['High']:
                    # TODO: remove print
                    # print(f'peak tough peak: {first_peak} {tough} {second_peak}')
                    if second_peak['Price'] <= df.iloc[i]['Open']:
                        enter_price = df.iloc[i]['Open']
                    else:
                        enter_price = second_peak['Price']
                    enter_date = df.iloc[i]['Date']
                    stop_loss = tough['Price']*0.98
                    take_profit = enter_price*1.095
                    long_position = True
                    peak_tough_peak = False
                    first_peak = None
                    second_peak = None
                    tough = None
            else:
                stop_loss = tough['Price']*0.98
                # TODO: remove print
                # print(f'new stop_loss: {stop_loss} {tough["Date"]}')
                peak_tough_peak = False
        elif is_peak_definitive(df, i):
            current_peak = df.shift(2).iloc[i]['High']
            if first_peak is None:
                first_peak = {'Date': df.shift(2).iloc[i]['Date'], 'Price': current_peak}
            elif current_peak >= first_peak['Price']*peaks_ratio and tough is not None and second_peak is None:
                second_peak = {'Date': df.shift(2).iloc[i]['Date'], 'Price': current_peak}
                peak_tough_peak = True
            else:
                first_peak = None
                second_peak = None
                tough = None
        elif is_tough_definitive(df, i):
            current_tough = df.shift(2).iloc[i]['Low']
            if tough is None and first_peak is not None and current_tough > df.iloc[i]['min14']:
                if current_tough < first_peak['Price']:
                    tough = {'Date': df.shift(2).iloc[i]['Date'], 'Price': current_tough}
                else:
                    first_peak = None
                    second_peak = None
                    tough = None
            else:
                first_peak = None
                second_peak = None
                tough = None
        i += 1

    print(ticker, cap)
    return trades, cap


def bullish_rising_peaks_v4(ticker, df, peaks_ratio=1.05):  # Depracted because 'is_peak/tough_definitive' were changed

    df['max14'] = df['High'].rolling(14).max()
    df['min14'] = df['Low'].rolling(14).min()
    df['Datetime'] = pd.to_datetime(df['Date'])

    first_peak = None
    second_peak = None
    tough = None
    peak_tough_peak = False
    long_position = False
    stop_loss = None
    take_profit = None

    cap = 100.0
    trades = []

    i = 0
    while i < len(df)-2:
        if long_position:
            if df.iloc[i]['Low'] < stop_loss:
                if df.iloc[i]['Open'] < stop_loss:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = stop_loss
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                change = ((exit_price - enter_price) / enter_price) * 100
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'period_max': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d') - relativedelta(days=3)) &
                              (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['High'].max(),
                              'period_min': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d') - relativedelta(days=3)) &
                                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['Low'].min(),
                              'win': change > 0,
                              'change%': change}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
                peak_tough_peak = False
            elif df.iloc[i]['High'] > take_profit:
                if df.iloc[i]['Open'] > take_profit:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = take_profit
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                change = ((exit_price - enter_price) / enter_price) * 100
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'period_max': df.loc[(df['Datetime'] >= datetime.strptime(enter_date,
                                                                                        '%Y-%m-%d')) &
                                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))][
                                  'High'].max(),
                              'period_min': df.loc[(df['Datetime'] >= datetime.strptime(enter_date,
                                                                                        '%Y-%m-%d')) &
                                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))][
                                  'Low'].min(),
                              'win': change > 0,
                              'change%': change}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
                peak_tough_peak = False
                take_profit = None
        if peak_tough_peak:
            if not long_position:
                if second_peak['Price'] <= df.iloc[i]['High']:
                    # TODO: remove print
                    # print(f'peak tough peak: {first_peak} {tough} {second_peak}')
                    if second_peak['Price'] <= df.iloc[i]['Open']:
                        enter_price = df.iloc[i]['Open']
                    else:
                        enter_price = second_peak['Price']
                    enter_date = df.iloc[i]['Date']
                    stop_loss = enter_price*0.893
                    take_profit = enter_price*1.095
                    long_position = True
                    peak_tough_peak = False
                    first_peak = None
                    second_peak = None
                    tough = None
            else:
                stop_loss = tough['Price']*0.98
                # TODO: remove print
                # print(f'new stop_loss: {stop_loss} {tough["Date"]}')
                peak_tough_peak = False
        elif is_peak_definitive(df, i):
            current_peak = df.shift(2).iloc[i]['High']
            if first_peak is None:
                first_peak = {'Date': df.shift(2).iloc[i]['Date'], 'Price': current_peak}
            elif current_peak >= first_peak['Price']*peaks_ratio and tough is not None and second_peak is None:
                second_peak = {'Date': df.shift(2).iloc[i]['Date'], 'Price': current_peak}
                peak_tough_peak = True
            else:
                first_peak = None
                second_peak = None
                tough = None
        elif is_tough_definitive(df, i):
            current_tough = df.shift(2).iloc[i]['Low']
            if tough is None and first_peak is not None and current_tough > df.iloc[i]['min14']:
                if current_tough < first_peak['Price']:
                    tough = {'Date': df.shift(2).iloc[i]['Date'], 'Price': current_tough}
                else:
                    first_peak = None
                    second_peak = None
                    tough = None
            else:
                first_peak = None
                second_peak = None
                tough = None
        i += 1

    print(ticker, cap)
    return trades, cap


def bullish_rising_peaks_v5(ticker, df, peaks_ratio=1.05):  # Depracted because 'is_peak/tough_definitive' were changed

    df['max14'] = df['High'].rolling(14).max()
    df['min14'] = df['Low'].rolling(14).min()
    df['Datetime'] = pd.to_datetime(df['Date'])

    first_peak = None
    second_peak = None
    tough = None
    peak_tough_peak = False
    long_position = False
    stop_loss = None
    take_profit = None

    cap = 100.0
    trades = []

    i = 0
    while i < len(df)-2:
        if long_position:
            if df.iloc[i]['Low'] < stop_loss:
                if df.iloc[i]['Open'] < stop_loss:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = stop_loss
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                change = ((exit_price - enter_price) / enter_price) * 100
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'period_max': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d') - relativedelta(days=3)) &
                              (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['High'].max(),
                              'period_min': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d') - relativedelta(days=3)) &
                                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['Low'].min(),
                              'win': change > 0,
                              'change%': change}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
                peak_tough_peak = False
        if peak_tough_peak:
            if not long_position:
                if second_peak['Price'] <= df.iloc[i]['High']:
                    # TODO: remove print
                    # print(f'peak tough peak: {first_peak} {tough} {second_peak}')
                    if second_peak['Price'] <= df.iloc[i]['Open']:
                        enter_price = df.iloc[i]['Open']
                    else:
                        enter_price = second_peak['Price']
                    enter_date = df.iloc[i]['Date']
                    stop_loss = enter_price*0.87
                    long_position = True
                    peak_tough_peak = False
                    first_peak = None
                    second_peak = None
                    tough = None
            else:
                stop_loss = tough['Price']*0.98
                # TODO: remove print
                # print(f'new stop_loss: {stop_loss} {tough["Date"]}')
                peak_tough_peak = False
        elif is_peak_definitive(df, i):
            current_peak = df.shift(2).iloc[i]['High']
            if first_peak is None:
                first_peak = {'Date': df.shift(2).iloc[i]['Date'], 'Price': current_peak}
            elif current_peak >= first_peak['Price']*peaks_ratio and tough is not None and second_peak is None:
                second_peak = {'Date': df.shift(2).iloc[i]['Date'], 'Price': current_peak}
                peak_tough_peak = True
            else:
                first_peak = None
                second_peak = None
                tough = None
        elif is_tough_definitive(df, i):
            current_tough = df.shift(2).iloc[i]['Low']
            if tough is None and first_peak is not None and current_tough > df.iloc[i]['min14']:
                if current_tough < first_peak['Price']:
                    tough = {'Date': df.shift(2).iloc[i]['Date'], 'Price': current_tough}
                else:
                    first_peak = None
                    second_peak = None
                    tough = None
            else:
                first_peak = None
                second_peak = None
                tough = None
        i += 1

    print(ticker, cap)
    return trades, cap


def bullish_rising_peaks_v6(ticker, df, peaks_ratio=1.05, peak_tough_ratio=0.33):

    min_period = 20
    max_period = 10
    df[f'max{max_period}'] = df['High'].rolling(max_period).max()
    df[f'min{min_period}'] = df['Low'].rolling(min_period).min()
    df['Datetime'] = pd.to_datetime(df['Date'])

    peaks = []
    toughs = []
    peak_tough_peak = False
    long_position = False
    stop_loss = None

    cap = 100.0
    trades = []

    i = 0
    while i < len(df)-2:
        if long_position:
            if df.iloc[i]['Low'] < stop_loss:
                if df.iloc[i]['Open'] < stop_loss:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = stop_loss
                exit_date = df.iloc[i]['Date']
                long_position = False
                peak_tough_peak = False
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'period_max': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                              (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['High'].max(),
                              'period_min': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['Low'].min(),
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
        if peak_tough_peak:
            if not long_position:
                if peaks[-1]['Price'] <= df.iloc[i]['High']:
                    # TODO: remove print
                    # print(f'peak tough peak: {first_peak} {tough} {second_peak}')
                    if peaks[-1]['Price'] <= df.iloc[i]['Open']:
                        enter_price = df.iloc[i]['Open']
                    else:
                        enter_price = peaks[-1]['Price']
                    enter_date = df.iloc[i]['Date']
                    stop_loss = toughs[-1]['Price']*0.98
                    long_position = True
                    peak_tough_peak = False
        if is_peak_definitive(df, i) and df.iloc[i]['High'] == df.iloc[i][f'max{max_period}']:
            current_peak = df.iloc[i]['High']
            current_peak_date = datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d')
            if not peaks:
                peaks.append({'Date': current_peak_date, 'Price': current_peak})
            elif toughs:
                if current_peak_date > toughs[-1]['Date'] > peaks[-1]['Date']:
                    if current_peak >= peaks[-1]['Price']*peaks_ratio:
                        peaks.append({'Date': datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d'), 'Price': current_peak})
                        peak_tough_peak = True
        elif is_tough_definitive(df, i):
            current_tough = df.iloc[i]['Low']
            current_tough_date = datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d')
            if not toughs and peaks and current_tough > df.iloc[i][f'min{min_period}']:
                if current_tough >= peaks[-1]['Price']*peak_tough_ratio:
                    toughs.append({'Date': current_tough_date, 'Price': current_tough})
            elif toughs and peaks:
                if current_tough >= peaks[-1]['Price']*peak_tough_ratio and current_tough_date > peaks[-1]['Date'] > toughs[-1]['Date'] and current_tough > df.iloc[i][f'min{min_period}']:
                    toughs.append({'Date': current_tough_date, 'Price': current_tough})
                    stop_loss = current_tough*0.98
        i += 1

    peaks_and_toughs = []

    for peak in peaks:
        peaks_and_toughs.append(
            {'ticker': ticker, 'type': 'peak', 'date': peak['Date'].strftime('%Y-%m-%d'), 'price': peak['Price']})
    for tough in toughs:
        peaks_and_toughs.append(
            {'ticker': ticker, 'type': 'tough', 'date': tough['Date'].strftime('%Y-%m-%d'), 'price': tough['Price']})

    print(ticker, cap)
    return trades, cap, peaks_and_toughs


def bullish_rising_peaks_v7(ticker, df, peaks_ratio=1.05, peak_tough_ratio=0.33):

    df.reset_index(inplace=True)
    min_period = 20
    max_period = 10
    df[f'max{max_period}'] = df['High'].rolling(max_period).max()
    df[f'min{min_period}'] = df['Low'].rolling(min_period).min()
    for i in range(min_period):
        df.loc[i, f'min{min_period}'] = df[:i+1]['Low'].min()
    for i in range(max_period):
        df.loc[i, f'max{max_period}'] = df[:i+1]['High'].max()
    df['Datetime'] = pd.to_datetime(df['Date'])

    peaks = []
    toughs = []
    peak_tough_peak = False
    long_position = False
    stop_loss = None

    cap = 100.0
    trades = []

    i = 0
    while i < len(df)-2:
        if long_position:
            if df.iloc[i]['Low'] < stop_loss:
                if df.iloc[i]['Open'] < stop_loss:
                    exit_price = df.shift(-1).iloc[i]['Open']
                else:
                    exit_price = stop_loss
                exit_date = df.shift(-1).iloc[i]['Date']
                # TODO: remove print
                print(f'Ended trade {exit_date}')
                long_position = False
                peak_tough_peak = False
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'period_max': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                              (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['High'].max(),
                              'period_min': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['Low'].min(),
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
        if peak_tough_peak:
            if not long_position:
                if peaks[-1]['Price'] <= df.iloc[i]['High'] and toughs[-1]['Price'] <= df.iloc[i]['Low']:
                    # TODO: remove print
                    # print(f'peak tough peak: {first_peak} {tough} {second_peak}')
                    if peaks[-1]['Price'] <= df.iloc[i]['Open']:
                        enter_price = df.shift(-1).iloc[i]['Open']
                    else:
                        enter_price = peaks[-1]['Price']
                    enter_date = df.shift(-1).iloc[i]['Date']
                    # TODO: remove print
                    print(f'Entered trade {enter_date} peak: {peaks[-1]["Price"]}')
                    stop_loss = toughs[-1]['Price']*0.98
                    long_position = True
                    peak_tough_peak = False
        if is_peak_loose(df, i):
            current_peak = df.iloc[i]['High']
            current_peak_date = datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d')
            peak = {'Date': current_peak_date, 'Price': current_peak}
            # TODO: remove print
            print(f'peak: {peak} max{max_period}: {df.iloc[i][f"max{max_period}"]}')
            if not peaks:
                peaks.append(peak)
                # TODO: remove print
                print('peak added')
            elif toughs:
                if current_peak_date > toughs[-1]['Date'] > peaks[-1]['Date']:
                    if current_peak >= peaks[-1]['Price']*peaks_ratio and df.iloc[i]['High'] == df.iloc[i][f'max{max_period}']:
                        peaks.append({'Date': datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d'), 'Price': current_peak})
                        # TODO: remove print
                        print('peak added')
                        peak_tough_peak = True
                elif current_peak < peaks[-1]['Price']*peaks_ratio:
                    peak_tough_peak = False
                    peaks.append({'Date': datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d'), 'Price': current_peak})
                    if long_position:
                        stop_loss = current_peak
                        # TODO: remove print
                        print('peak added, updated stoploss')
                    else:
                        # TODO: remove print
                        print('peak added')
        elif is_tough_loose(df, i):
            current_tough = df.iloc[i]['Low']
            current_tough_date = datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d')
            tough = {'Date': current_tough_date, 'Price': current_tough}
            # TODO: remove print
            print(f'tough: {tough} min{min_period}: {df.iloc[i][f"min{min_period}"]}')
            if not toughs and peaks and current_tough > df.iloc[i][f'min{min_period}']:
                if current_tough >= peaks[-1]['Price']*peak_tough_ratio:
                    toughs.append(tough)
                    # TODO: remove print
                    print('tough added')
            elif toughs and peaks:
                if current_tough >= peaks[-1]['Price']*peak_tough_ratio and current_tough_date > peaks[-1]['Date'] > toughs[-1]['Date'] and current_tough > df.iloc[i][f'min{min_period}']:
                    toughs.append({'Date': current_tough_date, 'Price': current_tough})
                    # TODO: remove print
                    print('tough added, updated stoploss')
                    stop_loss = current_tough*0.98
        i += 1

    peaks_and_toughs = []

    for peak in peaks:
        peaks_and_toughs.append(
            {'ticker': ticker, 'type': 'peak', 'date': peak['Date'].strftime('%Y-%m-%d'), 'price': peak['Price']})
    for tough in toughs:
        peaks_and_toughs.append(
            {'ticker': ticker, 'type': 'tough', 'date': tough['Date'].strftime('%Y-%m-%d'), 'price': tough['Price']})

    print(ticker, cap)
    return trades, cap, peaks_and_toughs


def bullish_rising_peaks_v7a(ticker, df, peaks_ratio=1.05, peak_tough_ratio=0.2):

    weekly_df = pd.read_csv(download_stock_week(ticker))
    weekly_df['Datetime'] = pd.to_datetime(weekly_df['Date'])
    df['Datetime'] = pd.to_datetime(df['Date'])
    # weekly_df = weekly_df.loc[df['Datetime'].iloc[0] < weekly_df['Datetime']]
    weekly_df = simple_moving_average(df, 50)
    weekly_df['SMA50angle'] = (weekly_df['SMA50'] - weekly_df.shift(1)['SMA50']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    weekly_df = simple_moving_average(df, 100)
    weekly_df['SMA100angle'] = (weekly_df['SMA100'] - weekly_df.shift(1)['SMA100']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    weekly_df = simple_moving_average(df, 200)
    weekly_df['SMA200angle'] = (weekly_df['SMA200'] - weekly_df.shift(1)['SMA200']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    weekly_df['uptrend'] = np.where((weekly_df['SMA50angle'] > 0) & (weekly_df['SMA100angle'] > 0) & (weekly_df['SMA200angle'] > 0), True, False)
    df.reset_index(inplace=True)
    min_period = 20
    max_period = 5
    df[f'max{max_period}'] = df['High'].rolling(max_period).max()
    df[f'min{min_period}'] = df['Low'].rolling(min_period).min()
    for i in range(min_period):
        df.loc[i, f'min{min_period}'] = df[:i+1]['Low'].min()
    for i in range(max_period):
        df.loc[i, f'max{max_period}'] = df[:i+1]['High'].max()
    df['Datetime'] = pd.to_datetime(df['Date'])

    peaks = []
    toughs = []
    peak_tough_peak = False
    long_position = False
    stop_loss = None

    cap = 100.0
    trades = []

    i = 0
    while i < len(df)-2:
        if long_position:
            if df.iloc[i]['Low'] < stop_loss:
                if df.iloc[i]['Open'] < stop_loss:
                    exit_price = df.shift(-1).iloc[i]['Open']
                else:
                    exit_price = stop_loss
                exit_date = df.shift(-1).iloc[i]['Date']
                # TODO: remove print
                print(f'------------------------------------Ended trade {exit_date} stoploss: {stop_loss}')
                long_position = False
                peak_tough_peak = False
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'period_max': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                              (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['High'].max(),
                              'period_min': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['Low'].min(),
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100
                              }
                print(trade_dict)
                trades.append(trade_dict)
        if peak_tough_peak:
            if not long_position:
                relevant_week = weekly_df.loc[weekly_df['Datetime'] < df.iloc[i]['Datetime']]
                if peaks[-1]['Price'] <= df.iloc[i]['High'] and toughs[-1]['Price'] <= df.iloc[i]['Low'] and relevant_week.iloc[-1]['uptrend']:
                    if peaks[-1]['Price'] <= df.iloc[i]['Open']:
                        enter_price = df.shift(-1).iloc[i]['Open']
                    else:
                        enter_price = peaks[-1]['Price']
                    enter_date = df.shift(-1).iloc[i]['Date']
                    # TODO: remove print
                    print(f'------------------------------------Entered trade {enter_date} peak: {peaks[-1]["Price"]}')
                    stop_loss = toughs[-1]['Price']*0.98
                    long_position = True
                    peak_tough_peak = False
        if is_peak_loose(df, i):
        # if is_peak_definitive(df, i):
            current_peak = df.iloc[i]['High']
            current_peak_date = datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d')
            peak = {'Date': current_peak_date, 'Price': current_peak}
            # TODO: remove print
            print(f'peak: {peak} max{max_period}: {df.iloc[i][f"max{max_period}"]}')
            if not peaks:
                # TODO: remove print
                print('met peak condition 0')
                if current_peak == df.iloc[i][f'max{max_period}']:
                    # TODO: remove print
                    print('met peak condition 0_1')
                    peaks.append(peak)
                    # TODO: remove print
                    print('peak added')
            elif toughs:
                # TODO: remove print
                print('met peak condition 1')
                if current_peak_date > toughs[-1]['Date'] > peaks[-1]['Date']:
                    # TODO: remove print
                    print('met peak condition 1_1')
                    if current_peak >= peaks[-1]['Price']*peaks_ratio or current_peak == df.iloc[i][f'max{max_period}']:
                        # TODO: remove print
                        print('met peak condition 1_1_1')
                        peaks.append({'Date': datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d'), 'Price': current_peak})
                        # TODO: remove print
                        print('peak added')
                        peak_tough_peak = True
                if current_peak < peaks[-1]['Price']:
                    # TODO: remove print
                    print('met peak condition 1_2')
                    peak_tough_peak = False
                    peaks = []
                    # TODO: remove print
                    print('emptied peaks list')
                    peaks.append({'Date': datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d'), 'Price': current_peak})
                    print('peak added')
                    if long_position:
                        # TODO: remove print
                        print('met peak condition 1_2_1')
                        stop_loss = current_peak
                        # TODO: remove print
                        print('peak added, updated stoploss')
                    else:
                        # TODO: remove print
                        print('met peak condition 1_2_2')
                        # TODO: remove print
                        print('peak added')
        elif is_tough_loose(df, i):
        # elif is_tough_definitive(df, i):
            current_tough = df.iloc[i]['Low']
            current_tough_date = datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d')
            tough = {'Date': current_tough_date, 'Price': current_tough}
            # TODO: remove print
            print(f'tough: {tough} min{min_period}: {df.iloc[i][f"min{min_period}"]}')
            if not toughs and peaks and current_tough > df.iloc[i][f'min{min_period}']:
                # TODO: remove print
                print('met tough condition 1')
                tough_pass_price = (peaks[-1]['Price'] - df.iloc[i][f'min{min_period}']) * peak_tough_ratio + \
                                   df.iloc[i][f'min{min_period}']
                if current_tough >= tough_pass_price:
                    # TODO: remove print
                    print('met tough condition 1_1')
                    toughs.append(tough)
                    # TODO: remove print
                    print('tough added')
            elif toughs and peaks:
                # TODO: remove print
                print('met tough condition 2')
                tough_pass_price = (peaks[-1]['Price'] - toughs[-1]['Price']) * peak_tough_ratio + \
                                   toughs[-1]['Price']
                if current_tough >= tough_pass_price and current_tough_date > peaks[-1]['Date'] > toughs[-1]['Date'] and current_tough > df.iloc[i][f'min{min_period}']:
                    # TODO: remove print
                    print('met tough condition 2_1')
                    toughs.append({'Date': current_tough_date, 'Price': current_tough})
                    print('tough added')
                    if long_position:
                        # TODO: remove print
                        print('met tough condition 2_1_1')
                        print('updated stoploss')
                        stop_loss = current_tough*0.98
                elif current_tough < toughs[-1]['Price']:
                    # TODO: remove print
                    print('met tough condition 2_2')
                    # TODO: remove print
                    toughs = []
                    peaks = []
                    peak_tough_peak = False
                    # TODO: remove print
                    print('emptied toughs and peaks list')
                    toughs.append({'Date': current_tough_date, 'Price': current_tough})
                    # TODO: remove print
                    print('tough added')
                else:
                    # TODO: remove print
                    print('met tough condition 2_2')
                    toughs.append({'Date': current_tough_date, 'Price': current_tough})
                    # TODO: remove print
                    stop_loss = current_tough*0.98
                    print('tough added, updated stoploss')

            elif toughs and not peaks:
                # TODO: remove print
                print('met tough condition 3')
                if current_tough < toughs[-1]['Price']:
                    # TODO: remove print
                    print('met tough condition 3_1')
                    toughs = []
                    peaks = []
                    peak_tough_peak = False
                    # TODO: remove print
                    print('emptied toughs and peaks list')
                    toughs.append({'Date': current_tough_date, 'Price': current_tough})
                    # TODO: remove print
                    print('tough added')

        i += 1

    print(ticker, cap)
    return trades, cap


def bullish_rising_peaks_v7b(ticker, df, peaks_ratio=1.05, peak_tough_ratio=0.2):

    df.reset_index(inplace=True)
    df = simple_moving_average(df, 200)
    df = simple_moving_average(df, 50)
    df = simple_moving_average(df, 20)
    df = rsi(df, 14)
    df = stochastic(df, 14)
    df = awesome_oscillator(df, 5, 34)
    df[f'SMA200angle'] = (df['SMA200'] - df.shift(1)['SMA200']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA50angle'] = (df['SMA50'] - df.shift(1)['SMA50']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA20angle'] = (df['SMA20'] - df.shift(1)['SMA20']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'RSI14angle'] = (df['RSI14'] - df.shift(1)['RSI14']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df['stoch14angle'] = (df['stoch14'] - df.shift(1)['stoch14']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    min_period = 30
    max_period = 5
    df[f'max{max_period}'] = df['High'].rolling(max_period).max()
    df[f'min{min_period}'] = df['Low'].rolling(min_period).min()
    for i in range(min_period):
        df.loc[i, f'min{min_period}'] = df[:i+1]['Low'].min()
    for i in range(max_period):
        df.loc[i, f'max{max_period}'] = df[:i+1]['High'].max()
    df['Datetime'] = pd.to_datetime(df['Date'])

    peaks = []
    toughs = []
    peaks_to_file = []
    toughs_to_file = []
    rising_peak_tough = False
    long_position = False
    stop_loss = None

    cap = 100.0
    trades = []

    i = 0
    while i < len(df)-2:
        if long_position:
            if df.iloc[i]['Low'] < stop_loss:
                if df.iloc[i]['Open'] < stop_loss:
                    exit_price = df.shift(-1).iloc[i]['Open']
                else:
                    exit_price = stop_loss
                exit_date = df.shift(-1).iloc[i]['Date']
                exit_sma200 = df.iloc[i]['SMA200']
                exit_sma200_angle = df.iloc[i]['SMA200angle']
                exit_sma50 = df.iloc[i]['SMA50']
                exit_sma50_angle = df.iloc[i]['SMA50angle']
                exit_sma20 = df.iloc[i]['SMA20']
                exit_sma20_angle = df.iloc[i]['SMA20angle']
                exit_rsi14 = df.iloc[i]['RSI14']
                exit_rsi14_angle = df.iloc[i]['RSI14angle']
                exit_stoch14 = df.iloc[i]['stoch14']
                exit_stoch14_angle = df.iloc[i]['stoch14angle']
                exit_ao = df.iloc[i]['AO']
                # TODO: remove print
                # print(f'Ended trade {exit_date} stoploss: {stop_loss}')
                long_position = False
                peak_tough_peak = False
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'period_max': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                              (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['High'].max(),
                              'period_min': df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))]['Low'].min(),
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'enter_sma200': enter_sma200,
                              'enter_sma200_angle': enter_sma200_angle,
                              'enter_sma50': enter_sma50,
                              'enter_sma50_angle': enter_sma50_angle,
                              'enter_sma20': enter_sma20,
                              'enter_sma20_angle': enter_sma20_angle,
                              'enter_rsi14': enter_rsi14,
                              'enter_rsi14_angle': enter_rsi14_angle,
                              'enter_stoch14': enter_stoch14,
                              'enter_stoch14_angle': enter_stoch14_angle,
                              'enter_ao': enter_ao,
                              'exit_sma200': exit_sma200,
                              'exit_sma200_angle': exit_sma200_angle,
                              'exit_sma50': exit_sma50,
                              'exit_sma50_angle': exit_sma50_angle,
                              'exit_sma20': exit_sma20,
                              'exit_sma20_angle': exit_sma20_angle,
                              'exit_rsi14': exit_rsi14,
                              'exit_rsi14_angle': exit_rsi14_angle,
                              'exit_stoch14': exit_stoch14,
                              'exit_stoch14_angle': exit_stoch14_angle,
                              'exit_ao': exit_ao
                              }
                print(trade_dict)
                trades.append(trade_dict)
        if rising_peak_tough:
            if not long_position:
                if peaks[-1]['Price'] <= df.iloc[i]['High'] and toughs[-1]['Price'] <= df.iloc[i]['Low']:
                    # TODO: remove print
                    # print(f'peak tough peak: {first_peak} {tough} {second_peak}')
                    if peaks[-1]['Price'] <= df.iloc[i]['Open']:
                        enter_price = df.shift(-1).iloc[i]['Open']
                    else:
                        enter_price = peaks[-1]['Price']
                    enter_date = df.shift(-1).iloc[i]['Date']
                    enter_sma200 = df.iloc[i]['SMA200']
                    enter_sma200_angle = df.iloc[i]['SMA200angle']
                    enter_sma50 = df.iloc[i]['SMA50']
                    enter_sma50_angle = df.iloc[i]['SMA50angle']
                    enter_sma20 = df.iloc[i]['SMA20']
                    enter_sma20_angle = df.iloc[i]['SMA20angle']
                    enter_rsi14 = df.iloc[i]['RSI14']
                    enter_rsi14_angle = df.iloc[i]['RSI14angle']
                    enter_stoch14 = df.iloc[i]['stoch14']
                    enter_stoch14_angle = df.iloc[i]['stoch14angle']
                    enter_ao = df.iloc[i]['AO']
                    # TODO: remove print
                    # print(f'Entered trade {enter_date} peak: {peaks[-1]["Price"]}')
                    stop_loss = toughs[-1]['Price']*0.98
                    long_position = True
                    rising_peak_tough = False
        if is_peak_loose(df, i):
        # if is_peak_definitive(df, i):
            current_peak = df.iloc[i]['High']
            current_peak_date = datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d')
            peak = {'Date': current_peak_date, 'Price': current_peak}
            peaks_to_file.append(peak)
            # TODO: remove print
            # print(f'peak: {peak} max{max_period}: {df.iloc[i][f"max{max_period}"]}')
            if not peaks:
                # TODO: remove print
                # print('met peak condition 0')
                if current_peak == df.iloc[i][f'max{max_period}']:
                    # TODO: remove print
                    # print('met peak condition 0_1')
                    peaks.append(peak)
                    # TODO: remove print
                    # print('peak added')
            elif toughs:
                # TODO: remove print
                # print('met peak condition 1')
                if current_peak_date > toughs[-1]['Date'] > peaks[-1]['Date']:
                    # TODO: remove print
                    # print('met peak condition 1_1')
                    if current_peak >= peaks[-1]['Price']*peaks_ratio and current_peak == df.iloc[i][f'max{max_period}']:
                        # TODO: remove print
                        # print('met peak condition 1_1_1')
                        peaks.append({'Date': datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d'), 'Price': current_peak})
                        # TODO: remove print
                        # print('peak added')
                        rising_peak_tough = False
                if current_peak < peaks[-1]['Price']:
                    # TODO: remove print
                    # print('met peak condition 1_2')
                    rising_peak_tough = False
                    peaks = []
                    # TODO: remove print
                    # print('emptied peaks list')
                    peaks.append({'Date': datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d'), 'Price': current_peak})
                    # print('peak added')
                    if long_position:
                        # TODO: remove print
                        # print('met peak condition 1_2_1')
                        stop_loss = current_peak
                        # TODO: remove print
                    #     print('peak added, updated stoploss')
                    # else:
                    #     # TODO: remove print
                    #     print('met peak condition 1_2_2')
                    #     # TODO: remove print
                    #     print('peak added')
        elif is_tough_loose(df, i):
        # elif is_tough_definitive(df, i):
            current_tough = df.iloc[i]['Low']
            current_tough_date = datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d')
            tough = {'Date': current_tough_date, 'Price': current_tough}
            toughs_to_file.append(tough)
            # TODO: remove print
            # print(f'tough: {tough} min{min_period}: {df.iloc[i][f"min{min_period}"]}')
            if not toughs and peaks and current_tough > df.iloc[i][f'min{min_period}']:
                # TODO: remove print
                # print('met tough condition 1')
                tough_pass_price = (peaks[-1]['Price'] - df.iloc[i][f'min{min_period}']) * peak_tough_ratio + \
                                   df.iloc[i][f'min{min_period}']
                if current_tough >= tough_pass_price:
                    # TODO: remove print
                    # print('met tough condition 1_1')
                    toughs.append(tough)
                    # TODO: remove print
                    # print('tough added')
                    rising_peak_tough = True
            elif toughs and peaks:
                # TODO: remove print
                # print('met tough condition 2')
                tough_pass_price = (peaks[-1]['Price'] - toughs[-1]['Price']) * peak_tough_ratio + \
                                   toughs[-1]['Price']
                if current_tough >= tough_pass_price and current_tough_date > peaks[-1]['Date'] > toughs[-1]['Date'] and current_tough > df.iloc[i][f'min{min_period}']:
                    # TODO: remove print
                    # print('met tough condition 2_1')
                    toughs.append({'Date': current_tough_date, 'Price': current_tough})
                    # TODO: remove print
                    rising_peak_tough = True
                    # print('tough added, updated stoploss')
                    stop_loss = current_tough*0.98
                # elif current_tough < toughs[-1]['Price']:
                elif current_tough < toughs[-1]['Price']:
                    # TODO: remove print
                    # print('met tough condition 2_2')
                    # TODO: remove print
                    toughs = []
                    peaks = []
                    rising_peak_tough = False
                    # TODO: remove print
                    # print('emptied toughs and peaks list')
                    toughs.append({'Date': current_tough_date, 'Price': current_tough})
                    # TODO: remove print
                    # print('tough added')
                else:
                    # TODO: remove print
                    # print('met tough condition 2_2')
                    toughs.append({'Date': current_tough_date, 'Price': current_tough})
                    # TODO: remove print
                    stop_loss = current_tough
                    # print('tough added, updated stoploss')

            elif toughs and not peaks:
                # TODO: remove print
                # print('met tough condition 3')
                if current_tough < toughs[-1]['Price']:
                    # TODO: remove print
                    # print('met tough condition 3_1')
                    # TODO: remove print
                    toughs = []
                    peaks = []
                    rising_peak_tough = False
                    # TODO: remove print
                    # print('emptied toughs and peaks list')
                    toughs.append({'Date': current_tough_date, 'Price': current_tough})
                    # TODO: remove print
                    # print('tough added')

        i += 1

    print(ticker, cap)
    return trades, cap


if __name__ == "__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, \
        get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import time

    ticker_returns = []
    all_trades = []
    all_peaks_and_toughs = []

    tickers = list(set(get_all_snp_stocks() + get_all_nasdaq_100_stocks() + get_all_dow_jones_industrial_stocks() + ['SPY']))

    start_time = time.time()

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue

        df = df[-1008:]
        trades, final_cap = bullish_rising_peaks_v1_refined(ticker, df)

        ticker_returns.append({'ticker': ticker, 'algorithm_return': final_cap - 100,
                               'buy&hold_return': ((df.iloc[0]['Close'] - df.iloc[-1]['Close'])/df.iloc[0]['Close'])*100.0})
        all_trades = all_trades + trades
        pd.DataFrame(ticker_returns).to_csv(
            save_under_results_path(f'bullish_rising_peaks_trading_v1_refined(_ticker_returns.csv'))
        pd.DataFrame(all_trades).to_csv(
            save_under_results_path(f'bullish_rising_peaks_trading_v1_refined(_all_trades.csv'))

    print(time.time() - start_time)

    # ticker = 'QCOM'
    #
    # df = pd.read_csv(download_stock_day(ticker))[-1008:]
    # print(f'{ticker} Start date: {df.iloc[1]["Date"]}')
    # trades, final_cap = bullish_rising_peaks_v7a(ticker, df)
    # pd.DataFrame(trades).to_csv(save_under_results_path(f'{ticker}_bullish_rising_peaks_trading_v7a_trades.csv'))
