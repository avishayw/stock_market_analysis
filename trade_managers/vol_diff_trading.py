import numpy as np
from indicators.my_indicators import average_volume_diff, percental_atr
from indicators.momentum_indicators import rsi, simple_moving_average


def vol_diff_trading(ticker, df, fast, slow, short_enabled=False):

    df = average_volume_diff(df, fast, slow)
    df = rsi(df, slow)


    df['buy_signal'] = np.where(df['VolDiff'] < -10, True, False)
    df['sell_signal'] = np.where(df['VolDiff'] > -10, True, False)

    i = 0
    long_position = False
    enter_price = None
    enter_date = None
    buy_signal_vol_diff = None
    buy_signal_rsi = None
    cap = 100.0

    trades = []


    while i < len(df):
        if long_position:
            if df.iloc[i]['sell_signal']:
                exit_price = df.shift(-1).iloc[i]['Open']
                exit_date = df.shift(-1).iloc[i]['Date']
                sell_signal_vol_diff = df.iloc[i]['VolDiff']
                sell_signal_rsi = df.iloc[i][f'RSI{slow}']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'buy_signal_vol_diff': buy_signal_vol_diff,
                              'buy_signal_rsi': buy_signal_rsi,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'sell_signal_vol_diff': sell_signal_vol_diff,
                              'sell_signal_rsi': sell_signal_rsi,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['buy_signal']:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            buy_signal_vol_diff = df.iloc[i]['VolDiff']
            buy_signal_rsi = df.iloc[i][f'RSI{slow}']
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


def vol_diff_sma_trading(ticker, df, fast, slow, short_enabled=False):
    df = average_volume_diff(df, fast, slow)
    df = simple_moving_average(df, fast)
    df = simple_moving_average(df,slow)
    # df = percental_atr(df, fast)
    # df[f'%ATR{fast}_angle'] = (df[f'%ATR{fast}'] - df.shift(1)[f'%ATR{fast}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df['max'] = df['High'].rolling(200).max()
    df = rsi(df, slow)
    df[f'SMA{fast}_angle'] = (df[f'SMA{fast}'] - df.shift(1)[f'SMA{fast}']).apply(lambda x: np.arctan(x) * (180 / np.pi))

    df['buy_signal'] = np.where((df['VolDiff'] < -10) & (df['Low'] > df[f'SMA{slow}']) & (df[f'SMA{fast}_angle'] > 0) & (df['Low'] > df['max']*0.7), True, False)
    df['sell_signal'] = np.where(df['VolDiff'] > -10, True, False)
    # df['sell_signal'] = np.where(df[f'RSI{slow}'] > 70, True, False)


    i = 0
    long_position = False
    enter_price = None
    enter_date = None
    buy_signal_vol_diff = None
    buy_signal_rsi = None
    cap = 100.0

    trades = []

    while i < len(df):
        if long_position:
            if df.iloc[i]['sell_signal']:
                exit_price = df.shift(-1).iloc[i]['Open']
                exit_date = df.shift(-1).iloc[i]['Date']
                sell_signal_vol_diff = df.iloc[i]['VolDiff']
                sell_signal_rsi = df.iloc[i][f'RSI{slow}']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'buy_signal_vol_diff': buy_signal_vol_diff,
                              'buy_signal_rsi': buy_signal_rsi,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'sell_signal_vol_diff': sell_signal_vol_diff,
                              'sell_signal_rsi': sell_signal_rsi,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['buy_signal']:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            buy_signal_vol_diff = df.iloc[i]['VolDiff']
            buy_signal_rsi = df.iloc[i][f'RSI{slow}']
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


def vol_diff_adapted_trading(ticker, df, fast, slow, short_enabled=False):
    df = average_volume_diff(df, fast, slow)
    df = simple_moving_average(df, fast)
    df = simple_moving_average(df,slow)
    # df = percental_atr(df, fast)
    # df[f'%ATR{fast}_angle'] = (df[f'%ATR{fast}'] - df.shift(1)[f'%ATR{fast}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df['max'] = df['High'].rolling(200).max()
    df = rsi(df, slow)
    df[f'SMA{fast}_angle'] = (df[f'SMA{fast}'] - df.shift(1)[f'SMA{fast}']).apply(lambda x: np.arctan(x) * (180 / np.pi))

    # df['buy_signal'] = np.where(df['VolDiff'] < -10, True, False)
    df['buy_signal'] = np.where((df['VolDiff'] < -10) & (df['Low'] > df[f'SMA{slow}']) & (df[f'SMA{fast}_angle'] > 0) & (df['Low'] > df['max']*0.7), True, False)


    i = 0
    long_position = False
    enter_price = None
    enter_date = None
    enter_index = None
    buy_signal_vol_diff = None
    buy_signal_rsi = None
    cap = 100.0

    trades = []

    while i < len(df):
        if long_position:
            min_vol_diff = df['VolDiff'][enter_index:i+1].min()
            if df.iloc[i]['VolDiff'] >= min_vol_diff*0.5:
                exit_price = df.shift(-1).iloc[i]['Open']
                exit_date = df.shift(-1).iloc[i]['Date']
                sell_signal_vol_diff = df.iloc[i]['VolDiff']
                sell_signal_rsi = df.iloc[i][f'RSI{slow}']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'buy_signal_vol_diff': buy_signal_vol_diff,
                              'buy_signal_rsi': buy_signal_rsi,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'sell_signal_vol_diff': sell_signal_vol_diff,
                              'sell_signal_rsi': sell_signal_rsi,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['buy_signal']:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            enter_index = i
            buy_signal_vol_diff = df.iloc[i]['VolDiff']
            buy_signal_rsi = df.iloc[i][f'RSI{slow}']
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


if __name__ == "__main__":
    from utils.get_all_stocks import get_all_nasdaq_100_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import json

    tickers = get_all_nasdaq_100_stocks()

    ticker_returns = []
    all_trades = []

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        df = df[-1008:]

        trades, final_cap = vol_diff_adapted_trading(ticker, df, 20, 200)
        ticker_returns.append({'ticker': ticker, 'return': final_cap-100.0})
        all_trades = all_trades + trades

        pd.DataFrame(ticker_returns).to_csv(save_under_results_path('vol_diff_adapted_ticker_returns.csv'))
        pd.DataFrame(all_trades).to_csv(save_under_results_path('vol_diff_adapted_all_trades.csv'))
