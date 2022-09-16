from indicators.momentum_indicators import simple_moving_average, awesome_oscillator, rsi, stoch_rsi
from indicators.exit_indicators import floor_trader_pivot
from utils.download_stock_csvs import download_stock_day
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import statistics
import time


def moving_average_trading_break_resistance(ticker, df, fast, medium, slow, support_level, resistance_level):  # long

    df = simple_moving_average(df, fast)
    df = simple_moving_average(df, medium)
    df = simple_moving_average(df, slow)
    df = awesome_oscillator(df, fast, slow)
    df = rsi(df, slow)
    df = stoch_rsi(df, slow)
    df = floor_trader_pivot(df)
    df.dropna(inplace=True)

    rsi_greater = 45
    rsi_lower = 55
    ao_greater = 0
    ao_lower = 0

    df[f'rsi_greater_than_{rsi_greater}'] = np.where(df['RSI'] > rsi_greater, True, False)
    df[f'rsi_lower_than_{rsi_lower}'] = np.where(df['RSI'] < rsi_lower, True, False)
    df[f'ao_greater_than_{ao_greater}'] = np.where(df['AO'] > ao_greater, True, False)
    df[f'ao_lower_than_{ao_lower}'] = np.where(df['AO'] < ao_lower, True, False)

    df[f'SMA{fast}_angle'] = (df[f'SMA{fast}'] - df.shift(1)[f'SMA{fast}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{medium}_angle'] = (df[f'SMA{medium}'] - df.shift(1)[f'SMA{medium}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{slow}_angle'] = (df[f'SMA{medium}'] - df.shift(1)[f'SMA{medium}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df['buy_signal'] = np.where((df.shift(1)[f'SMA{fast}'] < df.shift(1)[f'SMA{medium}']) & (df[f'SMA{fast}'] > df[f'SMA{medium}']) & (df['RSI'] < rsi_lower) & (df['AO'] < ao_lower), True, False)
    # df['sell_signal'] = np.where((df.shift(1)[f'SMA{fast}'] > df.shift(1)[f'SMA{medium}']) & (df[f'SMA{fast}'] < df[f'SMA{medium}']) & (rsi_greater < df['RSI']) & (df['AO'] > ao_greater), True, False)

    # df.to_csv(save_under_results_path(f'{ticker}_moving_average_df.csv'))


    df = df[1:-1]

    i = 0
    long_position = False
    position_price = None
    position_date = None
    cap = 100.0
    buy = True

    trades = []

    while i < len(df):
        if buy:
            if df.iloc[i]['Low'] < df.shift(1).iloc[i][resistance_level] < df.iloc[i]['High']:
                position_price = df.iloc[i][resistance_level]
                position_date = df.iloc[i]['Date']
                long_position = True
            buy = False
        elif long_position:
            if df.iloc[i]['Low'] < df.shift(1).iloc[i][support_level] < df.iloc[i]['High']:
                exit_price = df.shift(1).iloc[i][support_level]
                exit_date = df.iloc[i]['Date']
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
            if not long_position:
                buy = True

        i += 1

    print(ticker, cap)
    return trades, cap


def moving_average_trading_break_resistance_fixed_sl_tp(ticker, df, fast, medium, slow, support_level, resistance_level):  # long

    df = simple_moving_average(df, fast)
    df = simple_moving_average(df, medium)
    df = simple_moving_average(df, slow)
    df = awesome_oscillator(df, fast, slow)
    df = rsi(df, slow)
    df = stoch_rsi(df, slow)
    df = floor_trader_pivot(df)
    df.dropna(inplace=True)

    rsi_greater = 45
    rsi_lower = 55
    ao_greater = 0
    ao_lower = 0

    df[f'rsi_greater_than_{rsi_greater}'] = np.where(df['RSI'] > rsi_greater, True, False)
    df[f'rsi_lower_than_{rsi_lower}'] = np.where(df['RSI'] < rsi_lower, True, False)
    df[f'ao_greater_than_{ao_greater}'] = np.where(df['AO'] > ao_greater, True, False)
    df[f'ao_lower_than_{ao_lower}'] = np.where(df['AO'] < ao_lower, True, False)

    df[f'SMA{fast}_angle'] = (df[f'SMA{fast}'] - df.shift(1)[f'SMA{fast}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{medium}_angle'] = (df[f'SMA{medium}'] - df.shift(1)[f'SMA{medium}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{slow}_angle'] = (df[f'SMA{medium}'] - df.shift(1)[f'SMA{medium}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df['buy_signal'] = np.where((df.shift(1)[f'SMA{fast}'] < df.shift(1)[f'SMA{medium}']) & (df[f'SMA{fast}'] > df[f'SMA{medium}']) & (df['RSI'] < rsi_lower) & (df['AO'] < ao_lower), True, False)
    # df['sell_signal'] = np.where((df.shift(1)[f'SMA{fast}'] > df.shift(1)[f'SMA{medium}']) & (df[f'SMA{fast}'] < df[f'SMA{medium}']) & (rsi_greater < df['RSI']) & (df['AO'] > ao_greater), True, False)

    # df.to_csv(save_under_results_path(f'{ticker}_moving_average_df.csv'))


    df = df[1:-1]

    i = 0
    long_position = False
    position_price = None
    position_date = None
    cap = 100.0
    buy = False

    trades = []

    while i < len(df):
        if buy:
            if df.shift(1).iloc[i][resistance_level] < df.iloc[i]['High']:
                if df.iloc[i]['Open'] >= df.shift(1).iloc[i][resistance_level]:
                    position_price = df.iloc[i]['Open']
                else:
                    position_price = df.shift(1).iloc[i][resistance_level]
                position_date = df.iloc[i]['Date']
                long_position = True
            buy = False
        elif long_position:
            if df.iloc[i]['Low'] < df.shift(1).iloc[i][support_level]:
                if df.iloc[i]['Open'] <= df.shift(1).iloc[i][support_level]:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = df.shift(1).iloc[i][support_level]
                exit_date = df.iloc[i]['Date']
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
            if not long_position:
                buy = True

        i += 1

    print(ticker, cap)
    return trades, cap


def moving_average_trading_break_support(ticker, df, fast, medium, slow, support_level, resistance_level):  # short

    df = simple_moving_average(df, fast)
    df = simple_moving_average(df, medium)
    df = simple_moving_average(df, slow)
    df = awesome_oscillator(df, fast, slow)
    df = rsi(df, slow)
    df = stoch_rsi(df, slow)
    df = floor_trader_pivot(df)
    df.dropna(inplace=True)

    rsi_greater = 45
    rsi_lower = 55
    ao_greater = 0
    ao_lower = 0

    df[f'rsi_greater_than_{rsi_greater}'] = np.where(df['RSI'] > rsi_greater, True, False)
    df[f'rsi_lower_than_{rsi_lower}'] = np.where(df['RSI'] < rsi_lower, True, False)
    df[f'ao_greater_than_{ao_greater}'] = np.where(df['AO'] > ao_greater, True, False)
    df[f'ao_lower_than_{ao_lower}'] = np.where(df['AO'] < ao_lower, True, False)

    df[f'SMA{fast}_angle'] = (df[f'SMA{fast}'] - df.shift(1)[f'SMA{fast}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{medium}_angle'] = (df[f'SMA{medium}'] - df.shift(1)[f'SMA{medium}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{slow}_angle'] = (df[f'SMA{medium}'] - df.shift(1)[f'SMA{medium}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    # df['buy_signal'] = np.where((df.shift(1)[f'SMA{fast}'] < df.shift(1)[f'SMA{medium}']) & (df[f'SMA{fast}'] > df[f'SMA{medium}']) & (df['RSI'] < rsi_lower) & (df['AO'] < ao_lower), True, False)
    df['sell_signal'] = np.where((df.shift(1)[f'SMA{fast}'] > df.shift(1)[f'SMA{medium}']) & (df[f'SMA{fast}'] < df[f'SMA{medium}']) & (rsi_greater < df['RSI']) & (df['AO'] > ao_greater), True, False)

    # df.to_csv(save_under_results_path(f'{ticker}_moving_average_df.csv'))


    df = df[1:-1]

    i = 0
    short_position = False
    position_price = None
    position_date = None
    cap = 100.0
    sell = True

    trades = []

    while i < len(df):
        if sell:
            if df.iloc[i]['Low'] < df.shift(1).iloc[i][resistance_level] < df.iloc[i]['High']:
                position_price = df.iloc[i][resistance_level]
                position_date = df.iloc[i]['Date']
                short_position = True
            sell = False
        elif short_position:
            if df.iloc[i]['Low'] < df.shift(1).iloc[i][support_level] < df.iloc[i]['High']:
                exit_price = df.shift(1).iloc[i][support_level]
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((position_price - exit_price) / position_price))
                trade_dict = {'symbol': ticker,
                              'type': 'short',
                              'enter_date': position_date,
                              'enter_price': position_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': position_price > exit_price,
                              'change%': ((position_price - exit_price) / position_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                short_position = False
        elif df.iloc[i]['sell_signal']:
            if not short_position:
                sell = True

        i += 1

    print(ticker, cap)
    return trades, cap


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import glob
    import itertools
    import os

    # tickers = get_all_snp_companies()



    # for ticker in tickers:
    #     try:
    #         df = pd.read_csv(download_stock(ticker))
    #     except ValueError:
    #         continue
    #     df = df[-1008:]
    #     trades, final_cap = moving_average_trading_break_support(ticker, df, 4, 6, 21, 'S1', 'R1')
    #     all_trades = all_trades + trades
    #     all_trades_df = pd.DataFrame(all_trades)
    #     all_trades_df.to_csv(save_under_results_path(f'all_tickers_moving_average_trading_break_suppoer_S1_R1_sma_4_6_21_results.csv'))
    #     ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0)/100.0)*100.0})
    #     ticker_returns_df = pd.DataFrame(ticker_returns)
    #     ticker_returns_df.to_csv(save_under_results_path('ticker_returns_moving_average_trading_break_suppoer_S1_R1_sma_4_6_21.csv'))

    csvs = glob.glob(
        r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\stocks_max_daily_history" + '/*.csv')

    # support_levels = ['S1', 'S2', 'S3']
    # resistance_levels = ['R1', 'R2', 'R3']
    # support_resistance_pairs = list(itertools.product(support_levels, resistance_levels))
    #
    # for pair in support_resistance_pairs:
    #     support, resistance = pair[0], pair[1]
    #
    #     ticker_returns_s_r_long = []
    #     ticker_returns_r_s_long = []
    #     all_trades_s_r_long = []
    #     all_trades_r_s_long = []
    #
    #     ticker_returns_s_r_short = []
    #     ticker_returns_r_s_short = []
    #     all_trades_s_r_short = []
    #     all_trades_r_s_short = []
    #
    #     for csv in csvs:
    #         ticker = os.path.basename(csv).split('.')[0]
    #         print(ticker)
    #         df = pd.read_csv(csv)
    #         df = df[-1008:]
    #
    #         trades, final_cap = moving_average_trading_break_resistance(ticker, df, 4, 6, 21, support, resistance)
    #         all_trades_s_r_long = all_trades_s_r_long + trades
    #         all_trades_df = pd.DataFrame(all_trades_s_r_long)
    #         all_trades_df.to_csv(save_under_results_path(
    #             f'all_tickers_moving_average_trading_break_resistance_{support}_{resistance}_sma_4_6_21_results.csv'))
    #         ticker_returns_s_r_long.append({'ticker': ticker, 'return': ((final_cap - 100.0)/100.0)*100.0})
    #         ticker_returns_df = pd.DataFrame(ticker_returns_s_r_long)
    #         ticker_returns_df.to_csv(save_under_results_path(
    #             f'ticker_returns_moving_average_trading_break_resistance_{support}_{resistance}_sma_4_6_21.csv'))
    #
    #         trades, final_cap = moving_average_trading_break_resistance(ticker, df, 4, 6, 21, resistance, support)
    #         all_trades_r_s_long = all_trades_r_s_long + trades
    #         all_trades_df = pd.DataFrame(all_trades_r_s_long)
    #         all_trades_df.to_csv(save_under_results_path(
    #             f'all_tickers_moving_average_trading_break_resistance_{resistance}_{support}_sma_4_6_21_results.csv'))
    #         ticker_returns_r_s_long.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0})
    #         ticker_returns_df = pd.DataFrame(ticker_returns_r_s_long)
    #         ticker_returns_df.to_csv(save_under_results_path(
    #             f'ticker_returns_moving_average_trading_break_resistance_{resistance}_{support}_sma_4_6_21.csv'))
    #
    #         trades, final_cap = moving_average_trading_break_support(ticker, df, 4, 6, 21, support, resistance)
    #         all_trades_s_r_short = all_trades_s_r_short + trades
    #         all_trades_df = pd.DataFrame(all_trades_s_r_short)
    #         all_trades_df.to_csv(save_under_results_path(
    #             f'all_tickers_moving_average_trading_break_support_{support}_{resistance}_sma_4_6_21_results.csv'))
    #         ticker_returns_s_r_short.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0})
    #         ticker_returns_df = pd.DataFrame(ticker_returns_s_r_short)
    #         ticker_returns_df.to_csv(save_under_results_path(
    #             f'ticker_returns_moving_average_trading_break_support_{support}_{resistance}_sma_4_6_21.csv'))
    #
    #         trades, final_cap = moving_average_trading_break_support(ticker, df, 4, 6, 21, resistance, support)
    #         all_trades_r_s_short = all_trades_r_s_short + trades
    #         all_trades_df = pd.DataFrame(all_trades_r_s_short)
    #         all_trades_df.to_csv(save_under_results_path(
    #             f'all_tickers_moving_average_trading_break_support_{resistance}_{support}_sma_4_6_21_results.csv'))
    #         ticker_returns_r_s_short.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0})
    #         ticker_returns_df = pd.DataFrame(ticker_returns_r_s_short)
    #         ticker_returns_df.to_csv(save_under_results_path(
    #             f'ticker_returns_moving_average_trading_break_support_{resistance}_{support}_sma_4_6_21.csv'))

    ticker_returns_s_r_long = []
    ticker_returns_r_s_long = []
    all_trades_s_r_long = []
    all_trades_r_s_long = []

    support = 'S1'
    resistance = 'R3'

    for csv in csvs:
        ticker = os.path.basename(csv).split('.')[0]
        print(ticker)
        df = pd.read_csv(csv)
        df = df[-1008:]

        trades, final_cap = moving_average_trading_break_resistance(ticker, df, 4, 6, 21, support, resistance)
        all_trades_s_r_long = all_trades_s_r_long + trades
        all_trades_df = pd.DataFrame(all_trades_s_r_long)
        all_trades_df.to_csv(save_under_results_path(
            f'all_tickers_moving_average_trading_break_resistance_fixed_sl_tp_{support}_{resistance}_sma_4_6_21_results.csv'))
        ticker_returns_s_r_long.append({'ticker': ticker, 'return': ((final_cap - 100.0)/100.0)*100.0})
        ticker_returns_df = pd.DataFrame(ticker_returns_s_r_long)
        ticker_returns_df.to_csv(save_under_results_path(
            f'ticker_returns_moving_average_trading_break_resistance_fixed_sl_tp_{support}_{resistance}_sma_4_6_21.csv'))

        trades, final_cap = moving_average_trading_break_resistance(ticker, df, 4, 6, 21, resistance, support)
        all_trades_r_s_long = all_trades_r_s_long + trades
        all_trades_df = pd.DataFrame(all_trades_r_s_long)
        all_trades_df.to_csv(save_under_results_path(
            f'all_tickers_moving_average_trading_break_resistance_fixed_sl_tp_{resistance}_{support}_sma_4_6_21_results.csv'))
        ticker_returns_r_s_long.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0})
        ticker_returns_df = pd.DataFrame(ticker_returns_r_s_long)
        ticker_returns_df.to_csv(save_under_results_path(
            f'ticker_returns_moving_average_trading_break_resistance_fixed_sl_tp_{resistance}_{support}_sma_4_6_21.csv'))

    # ticker = 'PYPL'
    # df = pd.read_csv(download_stock(ticker))
    # df = df[-1008:]
    # trades, final_cap = moving_average_trading_break_support(ticker, df, 4, 6, 21, 'R1', 'S1')
