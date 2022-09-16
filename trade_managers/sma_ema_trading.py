import numpy as np
from indicators.momentum_indicators import simple_moving_average
from indicators.trend_indicators import exponential_moving_average


def sma_ema_trading(ticker, df, sma_fast_period, sma_medium_period, sma_slow_period, ema_period):  # long

    df = simple_moving_average(df, sma_fast_period)
    df = simple_moving_average(df, sma_medium_period)
    df = simple_moving_average(df, sma_slow_period)
    df = simple_moving_average(df, 200)
    df = simple_moving_average(df, 504)
    df = exponential_moving_average(df, 'Close', ema_period)
    df.dropna(inplace=True)

    df[f'SMA{sma_slow_period}_lowest'] = np.where((df[f'SMA{sma_slow_period}'] < df[f'SMA{sma_medium_period}']) &
                                (df[f'SMA{sma_slow_period}'] < df[f'SMA{sma_fast_period}']) &
                                (df[f'SMA{sma_slow_period}'] < df[f'EMA{ema_period}'])
                                , True, False)
    df['buy_signal'] = np.where((df[f'SMA{sma_slow_period}_lowest'] == True) &
                                (df.shift(1)[f'SMA{sma_slow_period}_lowest'] == False), True, False)
    df[f'SMA{sma_slow_period}_highest'] = np.where((df[f'SMA{sma_slow_period}'] > df[f'SMA{sma_medium_period}']) &
                                 (df[f'SMA{sma_slow_period}'] > df[f'SMA{sma_fast_period}']) &
                                 (df[f'SMA{sma_slow_period}'] > df[f'EMA{ema_period}'])
                                 , True, False)
    df['sell_signal'] = np.where((df[f'SMA{sma_slow_period}_highest'] == True) &
                                (df.shift(1)[f'SMA{sma_slow_period}_highest'] == False), True, False)

    i = 0
    long_position = False
    position_price = None
    position_date = None
    cap = 100.0

    trades = []

    while i < len(df):
        if long_position:
            if df.iloc[i]['sell_signal']:
                exit_price = df.shift(-1).iloc[i]['Open']
                exit_date = df.shift(-1).iloc[i]['Date']
                cap = cap * (1.0 + ((exit_price - position_price) / position_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': position_date,
                              'enter_price': position_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price > position_price,
                              'change%': ((exit_price - position_price) / position_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['buy_signal']:
            position_price = df.shift(-1).iloc[i]['Open']
            position_date = df.shift(-1).iloc[i]['Date']
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import json

    tickers = get_all_snp_stocks()

    ticker_returns = []

    ticker = 'PYPL'

    df = pd.read_csv(download_stock_day(ticker))

    df = df[-1008:]

    trades, final_cap = sma_ema_trading(ticker, df, 10, 21, 55, 6)
