from indicators.momentum_indicators import simple_moving_average, simple_moving_average_alt, awesome_oscillator, awesome_oscillator_alt, rsi, rsi_alt, stoch_rsi, stoch_rsi_alt, rsi_median, stoch_rsi_median
from indicators.volatility_indicators import average_true_range
from utils.download_stock_csvs import download_stock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import statistics
import time


def moving_average_trading(ticker, df, fast, medium, slow, short_enabled=False):

    df = simple_moving_average(df, fast)
    df = simple_moving_average(df, medium)
    df = simple_moving_average(df, slow)
    df = awesome_oscillator(df, fast, slow)
    df = rsi(df, slow)
    df = stoch_rsi(df, slow)
    df.dropna(inplace=True)

    rsi_greater = 45
    rsi_lower = 55
    ao_greater = 0
    ao_lower = 0

    df[f'rsi_greater_than_{rsi_greater}'] = np.where(df['RSI'] > rsi_greater, True, False)
    df[f'rsi_lower_than_{rsi_lower}'] = np.where(df['RSI'] < rsi_lower, True, False)
    df[f'ao_greater_than_{ao_greater}'] = np.where(df['AO'] > ao_greater, True, False)
    df[f'ao_lower_than_{ao_lower}'] = np.where(df['AO'] < ao_lower, True, False)

    df[f'SMA{fast}_yesterday'] = df.shift(1)[f'SMA{fast}']
    # df[f'SMA{fast}_difference'] = df[f'SMA{fast}'] - df[f'SMA{fast}_yesterday']
    # df[f'SMA{fast}_angle'] = df[f'SMA{fast}_difference'].apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{fast}_angle'] = (df[f'SMA{fast}'] - df[f'SMA{fast}_yesterday']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{medium}_yesterday'] = df.shift(1)[f'SMA{medium}']
    # df[f'SMA{medium}_difference'] = df[f'SMA{medium}'] - df[f'SMA{medium}_yesterday']
    # df[f'SMA{medium}_angle'] = df[f'SMA{medium}_difference'].apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{medium}_angle'] = (df[f'SMA{medium}'] - df[f'SMA{medium}_yesterday']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{slow}_yesterday'] = df.shift(1)[f'SMA{medium}']
    # df[f'SMA{slow}_difference'] = df[f'SMA{medium}'] - df[f'SMA{medium}_yesterday']
    # df[f'SMA{slow}_angle'] = df[f'SMA{medium}_difference'].apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{slow}_angle'] = (df[f'SMA{medium}'] - df[f'SMA{medium}_yesterday']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df['sma_buy'] = np.where((df[f'SMA{fast}_yesterday'] < df[f'SMA{medium}_yesterday']) & (df[f'SMA{fast}'] > df[f'SMA{medium}']), True, False)
    df['sma_sell'] = np.where((df[f'SMA{fast}_yesterday'] > df[f'SMA{medium}_yesterday']) & (df[f'SMA{fast}'] < df[f'SMA{medium}']), True, False)
    # df['buy_signal'] = np.where((df[f'SMA{fast}_yesterday'] < df[f'SMA{medium}_yesterday']) & (df[f'SMA{fast}'] > df[f'SMA{medium}']) & (df[f'SMA{fast}_angle'] > 20) & (df['RSI'] < rsi_lower) & (df['AO'] < ao_lower), True, False)
    df['buy_signal'] = np.where((df[f'SMA{fast}_yesterday'] < df[f'SMA{medium}_yesterday']) & (df[f'SMA{fast}'] > df[f'SMA{medium}']) & (df['RSI'] < rsi_lower) & (df['AO'] < ao_lower), True, False)
    df['sell_signal'] = np.where((df[f'SMA{fast}_yesterday'] > df[f'SMA{medium}_yesterday']) & (df[f'SMA{fast}'] < df[f'SMA{medium}']) & (rsi_greater < df['RSI']) & (df['AO'] > ao_greater), True, False)
    # df['sell_signal'] = np.where((df['heikin_ashi_close'] <= df.shift(1)['heikin_ashi_close']*0.9), True, False)
    df[f'SMA{slow}_yesterday'] = df.shift(1)[f'SMA{slow}']
    df[f'SMA{slow}_difference'] = df[f'SMA{slow}'] - df[f'SMA{slow}_yesterday']
    df['open_tomorrow'] = df.shift(-1)['Open']
    df['date_tomorrow'] = df.shift(-1)['Date']
    # df.to_csv(save_under_results_path(f'{ticker}_moving_average_df.csv'))


    df = df[1:-1]

    i = 0
    long_position = False
    short_position = False
    position_price = None
    position_date = None
    cap = 100.0

    trades = []

    if short_enabled:
        while i < len(df):
            if df.iloc[i]['buy_signal']:
                if short_position:
                    exit_price = df.iloc[i]['open_tomorrow']
                    exit_date = df.iloc[i]['date_tomorrow']
                    cap = cap*(1.0 + ((position_price - exit_price)/position_price))
                    trades.append({'symbol': ticker, 'type': 'short', 'enter_date': position_date, 'enter_price': position_price, 'exit_date': exit_date, 'exit_price': exit_price, 'win': position_price > exit_price, 'change%': ((position_price - exit_price)/position_price)*100})
                    short_position = False
                if not long_position:
                    position_price = df.iloc[i]['open_tomorrow']
                    position_date = df.iloc[i]['date_tomorrow']
                    long_position = True
            elif df.iloc[i]['sell_signal']:
                if long_position:
                    exit_price = df.iloc[i]['open_tomorrow']
                    exit_date = df.iloc[i]['date_tomorrow']
                    cap = cap*(1.0 + ((exit_price - position_price)/position_price))
                    trades.append({'symbol': ticker, 'type': 'long', 'enter_date': position_date, 'enter_price': position_price, 'exit_date': exit_date, 'exit_price': exit_price, 'win': exit_price > position_price, 'change%': ((exit_price - position_price)/position_price)*100})
                    long_position = False
                if not short_position:
                    position_price = df.iloc[i]['open_tomorrow']
                    position_date = df.iloc[i]['date_tomorrow']
                    short_position = True
            i += 1
        pass

    else:
        while i < len(df):
            if df.iloc[i]['buy_signal']:
                if not long_position:
                    position_price = df.iloc[i]['open_tomorrow']
                    position_date = df.shift(-1).iloc[i]['Date']
                    long_position = True
            elif df.iloc[i]['sell_signal']:
                if long_position:
                    exit_price = df.iloc[i]['open_tomorrow']
                    exit_date = df.shift(-1).iloc[i]['Date']
                    cap = cap*(1.0 + ((exit_price - position_price)/position_price))
                    trades.append({'symbol': ticker, 'type': 'long', 'enter_date': position_date, 'enter_price': position_price, 'exit_date': exit_date, 'exit_price': exit_price, 'win': exit_price > position_price, 'change%': ((exit_price - position_price)/position_price)*100})
                    long_position = False
            i += 1

    print(ticker, cap)
    return trades, cap


def moving_average_trading_heikin_ashi(ticker, df, fast, medium, slow, short_enabled=False):

    df['heikin_ashi_open'] = (df.shift(1)['Open'] + df.shift(1)['Close'])/2
    df['heikin_ashi_close'] = (df['High'] + df['Close'] + df['Low'] + df['Open'])/4
    df['high_of_close_open'] = df[['Open', 'Close']].max(axis=1)
    df['low_of_close_open'] = df[['Open', 'Close']].min(axis=1)
    df = simple_moving_average_alt(df, 'Close', fast)
    df = simple_moving_average_alt(df, 'Close', medium)
    df = simple_moving_average_alt(df, 'Close', slow)
    df = awesome_oscillator_alt(df, 'High', 'Low', fast, slow)
    # df = rsi_alt(df, 'heikin_ashi_close', slow)
    # df = stoch_rsi_alt(df, 'heikin_ashi_close', slow)
    df = rsi_median(df, slow)
    df = stoch_rsi_median(df, slow)
    df.dropna(inplace=True)

    rsi_greater = 45
    rsi_lower = 55
    ao_greater = 0
    ao_lower = 0

    df[f'rsi_greater_than_{rsi_greater}'] = np.where(df['RSI'] > rsi_greater, True, False)
    df[f'rsi_lower_than_{rsi_lower}'] = np.where(df['RSI'] < rsi_lower, True, False)
    df[f'ao_greater_than_{ao_greater}'] = np.where(df['AO'] > ao_greater, True, False)
    df[f'ao_lower_than_{ao_lower}'] = np.where(df['AO'] < ao_lower, True, False)

    df[f'SMA{fast}_yesterday'] = df.shift(1)[f'SMA{fast}']
    # df[f'SMA{fast}_difference'] = df[f'SMA{fast}'] - df[f'SMA{fast}_yesterday']
    # df[f'SMA{fast}_angle'] = df[f'SMA{fast}_difference'].apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{fast}_angle'] = (df[f'SMA{fast}'] - df[f'SMA{fast}_yesterday']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{medium}_yesterday'] = df.shift(1)[f'SMA{medium}']
    # df[f'SMA{medium}_difference'] = df[f'SMA{medium}'] - df[f'SMA{medium}_yesterday']
    # df[f'SMA{medium}_angle'] = df[f'SMA{medium}_difference'].apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{medium}_angle'] = (df[f'SMA{medium}'] - df[f'SMA{medium}_yesterday']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{slow}_yesterday'] = df.shift(1)[f'SMA{medium}']
    # df[f'SMA{slow}_difference'] = df[f'SMA{medium}'] - df[f'SMA{medium}_yesterday']
    # df[f'SMA{slow}_angle'] = df[f'SMA{medium}_difference'].apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{slow}_angle'] = (df[f'SMA{medium}'] - df[f'SMA{medium}_yesterday']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df['sma_buy'] = np.where((df[f'SMA{fast}_yesterday'] < df[f'SMA{medium}_yesterday']) & (df[f'SMA{fast}'] > df[f'SMA{medium}']), True, False)
    df['sma_sell'] = np.where((df[f'SMA{fast}_yesterday'] > df[f'SMA{medium}_yesterday']) & (df[f'SMA{fast}'] < df[f'SMA{medium}']), True, False)
    df['buy_signal'] = np.where((df[f'SMA{fast}_yesterday'] < df[f'SMA{medium}_yesterday']) & (df[f'SMA{fast}'] > df[f'SMA{medium}']) & (df['RSI'] < rsi_lower) & (df['AO'] < ao_lower), True, False)
    df['sell_signal'] = np.where((df[f'SMA{fast}_yesterday'] > df[f'SMA{medium}_yesterday']) & (df[f'SMA{fast}'] < df[f'SMA{medium}']) & (rsi_greater < df['RSI']) & (df['AO'] > ao_greater), True, False)
    # df['sell_signal'] = np.where((df['heikin_ashi_close'] <= df.shift(1)['heikin_ashi_close']*0.9), True, False)
    df[f'SMA{slow}_yesterday'] = df.shift(1)[f'SMA{slow}']
    df[f'SMA{slow}_difference'] = df[f'SMA{slow}'] - df[f'SMA{slow}_yesterday']
    df['open_tomorrow'] = df.shift(-1)['Open']
    df['date_tomorrow'] = df.shift(-1)['Date']
    # df.to_csv(save_under_results_path(f'{ticker}_moving_average_df.csv'))


    df = df[1:-1]

    i = 0
    long_position = False
    short_position = False
    position_price = None
    position_date = None
    cap = 100.0

    trades = []

    if short_enabled:
        while i < len(df):
            if df.iloc[i]['buy_signal']:
                if short_position:
                    exit_price = df.iloc[i]['open_tomorrow']
                    exit_date = df.iloc[i]['date_tomorrow']
                    cap = cap*(1.0 + ((position_price - exit_price)/position_price))
                    trades.append({'symbol': ticker, 'type': 'short', 'enter_date': position_date, 'enter_price': position_price, 'exit_date': exit_date, 'exit_price': exit_price, 'win': position_price > exit_price, 'change%': ((position_price - exit_price)/position_price)*100})
                    short_position = False
                if not long_position:
                    position_price = df.iloc[i]['open_tomorrow']
                    position_date = df.iloc[i]['date_tomorrow']
                    long_position = True
            elif df.iloc[i]['sell_signal']:
                if long_position:
                    exit_price = df.iloc[i]['open_tomorrow']
                    exit_date = df.iloc[i]['date_tomorrow']
                    cap = cap*(1.0 + ((exit_price - position_price)/position_price))
                    trades.append({'symbol': ticker, 'type': 'long', 'enter_date': position_date, 'enter_price': position_price, 'exit_date': exit_date, 'exit_price': exit_price, 'win': exit_price > position_price, 'change%': ((exit_price - position_price)/position_price)*100})
                    long_position = False
                if not short_position:
                    position_price = df.iloc[i]['open_tomorrow']
                    position_date = df.iloc[i]['date_tomorrow']
                    short_position = True
            i += 1
        pass

    else:
        while i < len(df):
            if df.iloc[i]['buy_signal']:
                if not long_position:
                    position_price = df.iloc[i]['open_tomorrow']
                    position_date = df.shift(-1).iloc[i]['Date']
                    long_position = True
            elif df.iloc[i]['sell_signal']:
                if long_position:
                    exit_price = df.iloc[i]['open_tomorrow']
                    exit_date = df.shift(-1).iloc[i]['Date']
                    cap = cap*(1.0 + ((exit_price - position_price)/position_price))
                    trades.append({'symbol': ticker, 'type': 'long', 'enter_date': position_date, 'enter_price': position_price, 'exit_date': exit_date, 'exit_price': exit_price, 'win': exit_price > position_price, 'change%': ((exit_price - position_price)/position_price)*100})
                    long_position = False
            i += 1

    print(ticker, cap)
    return trades, cap



