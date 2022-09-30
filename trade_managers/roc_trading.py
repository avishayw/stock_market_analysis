from indicators.momentum_indicators import rate_of_change
from trade_managers._signal_trading_manager import signal_trading_manager_long
import numpy as np


def roc_trading(ticker, df, roc_period):

    df = rate_of_change(df, roc_period)
    df['ROC_angle'] = (df[f'ROC{roc_period}'] - df.shift(1)[f'ROC{roc_period}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df['buy_signal'] = np.where((df[f'ROC{roc_period}'] > 0) &
                                (df['ROC_angle'] > 0) &
                                (df.shift(1)['ROC_angle'] > 0), True, False)
    df['sell_signal'] = np.where(df['ROC_angle'] < 0, True, False)

    return signal_trading_manager_long(ticker, df)


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

        trades, final_cap = roc_trading(ticker, df, 20)
        ticker_returns.append({'ticker': ticker, 'return': final_cap-100.0})
        all_trades = all_trades + trades

        pd.DataFrame(ticker_returns).to_csv(save_under_results_path('roc_trading_ticker_returns.csv'))
        pd.DataFrame(all_trades).to_csv(save_under_results_path('roc_trading_adapted_all_trades.csv'))
