import pandas as pd
import numpy as np
from utils.download_stock_csvs import download_stock_day
from _signal_trading_manager import signal_trading_manager_long, signal_trading_manager_short


def n_day_high_breakout(ticker):
    days = list(range(21, 253, 21))
    df = pd.read_csv(download_stock_day(ticker))
    for day in days:
        df[f'{day}_days_high'] = df['High'].rolling(day).max()
        df[f'{day}_days_breakout'] = np.where(df['Close'] > df.shift(1)[f'{day}_days_high'], 1, 0)

    breakout_columns = [c for c in df.columns.tolist() if 'breakout' in c]
    df['total_breakouts'] = df[breakout_columns].sum(axis='columns')

    for day in days:
        df.drop(columns=[f'{day}_days_high', f'{day}_days_breakout'], inplace=True)

    df['buy_signal'] = np.where(df['total_breakouts'] == 12, True, False)
    df['sell_signal'] = np.where((df['total_breakouts'] > 0) & (df['total_breakouts'] < 12), True, False)

    return signal_trading_manager_long(ticker, df)


def n_day_high_breakout_signals(ticker):
    days = list(range(21, 253, 21))
    df = pd.read_csv(download_stock_day(ticker))
    for day in days:
        df[f'{day}_days_high'] = df['High'].rolling(day).max()
        df[f'{day}_days_breakout'] = np.where(df['Close'] > df.shift(1)[f'{day}_days_high'], 1, 0)

    breakout_columns = [c for c in df.columns.tolist() if 'breakout' in c]
    df['total_breakouts'] = df[breakout_columns].sum(axis='columns')

    for day in days:
        df.drop(columns=[f'{day}_days_high', f'{day}_days_breakout'], inplace=True)

    df['buy_signal'] = np.where(df['total_breakouts'] == 12, True, False)
    df['sell_signal'] = np.where((df['total_breakouts'] > 0) & (df['total_breakouts'] < 12), True, False)

    return df


def n_day_low_breakout(ticker):
    days = list(range(21, 253, 21))
    df = pd.read_csv(download_stock_day(ticker))
    for day in days:
        df[f'{day}_days_low'] = df['Low'].rolling(day).min()
        df[f'{day}_days_breakout'] = np.where(df['Close'] < df.shift(1)[f'{day}_days_low'], 1, 0)

    breakout_columns = [c for c in df.columns.tolist() if 'breakout' in c]
    df['total_breakouts'] = df[breakout_columns].sum(axis='columns')

    for day in days:
        df.drop(columns=[f'{day}_days_low', f'{day}_days_breakout'], inplace=True)

    df['sell_signal'] = np.where(df['total_breakouts'] == 12, True, False)
    df['buy_signal'] = np.where((df['total_breakouts'] > 0) & (df['total_breakouts'] < 12), True, False)

    return signal_trading_manager_short(ticker, df)


def n_day_breakout_long(ticker):
    days = list(range(21, 253, 21))
    df = pd.read_csv(download_stock_day(ticker))
    for day in days:
        df[f'{day}_days_high'] = df['High'].rolling(day).max()
        df[f'{day}_days_high_breakout'] = np.where(df['Close'] > df.shift(1)[f'{day}_days_high'], 1, 0)
        df[f'{day}_days_low'] = df['Low'].rolling(day).min()
        df[f'{day}_days_low_breakout'] = np.where(df['Close'] < df.shift(1)[f'{day}_days_low'], 1, 0)

    high_breakout_columns = [c for c in df.columns.tolist() if 'high_breakout' in c]
    df['total_high_breakouts'] = df[high_breakout_columns].sum(axis='columns')
    low_breakout_columns = [c for c in df.columns.tolist() if 'low_breakout' in c]
    df['total_low_breakouts'] = df[low_breakout_columns].sum(axis='columns')

    # for day in days:
    #     df.drop(columns=[f'{day}_days_high',
    #                      f'{day}_days_high_breakout',
    #                      f'{day}_days_low',
    #                      f'{day}_days_low_breakout'], inplace=True)

    df['buy_signal'] = np.where(df['total_high_breakouts'] >= 6, True, False)
    df['sell_signal'] = np.where(df['total_low_breakouts'] >= 6, True, False)

    return signal_trading_manager_long(ticker, df)


def n_day_breakout_short(ticker):
    days = list(range(21, 253, 21))
    df = pd.read_csv(download_stock_day(ticker))
    for day in days:
        df[f'{day}_days_high'] = df['High'].rolling(day).max()
        df[f'{day}_days_high_breakout'] = np.where(df['Close'] > df.shift(1)[f'{day}_days_high'], 1, 0)
        df[f'{day}_days_low'] = df['Low'].rolling(day).min()
        df[f'{day}_days_low_breakout'] = np.where(df['Close'] < df.shift(1)[f'{day}_days_low'], 1, 0)

    high_breakout_columns = [c for c in df.columns.tolist() if 'high_breakout' in c]
    df['total_high_breakouts'] = df[high_breakout_columns].sum(axis='columns')
    low_breakout_columns = [c for c in df.columns.tolist() if 'low_breakout' in c]
    df['total_low_breakouts'] = df[low_breakout_columns].sum(axis='columns')

    # for day in days:
    #     df.drop(columns=[f'{day}_days_high',
    #                      f'{day}_days_high_breakout',
    #                      f'{day}_days_low',
    #                      f'{day}_days_low_breakout'], inplace=True)

    df['sell_signal'] = np.where(df['total_low_breakouts'] >= 2, True, False)
    df['buy_signal'] = np.where((df['total_low_breakouts'] >= 6) | (df['total_high_breakouts'] >= 1), True, False)

    return signal_trading_manager_short(ticker, df)


if __name__ == '__main__':
    import pathos
    from utils.paths import save_under_results_path
    from utils.in_sample_tickers import *
    from utils.get_all_stocks import in_sample_tickers

    tickers = IN_SAMPLE_TICKERS
    all_trades = []

    with pathos.multiprocessing.ProcessPool() as executor:
        results = executor.map(n_day_high_breakout, tickers)

        for result in results:
            all_trades = all_trades + result[0]

    pd.DataFrame(all_trades).to_csv(save_under_results_path('n_day_high_breakout_12_0_new_in_sample_tickers_all_trades.csv'))
