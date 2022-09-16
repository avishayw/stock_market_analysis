from locators.peaks_and_toughs import is_tough_loose
from indicators.momentum_indicators import simple_moving_average
from indicators.trend_indicators import exponential_moving_average
import pandas as pd
import numpy as np


def ma_enter_tough_exit_v0_1(ticker, df, rapid, fast, medium, slow):

    df = exponential_moving_average(df, 'Close', rapid)
    df = exponential_moving_average(df, 'Close', fast)
    df = exponential_moving_average(df, 'Close', medium)
    df = exponential_moving_average(df, 'Close', slow)
    df[f'EMA{rapid}angle'] = (df[f'EMA{rapid}'] - df.shift(1)[f'EMA{rapid}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'EMA{fast}angle'] = (df[f'EMA{fast}'] - df.shift(1)[f'EMA{fast}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'EMA{medium}angle'] = (df[f'EMA{medium}'] - df.shift(1)[f'EMA{medium}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'EMA{slow}angle'] = (df[f'EMA{slow}'] - df.shift(1)[f'EMA{slow}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df['buy_signal'] = np.where((df[f'EMA{rapid}angle'] > 0) & (df[f'EMA{rapid}angle'] < 45), True, False)
    # df['sell_signal'] = np.where((df[f'EMA{rapid}angle'] < 0) &
    #                             (df[f'EMA{fast}angle'] < 0), True, False)
    df[f'min{rapid}'] = df['Low'].rolling(rapid).min()


    i = 0
    long_position = False
    enter_price = None
    enter_date = None
    stop_loss = None
    toughs = []

    cap = 100.0
    trades = []

    while i < len(df):
        if is_tough_loose(df, i):
            current_tough = df.iloc[i]['Low']
            current_tough_date = df.iloc[i]['Date']
            if not toughs:
                if current_tough > df.iloc[i][f'min{rapid}']:
                    # print(f'tough {current_tough} {current_tough_date}')
                    toughs.append(current_tough)
                    stop_loss = current_tough
            else:
                if current_tough >= toughs[-1]:
                    # print(f'tough {current_tough} {current_tough_date}')
                    toughs.append(current_tough)
                    stop_loss = current_tough
                elif current_tough < toughs[-1] and not long_position:
                    # print(f'tough {current_tough} {current_tough_date}')
                    toughs = []
                    toughs.append(current_tough)
                    stop_loss = current_tough
        if long_position:
            if df.iloc[i]['Low'] < stop_loss:
                if df.iloc[i]['Open'] < stop_loss:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = stop_loss
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'stop_loss': stop_loss,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
                stop_loss = None
        elif df.iloc[i]['buy_signal'] and stop_loss is not None:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import time

    # start_time = time.time()
    #
    # tickers = list(set(get_all_snp_stocks() + get_all_nasdaq_100_stocks() + get_all_dow_jones_industrial_stocks() + ['SPY']))
    # ticker_returns = []
    # all_trades = []
    #
    # for i, ticker in enumerate(tickers):
    #     print(f'{i+1}/{len(tickers)}')
    #     try:
    #         df = pd.read_csv(download_stock_day(ticker))
    #     except ValueError:
    #         continue
    #     df = df[-1008:]
    #     trades, final_cap = ma_enter_tough_exit_v0_1(ticker, df, 20, 50, 100, 200)
    #     all_trades = all_trades + trades
    #     ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0, 'buy&hold': ((df.iloc[-1]['Close'] - df.iloc[0]['Close'])/df.iloc[0]['Close']))*100.0})
    #     pd.DataFrame(all_trades).to_csv(save_under_results_path(f'ma_enter_tough_exit_v0_1_all_trades.csv'))
    #     pd.DataFrame(ticker_returns).to_csv(save_under_results_path('ma_enter_tough_exit_v0_1_ticker_returns.csv'))
    #
    # print(time.time() - start_time)

    ticker = 'BIIB'

    df = pd.read_csv(download_stock_day(ticker))[-1008:]
    trades, final_cap = ma_enter_tough_exit_v0_1(ticker, df, 20, 50, 100, 200)
