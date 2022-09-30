from trade_managers._signal_trading_manager import signal_trading_manager_long, signal_trading_manager_short
import numpy as np


def bullish_min_trading(ticker, df, fast, slow):

    df[f'min{fast}'] = df['Low'].rolling(fast).min()
    df[f'min{slow}'] = df['Low'].rolling(slow).min()

    df['buy_signal'] = np.where((df.shift(3)[f'min{fast}'] == df.shift(3)[f'min{slow}']) &
                                (df.shift(2)[f'min{fast}'] == df.shift(2)[f'min{slow}']) &
                                (df.shift(1)[f'min{fast}'] == df.shift(1)[f'min{slow}']) &
                                (df[f'min{fast}'] > df[f'min{slow}']), True, False)
    df['sell_signal'] = np.where(((df.shift(1)[f'min{fast}'] > df.shift(1)[f'min{slow}']) &
                                 (df[f'min{fast}'] <= df[f'min{slow}'])) |
                                  (df.shift(1)[f'min{fast}'] < df[f'min{fast}']), True, False)

    trades, final_cap = signal_trading_manager_long(ticker, df)
    return trades, final_cap


def bullish_min_trading_v2(ticker, df, period):

    df[f'min{period}'] = df['Low'].rolling(period).min()
    df[f'max{period}'] = df['High'].rolling(period).max()

    df['buy_signal'] = np.where((df.shift(2)[f'min{period}'] < df.shift(1)[f'min{period}']) &
                                (df.shift(1)[f'min{period}'] < df[f'min{period}']), True, False)
    df['sell_signal'] = np.where(df.shift(1)[f'max{period}'] == df[f'max{period}'], True, False)

    trades, final_cap = signal_trading_manager_long(ticker, df)
    return trades, final_cap


def bullish_min_trading_v3(ticker, df, period):

    df[f'min{period}'] = df['Low'].rolling(period).min()
    df[f'max{period}'] = df['High'].rolling(period).max()
    df['SMA20'] = df['Close'].rolling(20).mean()
    df['SMA200'] = df['Close'].rolling(200).mean()

    df['buy_signal'] = np.where((df.shift(2)[f'min{period}'] < df.shift(1)[f'min{period}']) &
                                (df.shift(1)[f'min{period}'] < df[f'min{period}']) &
                                (df.shift(1)[f'min{period}'] > df['SMA200']) &
                                (df[f'min{period}'] > df['SMA20']), True, False)
    df['sell_signal'] = np.where((df.shift(1)[f'max{period}'] > df.shift(1)[f'SMA20']) &
                                 (df[f'max{period}'] <= df[f'SMA20']), True, False)

    trades, final_cap = signal_trading_manager_long(ticker, df)
    return trades, final_cap


def bearish_max_trading(ticker, df, fast, slow):

    df[f'max{fast}'] = df['High'].rolling(fast).max()
    df[f'max{slow}'] = df['High'].rolling(slow).max()

    df['sell_signal'] = np.where((df.shift(3)[f'max{fast}'] == df.shift(3)[f'max{slow}']) &
                                (df.shift(2)[f'max{fast}'] == df.shift(2)[f'max{slow}']) &
                                (df.shift(1)[f'max{fast}'] == df.shift(1)[f'max{slow}']) &
                                (df[f'max{fast}'] < df[f'max{slow}']), True, False)
    df['buy_signal'] = np.where(((df.shift(1)[f'max{fast}'] < df.shift(1)[f'max{slow}']) &
                                 (df[f'max{fast}'] >= df[f'max{slow}'])) |
                                (df.shift(1)[f'max{fast}'] > df[f'max{fast}']), True, False)

    trades, final_cap = signal_trading_manager_short(ticker, df)
    return trades, final_cap


if __name__ == "__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd

    tickers = list(set(get_all_snp_stocks() + get_all_dow_jones_industrial_stocks() + get_all_nasdaq_100_stocks()))

    year = 252

    bullish_trades = []
    bearish_trades = []
    bullish_ticker_returns = []
    bearish_ticker_returns = []

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        df = df[-2016:]

        volume = df['Volume'].rolling(200).mean()
        print(f'Ticker: {ticker} | Volume[M]: {volume.iloc[-1]/1000000.0}')



        print('bull')
        trades, final_cap = bullish_min_trading_v3(ticker, df, 3)
        bullish_ticker_returns.append({'ticker': ticker, 'return': final_cap - 100.0})
        bullish_trades = bullish_trades + trades
        # pd.DataFrame(bullish_ticker_returns).to_csv(save_under_results_path(f'bullish_min_max_trading_v3_sma100_ticker_returns.csv'))
        # pd.DataFrame(bullish_trades).to_csv(save_under_results_path(f'bullish_min_max_trading_v3_sma100_all_trades.csv'))

        # print('bear')
        # trades, final_cap = bearish_max_trading(ticker, df, 20, 50)
        # bearish_ticker_returns.append({'ticker': ticker, 'return': final_cap - 100.0})
        # bearish_trades = bearish_trades + trades
        # pd.DataFrame(bearish_ticker_returns).to_csv(save_under_results_path(f'8_years_bearish_max_trading_2_ticker_returns.csv'))
        # pd.DataFrame(bearish_trades).to_csv(save_under_results_path(f'8_years_bearish_max_trading_2_all_trades.csv'))