from trade_managers._signal_trading_manager import signal_trading_manager
from machine_learning_stuff.linear_regression import rolling_ols_envelope
import numpy as np


def linreg_envelope_trading(ticker, df, period=200):

    df = rolling_ols_envelope(df, period)

    df['buy_long_signal'] = np.where(df['Low'] > df[f'linreg_low_{period}'], True, False)
    df['sell_long_signal'] = np.where(df['High'] < df[f'linreg_low_{period}'], True, False)
    # df['sell_short_signal'] = np.where(df['High'] < df[f'linreg_high_{period}'], True, False)
    # df['buy_short_signal'] = np.where(df['Low'] > df[f'linreg_high_{period}'], True, False)
    df['sell_short_signal'] = False
    df['buy_short_signal'] = False

    return signal_trading_manager(ticker, df)


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import time

    start_time = time.time()

    # tickers = list(set(get_all_snp_stocks() + get_all_nasdaq_100_stocks() + get_all_dow_jones_industrial_stocks() + ['SPY']))
    tickers = get_all_nasdaq_100_stocks()

    if len(tickers) < 102:
        print(len(tickers))
        print('exited')
        exit()
    ticker_returns = []
    all_trades = []

    for i, ticker in enumerate(tickers):
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError as e:
            print(e)
            continue
        print(f'{i}/{len(tickers)}')
        df = df[-2016:]
        trades, final_cap = linreg_envelope_trading(ticker, df, period=200)
        buy_and_hold = ((df.iloc[-1]["Close"])/df.iloc[0]["Close"])*100.0
        print(f'buy & hold: {buy_and_hold}')
        all_trades = all_trades + trades
        ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0, 'buy&hold': (buy_and_hold - 100.0)})
        pd.DataFrame(all_trades).to_csv(
            save_under_results_path(f'linreg_envelope_trading_all_trades.csv'))
        pd.DataFrame(ticker_returns).to_csv(
            save_under_results_path('linreg_envelope_trading_ticker_returns.csv'))

    print(time.time() - start_time)