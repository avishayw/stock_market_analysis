from indicators.trend_indicators import exponential_moving_average
import numpy as np


def macd_histogram_signals(df, fast=12, slow=26, smoothing=9):

    df['FAST'] = exponential_moving_average(df, 'Close', fast, inplace=False)
    df['SLOW'] = exponential_moving_average(df, 'Close', slow, inplace=False)
    df['DIFF'] = df['FAST'] - df['SLOW']
    df['SMOOTH'] = exponential_moving_average(df, 'DIFF', smoothing, inplace=False)
    df['HIST'] = df['DIFF'] - df['SMOOTH']

    df['buy_signal'] = np.where((df.shift(1)['HIST'] < df['HIST']) &
                                (df['HIST'] > 0), True, False)
    df['sell_signal'] = np.where(df['HIST'] < df.shift(1)['HIST'], True, False)

    return df


if __name__=='__main__':
    from trade_managers.signal_trading_manager import signal_trading_manager_long, signal_trading_manager_short
    from utils.get_all_stocks import in_sample_tickers
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import concurrent.futures

    tickers = in_sample_tickers()

    all_trades = []

    # for ticker in tickers:
    #     df = pd.read_csv(download_stock_day(ticker))
    #     df = macd_histogram_signals(df, fast=50, slow=200, smoothing=9)
    #     trades, final_cap = signal_trading_manager_long(ticker, df)
    #     all_trades = all_trades + trades
    #     pd.DataFrame(all_trades).to_csv(save_under_results_path('macd_histogram_trading.csv'))
    #

    def run_strategy(ticker):
        df = pd.read_csv(download_stock_day(ticker))
        df = macd_histogram_signals(df, fast=50, slow=200, smoothing=9)
        return signal_trading_manager_long(ticker, df)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(run_strategy, tickers)

        for result in results:
            all_trades += result[0]
            pd.DataFrame(all_trades).to_csv(save_under_results_path('macd_histogram_trading.csv'))
