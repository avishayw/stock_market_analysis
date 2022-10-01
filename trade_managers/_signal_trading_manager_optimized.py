import numpy as np
import pandas as pd
from datetime import datetime


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
        elif df.iloc[i]['buy_signal'] and df.shift(-1).iloc[i]['Open'] != 0.0:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            long_position = True

        i += 1

    if print_trades:
        print(ticker, cap)
    return trades, cap


if __name__=='__main__':
    from trade_managers._ma_roc_er_trading import ma_roc_er_signals
    from utils.download_stock_csvs import download_stock_day
    from utils.get_all_stocks import in_sample_tickers
    from _signal_trading_manager import signal_trading_manager_long, signal_trading_manager_long_optimized
    import time
    import pandas as pd

    # tickers = in_sample_tickers()
    #
    # for ticker in tickers:
    #     df = pd.read_csv(download_stock_day(ticker))
    #     df = ma_roc_er_signals(df)
    #     copy_df = df.copy()
    #
    #     trades1, cap = signal_trading_manager_long(ticker, df, print_trades=False)
    #
    #     trades2 = signal_trading_manager_long_optimized(ticker, copy_df)
    #
    #     df1 = pd.DataFrame(trades1)
    #
    #     if not df1.empty:
    #         df1.drop(columns=['period_max', 'period_max_date', 'period_min', 'period_min_date'], inplace=True)
    #
    #     df2 = pd.DataFrame(trades2)
    #
    #     if not (df1.empty or df2.empty):
    #         df1.drop(columns=['change%'], inplace=True)
    #         df2.drop(columns=['change%'], inplace=True)
    #         print(ticker, len(df1), len(df2), df1.equals(df2))
    #     else:
    #         print(ticker, len(df1), len(df2))

    ticker = 'BEN'

    df = pd.read_csv(download_stock_day(ticker))
    df = ma_roc_er_signals(df)
    copy_df = df.copy()

    trades1, cap = signal_trading_manager_long(ticker, df, print_trades=False)

    trades2 = signal_trading_manager_long_optimized(ticker, copy_df)

    df1 = pd.DataFrame(trades1)

    if not df1.empty:
        df1.drop(columns=['period_max', 'period_max_date', 'period_min', 'period_min_date'], inplace=True)

    df2 = pd.DataFrame(trades2)

    print(df1.head())
    print(df2.head())
    print(df1.tail())
    print(df2.tail())

    if not (df1.empty or df2.empty):
        df1.drop(columns=['change%'], inplace=True)
        df2.drop(columns=['change%'], inplace=True)
        print(ticker, len(df1), len(df2), df1.equals(df2))
    else:
        print(ticker, len(df1), len(df2))



