from detectors.candle_stick_patterns_class import CandlestickPatterns
from indicators.momentum_indicators import simple_moving_average
import numpy as np


def candlestick_patterns_trading_long(ticker, df):

    df = CandlestickPatterns(df).df
    sma_period = 20
    df = simple_moving_average(df, sma_period)
    df[f'SMA{sma_period}angle'] = (df[f'SMA{sma_period}'] - df.shift(1)[f'SMA{sma_period}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))

    i = 0
    long_position = False
    enter_price = None
    enter_date = None
    cap = 100.0

    trades = []

    while i < len(df):
        if long_position:
            if df.iloc[i]['downtrend'] > 0 and df.iloc[i][f'SMA{sma_period}angle'] <= 20:
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
        elif df.iloc[i]['bullish_patterns']:
            if df.shift(-1).iloc[i]['High'] >= df.iloc[i]['High']*1.002 and df.iloc[i][f'SMA{sma_period}angle'] >= 20:
                long_position = True
                if df.shift(-1).iloc[i]['Open'] >= df.iloc[i]['High']*1.002:
                    enter_price = df.shift(-1).iloc[i]['Open']
                    enter_date = df.shift(-1).iloc[i]['Date']
                else:
                    enter_price = df.iloc[i]['High']*1.002
                    enter_date = df.shift(-1).iloc[i]['Date']

        i += 1

    print(ticker, cap)
    return trades, cap


def candlestick_patterns_trading_short(ticker, df):

    df = CandlestickPatterns(df).df
    sma_period = 20
    df = simple_moving_average(df, sma_period)
    df[f'SMA{sma_period}angle'] = (df[f'SMA{sma_period}'] - df.shift(1)[f'SMA{sma_period}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))

    i = 0
    short_position = False
    enter_price = None
    enter_date = None
    cap = 100.0

    trades = []

    while i < len(df):
        if short_position:
            if df.iloc[i]['uptrend'] > 2 and df.iloc[i][f'SMA{sma_period}angle'] >= -20:
                exit_price = df.shift(-1).iloc[i]['Open']
                exit_date = df.shift(-1).iloc[i]['Date']
                cap = cap * (1.0 + ((enter_price - exit_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price < enter_price,
                              'change%': ((enter_price - exit_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                short_position = False
        elif df.iloc[i]['bearish_patterns']:
            if df.shift(-1).iloc[i]['Low'] <= df.iloc[i]['Low']*0.998 and df.iloc[i][f'SMA{sma_period}angle'] <= -20:
                short_position = True
                if df.shift(-1).iloc[i]['Open'] <= df.iloc[i]['Low']*0.998:
                    enter_price = df.shift(-1).iloc[i]['Open']
                    enter_date = df.shift(-1).iloc[i]['Date']
                else:
                    enter_price = df.iloc[i]['Low']*0.998
                    enter_date = df.shift(-1).iloc[i]['Date']

        i += 1

    print(ticker, cap)
    return trades, cap


if __name__ == "__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd

    tickers = list(set(get_all_snp_stocks() + get_all_dow_jones_industrial_stocks() + get_all_nasdaq_100_stocks()))

    bullish_trades = []
    bearish_trades = []
    bullish_ticker_returns = []
    bearish_ticker_returns = []

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        df = df[-252:]

        print('bull')
        trades, final_cap = candlestick_patterns_trading_long(ticker, df)
        bullish_ticker_returns.append({'ticker': ticker, 'return': final_cap - 100.0})
        bullish_trades = bullish_trades + trades
        pd.DataFrame(bullish_ticker_returns).to_csv(save_under_results_path(f'bullish_candlestick_patterns_sma_trading_ticker_returns.csv'))
        pd.DataFrame(bullish_trades).to_csv(save_under_results_path(f'bullish_candlestick_patterns_sma_trading_all_trades.csv'))

        print('bear')
        trades, final_cap = candlestick_patterns_trading_short(ticker, df)
        bearish_ticker_returns.append({'ticker': ticker, 'return': final_cap - 100.0})
        bearish_trades = bearish_trades + trades
        pd.DataFrame(bearish_ticker_returns).to_csv(save_under_results_path(f'bearish_candlestick_patterns_sma_trading_ticker_returns.csv'))
        pd.DataFrame(bearish_trades).to_csv(save_under_results_path(f'bearish_candlestick_patterns_sma_trading_all_trades.csv'))