if __name__=="__main__":
    from utils.get_all_snp_companies import get_all_snp_companies
    from utils.download_stock_csvs import download_stock
    from utils.paths import save_under_results_path
    import pandas as pd

    tickers = get_all_snp_companies()

    ticker_returns = []

    all_trades = []

    # for ticker in tickers:
    #     try:
    #         df = pd.read_csv(download_stock(ticker))
    #     except ValueError:
    #         continue
    #     df = df[-365:]
    #     trades, final_cap = moving_average_trading_alt_2(ticker, df, 3, 7, 21)
    #     trades_df = pd.DataFrame(trades)
    #     trades_df.to_csv(save_under_results_path(f'{ticker}_moving_average_trading_alt_2_results.csv'))
    #     all_trades = all_trades + trades
    #     all_trades_df = pd.DataFrame(all_trades)
    #     all_trades_df.to_csv(save_under_results_path(f'all_tickers_moving_average_trading_alt_2_results.csv'))
    #     ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0)/100.0)*100.0})
    #     ticker_returns_df = pd.DataFrame(ticker_returns)
    #     ticker_returns_df.to_csv(save_under_results_path('ticker_returns.csv'))

    # for ticker in tickers:
    #     try:
    #         df = pd.read_csv(download_stock(ticker))
    #     except ValueError:
    #         continue
    #     df = df[-365:]
    #     trades, final_cap = moving_average_trading(ticker, df, 4, 6, 21, short_enabled=False)
    #     # trades_df = pd.DataFrame(trades)
    #     # trades_df.to_csv(save_under_results_path(f'{ticker}_moving_average_trading_alt_2_with_short_results.csv'))
    #     all_trades = all_trades + trades
    #     all_trades_df = pd.DataFrame(all_trades)
    #     all_trades_df.to_csv(save_under_results_path(f'all_tickers_moving_average_trading_alt_2_results_4_6_21_stochrsi_fast_angle_greater_than_20.csv'))
    #     ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0)/100.0)*100.0})
    #     ticker_returns_df = pd.DataFrame(ticker_returns)
    #     ticker_returns_df.to_csv(save_under_results_path('ticker_returns_4_6_21_stochrsi_fast_angle_greater_than_20.csv'))


    ticker = 'PYPL'
    df = pd.read_csv(download_stock(ticker))
    df = df[-365:]
    moving_average_trading_heikin_ashi(ticker, df, 4, 6, 21, short_enabled=False)
    moving_average_trading(ticker, df, 4, 6, 21, short_enabled=False)
    # trades, final_cap = moving_average_trading_heikin_ashi(ticker, df, 4, 6, 21, short_enabled=False)
    # trades_df = pd.DataFrame(trades)
    # trades_df.to_csv(save_under_results_path(f'{ticker}_moving_average_trading_alt_2_results_2.csv'))

    # Results AAPL short disabled
    # 4, 6, 21 143.8564528990719
    # 3, 7, 21 135.37
    # 4, 6, 31 143.8564528990719
    # 5, 10, 34 136.30027048252714
    # 4, 5, 21 136.49785385871596
    # 4, 6, 12 118.33454999360978
    # 4, 6, 40 139.25664246979218






