import numpy as np
from indicators.momentum_indicators import simple_moving_average
from indicators.trend_indicators import exponential_moving_average


def mean_reversion_trading(ticker, df):

    fast = 4
    medium = 50
    slow = 200
    df = simple_moving_average(df, fast)
    df = simple_moving_average(df, medium)
    df = simple_moving_average(df, slow)
    df = exponential_moving_average(df, 'Close', medium)
    df.dropna(inplace=True)

    df[f'SMA{fast}_angle'] = (df[f'SMA{fast}'] - df.shift(1)[f'SMA{fast}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{medium}_angle'] = (df[f'SMA{medium}'] - df.shift(1)[f'SMA{medium}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))

    df['buy_signal'] = np.where((df['Low'] > df[f'SMA{slow}']) &
                                (df[f'SMA{fast}_angle'] > 0) &
                                (df[f'SMA{medium}']*0.98 < df['Low']) &
                                (df['Low'] < df[f'SMA{medium}']*1.02), True, False)
    df['sell_signal'] = np.where((df['High'] > df[f'SMA{medium}']*1.2) |
                                 (df['Low'] < df[f'SMA{medium}']*0.95), True, False)


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
                exit_date = df.shift(-1).iloc[i]['Date']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['buy_signal']:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


if __name__ == "__main__":
    from utils.get_all_stocks import get_all_nasdaq_100_stocks, \
        get_all_nyse_composite_stocks, \
        get_all_dow_jones_industrial_stocks, get_all_snp_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import json

    tickers = list(set(get_all_dow_jones_industrial_stocks() +
                       get_all_nyse_composite_stocks() +
                       get_all_nasdaq_100_stocks() +
                       get_all_snp_stocks()))

    ticker_returns = []
    all_trades = []

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        df = df[-1008:]

        trades, final_cap = mean_reversion_trading(ticker, df)
        ticker_returns.append({'ticker': ticker, 'return': final_cap-100.0})
        all_trades = all_trades + trades

        pd.DataFrame(ticker_returns).to_csv(save_under_results_path('mean_reversion_trading_ticker_returns.csv'))
        pd.DataFrame(all_trades).to_csv(save_under_results_path('mean_reversion_trading_all_trades.csv'))