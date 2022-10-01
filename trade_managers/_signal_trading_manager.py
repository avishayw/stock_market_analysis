import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def signal_trading_manager_long(ticker, df, print_trades=True):
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
                              'period_min_date': min_date}
                if print_trades:
                    print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['buy_signal']:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            long_position = True

        i += 1

    if print_trades:
        print(ticker, cap)
    return trades, cap


def signal_trading_manager_long_optimized(ticker, df, print_trades=True):

    df['symbol'] = ticker
    df['type'] = 'long'
    df['enter_price'] = df.shift(-1)['Open']
    df['enter_date'] = df.shift(-1)['Date']
    df['exit_price'] = df.shift(-1)['Open']
    df['exit_date'] = df.shift(-1)['Date']

    buys = df['buy_signal'].copy()
    sells = df['sell_signal'].copy()

    idx_list = []

    i = 0
    buy = True
    while i < len(df):
        if buy:
            if idx_list:
                if buys[list(reversed(idx_list))[0]:i].any():
                    idx_list.append(i - 1)
                    buy = False
            else:
                if buys[:i].any():
                    idx_list.append(i-1)
                    buy = False
        else:
            if sells[list(reversed(idx_list))[0]:i].any():
                idx_list.append(i - 1)
                buy = True
        i += 1

    if (len(idx_list) % 2) != 0:
        idx_list = idx_list[:-1]

    try:
        if (idx_list[-1] + 1) < (len(df) - 1):
            idx_list.append(idx_list[-1] + 1)
    except IndexError as e:
        print(e)
        print(ticker)
        exit()

    df = df.iloc[idx_list]

    df['sell_signal'] = df.sell_signal.shift(-1)
    df['exit_price'] = df.exit_price.shift(-1)
    df['exit_date'] = df.exit_date.shift(-1)
    df = df.loc[df['buy_signal']]
    # df = df.reset_index().drop(columns=['index'])
    # df = df.drop([df.index[-1]], axis=0)
    df['change%'] = (df['exit_price'] / df['enter_price'] - 1) * 100.0
    df['win'] = df['exit_price'] > df['enter_price']
    trades_df = df[['symbol', 'type', 'enter_date', 'enter_price', 'exit_date', 'exit_price', 'win', 'change%']].copy()

    trades = trades_df.to_dict('records')
    # print(trades)
    return trades


def signal_trading_manager_short(ticker, df):
    i = 0
    short_position = False
    enter_price = None
    enter_date = None
    cap = 100.0

    trades = []

    while i < len(df):
        if short_position:
            if df.iloc[i]['buy_signal']:
                exit_price = df.shift(-1).iloc[i]['Open']
                if np.isnan(exit_price):
                    break
                exit_date = df.shift(-1).iloc[i]['Date']
                cap = cap * (1.0 + ((enter_price - exit_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'short',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price < enter_price,
                              'change%': ((enter_price - exit_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                short_position = False
        elif df.iloc[i]['sell_signal'] and df.shift(-1).iloc[i]['Open'] != 0.0:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            short_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


def signal_trading_manager(ticker, df):

    if 'Date' not in df.columns.tolist():
        df.reset_index(inplace=True)
    if 'Datetime' not in df.columns.tolist():
        df['Datetime'] = pd.to_datetime(df['Date'])

    i = 0
    short_position = False
    long_position = False
    enter_price = None
    enter_date = None
    cap = 100.0

    trades = []

    while i < len(df):
        if short_position:
            if df.iloc[i]['buy_short_signal']:
                exit_price = df.shift(-1).iloc[i]['Open']
                exit_date = df.shift(-1).iloc[i]['Date']
                if np.isnan(exit_price):
                    short_position = False
                    continue
                cap = cap * (1.0 + ((enter_price - exit_price) / enter_price))
                period_df = pd.DataFrame.copy(df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                                                     (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))])
                period_df.reset_index(inplace=True)
                period_max = period_df['High'].max()
                max_date = period_df.iloc[period_df['High'].idxmax()]['Datetime'].strftime('%Y-%m-%d')
                period_min = period_df['Low'].min()
                min_date = period_df.iloc[period_df['Low'].idxmin()]['Datetime'].strftime('%Y-%m-%d')
                trade_dict = {'symbol': ticker,
                              'type': 'short',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price < enter_price,
                              'change%': ((enter_price - exit_price) / enter_price) * 100,
                              'period_best_change%': ((enter_price - period_min) / enter_price) * 100,
                              'period_best_date': min_date,
                              'period_worst_change%': ((enter_price - period_max) / enter_price) * 100,
                              'period_worst_date': max_date}
                print(trade_dict)
                trades.append(trade_dict)
                short_position = False
        elif long_position:
            if df.iloc[i]['sell_long_signal']:
                exit_price = df.shift(-1).iloc[i]['Open']
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
                              'period_best_change%': ((period_max - enter_price) / enter_price) * 100,
                              'period_best_date': max_date,
                              'period_worst_change%': ((period_min - enter_price) / enter_price) * 100,
                              'period_worst_date': min_date}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['sell_short_signal']:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            short_position = True
        elif df.iloc[i]['buy_long_signal']:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap