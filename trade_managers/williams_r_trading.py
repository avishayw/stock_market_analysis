import numpy as np
from indicators.momentum_indicators import williams_r
from indicators.my_indicators import williams_r_all
from trade_managers.signal_trading_manager import signal_trading_manager_long, signal_trading_manager_short


def williams_r_trading_long(ticker, df, period=5, overbought=-10.0, oversold=-90.0):

    df = williams_r(df, period)
    df['buy_signal'] = np.where((df.shift(1)[f'Williams_R%_{period}'] <= oversold) & (df[f'Williams_R%_{period}'] >= oversold), True, False)
    df['sell_signal'] = np.where(df[f'Williams_R%_{period}'] >= overbought, True, False)

    return signal_trading_manager_long(ticker, df)


def williams_r_trading_v2(ticker, df, period=5, overbought=-10.0, oversold=-90.0):
    df = williams_r(df, period)
    df['buy_signal'] = np.where((df.shift(1)[f'Williams_R%_{period}'] <= oversold) & (df[f'Williams_R%_{period}'] >= oversold), True, False)
    df['sell_signal'] = np.where(df.shift(1)[f'Williams_R%_{period}'] < df[f'Williams_R%_{period}'], True, False)

    return signal_trading_manager_long(ticker, df)


def williams_r_all_v1(ticker, df, period=5, open_ratio_on_scale=0.2):

    highest_high = df.shift(1)['High'].rolling(period).max()
    lowest_low = df.shift(1)['Low'].rolling(period).min()
    df[f'Williams_R%_High_{period}'] = ((highest_high - df.shift(1)['High']) / (highest_high - lowest_low)) * -100.0
    df[f'Williams_R%_Open_{period}'] = ((highest_high - df.shift(1)['Open']) / (highest_high - lowest_low)) * -100.0
    df[f'Williams_R%_Close_{period}'] = ((highest_high - df.shift(1)['Close']) / (highest_high - lowest_low)) * -100.0
    df[f'Williams_R%_Low_{period}'] = ((highest_high - df.shift(1)['Low']) / (highest_high - lowest_low)) * -100.0
    # df = williams_r_all(df, period)

    i = 0
    long_position = False
    cap = 100.0

    trades = []

    while i < len(df):
        william_high = df.iloc[i][f'Williams_R%_High_{period}']
        william_low = df.iloc[i][f'Williams_R%_Low_{period}']
        william_open = df.iloc[i][f'Williams_R%_Open_{period}']
        william_close = df.iloc[i][f'Williams_R%_Close_{period}']
        open_on_scale = (william_high - william_open)/(william_high - william_low)
        close_on_scale = (william_high - william_close)/(william_high - william_low)
        if ((william_high - william_low) > 30) and (open_on_scale < 0.2) and (close_on_scale > 0.8):
            date = df.iloc[i]['Date']
            enter_price = df.iloc[i]['Open']
            exit_price = df.iloc[i]['Close']
            cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
            trade_dict = {'symbol': ticker,
                          'type': 'long',
                          'date': date,
                          'enter_price': enter_price,
                          'exit_price': exit_price,
                          'win': exit_price > enter_price,
                          'change%': ((exit_price - enter_price) / enter_price) * 100}
            print(trade_dict)
            trades.append(trade_dict)
        # elif open_on_scale > (1 - open_ratio_on_scale):
        #     date = df.iloc[i]['Date']
        #     enter_price = df.iloc[i]['Open']
        #     exit_price = df.iloc[i]['Close']
        #     cap = cap * (1.0 + ((enter_price - exit_price) / enter_price))
        #     trade_dict = {'symbol': ticker,
        #                   'type': 'short',
        #                   'date': date,
        #                   'enter_price': enter_price,
        #                   'exit_price': exit_price,
        #                   'win': enter_price > exit_price,
        #                   'change%': ((enter_price - exit_price) / enter_price) * 100}
        #     print(trade_dict)
        #     trades.append(trade_dict)

        i += 1

    print(ticker, cap)
    return trades, cap


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import time

    start_time = time.time()

    tickers = list(set(get_all_snp_stocks() + get_all_nasdaq_100_stocks() + get_all_dow_jones_industrial_stocks() + ['SPY']))
    # tickers = ['SPY']
    ticker_returns = []
    all_trades = []

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        df = df[-1008:]
        trades, final_cap = williams_r_trading_v2(ticker, df)
        buy_and_hold = ((df.iloc[-1]["Close"])/df.iloc[0]["Close"])*100.0
        print(f'buy & hold: {buy_and_hold}')
        all_trades = all_trades + trades
        ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0, 'buy&hold': buy_and_hold})
        pd.DataFrame(all_trades).to_csv(
            save_under_results_path(f'williams_r_trading_all_trades.csv'))
        pd.DataFrame(ticker_returns).to_csv(
            save_under_results_path('williams_r_trading_ticker_returns.csv'))

    print(time.time() - start_time)