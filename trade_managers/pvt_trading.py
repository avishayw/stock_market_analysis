from trade_managers.signal_trading_manager import signal_trading_manager_long
from indicators.volume_indicators import vpt
from machine_learning_stuff.linear_regression import rolling_ols
import numpy as np


def vpt_trading(ticker, df, smoothing_period):

    df = vpt(df)
    df[f'VPT_OLS{smoothing_period}'] = rolling_ols(df, 'VPT', smoothing_period)
    # df[f'VPT_Smooth{smoothing_period}'] = df['VPT'].rolling(smoothing_period).mean()
    # df['buy_signal'] = np.where((df.shift(1)['VPT'] < df.shift(1)[f'VPT_Smooth{smoothing_period}']) &
    #                             (df['VPT'] > df[f'VPT_Smooth{smoothing_period}']), True, False)
    # df['sell_signal'] = np.where((df.shift(1)['VPT'] > df.shift(1)[f'VPT_Smooth{smoothing_period}']) &
    #                             (df['VPT'] < df[f'VPT_Smooth{smoothing_period}']), True, False)
    df['buy_signal'] = np.where((df.shift(2)[f'VPT_OLS{smoothing_period}'] < df.shift(1)[f'VPT_OLS{smoothing_period}']) &
                                (df.shift(1)[f'VPT_OLS{smoothing_period}'] < df[f'VPT_OLS{smoothing_period}']), True, False)
    df['sell_signal'] = np.where((df.shift(2)[f'VPT_OLS{smoothing_period}'] > df.shift(1)[f'VPT_OLS{smoothing_period}']) &
                                (df.shift(1)[f'VPT_OLS{smoothing_period}'] > df[f'VPT_OLS{smoothing_period}']), True, False)

    return signal_trading_manager_long(ticker, df)


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import time

    start_time = time.time()

    tickers = list(set(get_all_snp_stocks() + get_all_nasdaq_100_stocks() + get_all_dow_jones_industrial_stocks() + ['SPY']))
    # tickers = get_all_nasdaq_100_stocks()
    # tickers = ['SPY']
    ticker_returns = []
    all_trades = []

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        df = df[-1008:]
        trades, final_cap = vpt_trading(ticker, df, 21)
        buy_and_hold = ((df.iloc[-1]["Close"])/df.iloc[0]["Close"])*100.0
        print(f'buy & hold: {buy_and_hold}')
        all_trades = all_trades + trades
        ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0, 'buy&hold': buy_and_hold})
        pd.DataFrame(all_trades).to_csv(
            save_under_results_path(f'pvt_trading_long_all_trades.csv'))
        pd.DataFrame(ticker_returns).to_csv(
            save_under_results_path('pvt_trading_long_ticker_returns.csv'))

    print(time.time() - start_time)
