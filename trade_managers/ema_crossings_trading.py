from statistical_questions.after_emas_crossed_what_was_the_max_diff import ema_diff
from indicators.trend_indicators import exponential_moving_average
from trade_managers.signal_trading_manager import signal_trading_manager_long
import statistics
import numpy as np
import pandas as pd


def ema_crossings_trading(ticker, df, ema1=20, ema2=100):

    if len(df) < 3528:
        print("not enough data")
        return [], 100.0

    sample_df = pd.DataFrame.copy(df[-3528:-1008])
    trade_df = pd.DataFrame.copy(df[-1008:])

    ema_differences = ema_diff(sample_df, ema1=ema1, ema2=ema2)
    min_difference = min(ema_differences)

    if min_difference < 2:
        print("pass")
        return [], 100.0

    target_take_profit = (statistics.median(ema_differences) - min_difference)/2 + min_difference

    trade_df = exponential_moving_average(trade_df, 'Close', ema1)
    trade_df = exponential_moving_average(trade_df, 'Close', ema2)
    trade_df['ema_ratio'] = ((trade_df[f'EMA{ema1}'] - trade_df[f'EMA{ema2}'])/trade_df[f'EMA{ema1}'])*100
    trade_df['buy_signal'] = np.where((trade_df.shift(1)[f'EMA{ema1}'] < trade_df.shift(1)[f'EMA{ema2}']) &
                                      (trade_df[f'EMA{ema1}'] > trade_df[f'EMA{ema2}']), True, False)
    trade_df['sell_signal'] = np.where(((trade_df.shift(1)[f'EMA{ema1}'] > trade_df.shift(1)[f'EMA{ema2}']) &
                                      (trade_df[f'EMA{ema1}'] < trade_df[f'EMA{ema2}'])) |
                                       (trade_df['ema_ratio'] >= target_take_profit), True, False)

    return signal_trading_manager_long(ticker, trade_df)


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import time

    start_time = time.time()

    tickers = list(set(get_all_snp_stocks() + get_all_nasdaq_100_stocks() + get_all_dow_jones_industrial_stocks() + ['SPY']))
    ticker_returns = []
    all_trades = []

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        trades, final_cap = ema_crossings_trading(ticker, df, ema1=20, ema2=100)
        all_trades = all_trades + trades
        ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0})
        pd.DataFrame(all_trades).to_csv(save_under_results_path(f'ema_crossing_trading_all_trades.csv'))
        pd.DataFrame(ticker_returns).to_csv(save_under_results_path('ema_crossing_trading_ticker_returns.csv'))

    print(time.time() - start_time)

