from indicators.momentum_indicators import rsi
import numpy as np
from trade_managers.signal_trading_manager import signal_trading_manager_long


def rsi_trading(ticker, df, fast=20, slow=126):

    df = rsi(df, fast)
    df = rsi(df, slow)

    df['buy_signal'] = np.where((df.shift(1)[f'RSI{fast}'] < df.shift(1)[f'RSI{slow}']) &
                                (df[f'RSI{fast}'] > df[f'RSI{slow}']) &
                                (df[f'RSI{slow}'] > 40), True, False)
    df['sell_signal'] = np.where((df.shift(1)[f'RSI{fast}'] > df.shift(1)[f'RSI{slow}']) &
                                (df[f'RSI{fast}'] < df[f'RSI{slow}']), True, False)

    return signal_trading_manager_long(ticker, df)


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
        trades, final_cap = rsi_trading(ticker, df)
        buy_and_hold = ((df.iloc[-1]["Close"])/df.iloc[0]["Close"])*100.0
        print(f'buy & hold: {buy_and_hold}')
        all_trades = all_trades + trades
        ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0, 'buy&hold': (buy_and_hold - 100.0)})
        pd.DataFrame(all_trades).to_csv(
            save_under_results_path(f'rsi_trading_2_all_trades.csv'))
        pd.DataFrame(ticker_returns).to_csv(
            save_under_results_path('rsi_trading_2_ticker_returns.csv'))

    print(time.time() - start_time)