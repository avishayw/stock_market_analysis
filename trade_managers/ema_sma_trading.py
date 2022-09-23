from indicators.momentum_indicators import simple_moving_average
from indicators.trend_indicators import exponential_moving_average
from trade_managers.signal_trading_manager import signal_trading_manager
import numpy as np

# Bull - SMA50 > SMA200. Enter long: EMA9 < EMA20. Exit long: EMA9 > EMA20
# Bear - SMA50 < SMA200. Enter short: EMA9 > EMA20. Exit short: EMA9 < EMA20


def ema_sma_trading(ticker, df, ema_fast=9, ema_slow=20, sma_fast=50, sma_slow=200):

    df = exponential_moving_average(df, 'Close', ema_fast)
    df = exponential_moving_average(df, 'Close', ema_slow)
    df = simple_moving_average(df, sma_fast)
    df = simple_moving_average(df, sma_slow)

    df['buy_long_signal'] = np.where((df[f'SMA{sma_fast}'] > df[f'SMA{sma_slow}']) &
                                     (df[f'EMA{ema_fast}'] < df[f'EMA{ema_slow}']), True, False)
    df['sell_long_signal'] = np.where(df[f'EMA{ema_fast}'] > df[f'EMA{ema_slow}'], True, False)
    df['sell_short_signal'] = np.where((df[f'SMA{sma_fast}'] < df[f'SMA{sma_slow}']) &
                                     (df[f'EMA{ema_fast}'] > df[f'EMA{ema_slow}']), True, False)
    df['buy_short_signal'] = np.where(df[f'EMA{ema_fast}'] < df[f'EMA{ema_slow}'], True, False)

    return signal_trading_manager(ticker, df)


if __name__=='__main__':
    from utils.paths import get_in_sample_data_csvs, save_under_results_path
    from utils.get_ticker_from_csv import get_ticker_from_csv
    import pandas as pd

    all_trades = []

    csvs = get_in_sample_data_csvs()
    for csv in csvs:
        ticker = get_ticker_from_csv(csv)
        df = pd.read_csv(csv)

        trades, final_cap = ema_sma_trading(ticker, df, sma_fast=20)

        all_trades = all_trades + trades
        pd.DataFrame(all_trades).to_csv(save_under_results_path('ema_sma_trading_in_sample.csv'))

