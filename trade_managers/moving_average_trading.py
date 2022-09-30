from indicators.momentum_indicators import simple_moving_average, awesome_oscillator, rsi
from indicators.trend_indicators import exponential_moving_average
from indicators.volatility_indicators import average_true_range
from utils.download_stock_csvs import download_stock_day
from trade_managers._signal_trading_manager import signal_trading_manager_long, signal_trading_manager_short
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import statistics
import time


def moving_average_trading_long(ticker, df, fast, medium, slow):

    df = simple_moving_average(df, fast)
    df = simple_moving_average(df, medium)
    df = simple_moving_average(df, slow)
    df = awesome_oscillator(df, fast, slow)
    df = rsi(df, slow)
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
    # df['buy_signal'] = np.where((df[f'SMA{fast}_yesterday'] < df[f'SMA{medium}_yesterday']) & (df[f'SMA{fast}'] > df[f'SMA{medium}']) & (df[f'SMA{fast}_angle'] > 20) & (df['RSI'] < rsi_lower) & (df['AO'] < ao_lower), True, False)
    df['buy_signal'] = np.where((df.shift(1)[f'SMA{fast}'] < df.shift(1)[f'SMA{medium}']) & (df[f'SMA{fast}'] > df[f'SMA{medium}']) & (df['RSI'] < rsi_lower) & (df['AO'] < ao_lower), True, False)
    df['sell_signal'] = np.where((df.shift(1)[f'SMA{fast}'] > df.shift(1)[f'SMA{medium}']) & (df[f'SMA{fast}'] < df[f'SMA{medium}']) & (rsi_greater < df['RSI']) & (df['AO'] > ao_greater), True, False)

    # df.to_csv(save_under_results_path(f'{ticker}_moving_average_df.csv'))


    df = df[1:-1]

    i = 0
    long_position = False
    position_price = None
    position_max_price = None
    position_max_price_date = None
    position_min_price = None
    position_min_price_date = None
    position_date = None
    cap = 100.0

    trades = []

    while i < len(df):
        if long_position:
            if df.iloc[i]['High'] > position_max_price:
                position_max_price = df.iloc[i]['High']
                position_max_price_date = df.iloc[i]['Date']
            if df.iloc[i]['Low'] < position_min_price:
                position_min_price = df.iloc[i]['Low']
                position_min_price_date = df.iloc[i]['Date']
        if df.iloc[i]['buy_signal']:
            if not long_position:
                position_price = df.shift(-1).iloc[i]['Open']
                position_max_price = df.shift(-1).iloc[i]['High']
                position_max_price_date = df.shift(-1).iloc[i]['Date']
                position_min_price = df.shift(-1).iloc[i]['Low']
                position_min_price_date = df.shift(-1).iloc[i]['Date']
                position_date = df.shift(-1).iloc[i]['Date']
                long_position = True
        elif df.iloc[i]['sell_signal']:
            if long_position:
                exit_price = df.shift(-1).iloc[i]['Open']
                exit_date = df.shift(-1).iloc[i]['Date']
                cap = cap*(1.0 + ((exit_price - position_price)/position_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': position_date,
                              'enter_price': position_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'max_price': position_max_price,
                              'max_price_date': position_max_price_date,
                              'min_price': position_min_price,
                              'min_price_date': position_min_price_date,
                              'win': exit_price > position_price,
                              'change%': ((exit_price - position_price)/position_price)*100}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        i += 1

    print(ticker, cap)
    return trades, cap


def moving_average_trading_long_modified(ticker, df, fast, medium, slow):
    # After looking and minimum and maximum prices both winning and losing positions reach, I noticed most of the
    # losses can be cut pretty early, and some profit can be taken from losing positions.
    # The numbers:
    # 1. Only 10% of the winning trade reach a -8.57% loss or lower (meaning stop loss at -8.57% will only lose 10%
    # of the winning trades)
    # 2. As for the losing trades - 54% of the losses reach a -8.57% loss ot lower (meaning 54% of the losses can be
    # cut early without risking a winning trade according to 1)
    # 3. 20% of the losing trades reach a 4.21% change or higher (max 22%). 50% of the losing trades reach a 2.24%
    # change or higher. This could mean for instance that some profit can be taken at 2.24%. However, the question
    # rises from this is whether I should change the stop loss, risking getting out of the trade early, or wait for
    # the -8.57% stop loss and wait for more profit besides that.
    # 4. WELL! from the winning trades looks like 95% of the winning trades reach a 2.24% profit or higher. BUT 50% of
    # the winning trades reach a profit of 7.56% or higher.

    # I will first cut losses sooner, then we'll see about the early realized profits.

    df = simple_moving_average(df, fast)
    df = simple_moving_average(df, medium)
    df = simple_moving_average(df, slow)
    df = awesome_oscillator(df, fast, slow)
    df = rsi(df, slow)
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
    df['sell_signal'] = np.where((df.shift(1)[f'SMA{fast}'] > df.shift(1)[f'SMA{medium}']) & (df[f'SMA{fast}'] < df[f'SMA{medium}']) & (rsi_greater < df['RSI']) & (df['AO'] > ao_greater), True, False)

    # df.to_csv(save_under_results_path(f'{ticker}_moving_average_df.csv'))

    df = df[1:-1]

    i = 0
    long_position = False
    position_price = None
    position_date = None
    stop_loss_price = None
    cap = 100.0

    trades = []

    while i < len(df):
        if long_position:
            if df.iloc[i]['Low'] < stop_loss_price:
                exit_price = stop_loss_price
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

        if df.iloc[i]['buy_signal']:
            if not long_position:
                position_price = df.shift(-1).iloc[i]['Open']
                position_date = df.shift(-1).iloc[i]['Date']
                stop_loss_price = position_price*0.6 # max -12.6% loss
                long_position = True
        elif df.iloc[i]['sell_signal']:
            if long_position:
                exit_price = df.shift(-1).iloc[i]['Open']
                exit_date = df.shift(-1).iloc[i]['Date']
                cap = cap*(1.0 + ((exit_price - position_price)/position_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': position_date,
                              'enter_price': position_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price > position_price,
                              'change%': ((exit_price - position_price)/position_price)*100}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        i += 1

    print(ticker, cap)
    return trades, cap


def moving_average_trading_heikin_ashi(ticker, df, fast, medium, slow, short_enabled=False):

    df['heikin_ashi_open'] = (df.shift(1)['Open'] + df.shift(1)['Close'])/2
    df['heikin_ashi_close'] = (df['High'] + df['Close'] + df['Low'] + df['Open'])/4
    df['high_of_close_open'] = df[['Open', 'Close']].max(axis=1)
    df['low_of_close_open'] = df[['Open', 'Close']].min(axis=1)
    # df = rsi_alt(df, 'heikin_ashi_close', slow)
    # df = stoch_rsi_alt(df, 'heikin_ashi_close', slow)
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


def moving_average_trading_long_v2a(ticker, df, rapid, fast, medium, slow):

    df = simple_moving_average(df, rapid)
    df = simple_moving_average(df, fast)
    df = simple_moving_average(df, medium)
    df = simple_moving_average(df, slow)
    df[f'SMA{rapid}angle'] = (df[f'SMA{rapid}'] - df.shift(1)[f'SMA{rapid}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{fast}angle'] = (df[f'SMA{fast}'] - df.shift(1)[f'SMA{fast}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{medium}angle'] = (df[f'SMA{medium}'] - df.shift(1)[f'SMA{medium}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{slow}angle'] = (df[f'SMA{slow}'] - df.shift(1)[f'SMA{slow}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))

    df['buy_signal'] = np.where((df[f'SMA{fast}angle'] > 0) &
                                (df[f'SMA{medium}angle'] > 0) &
                                (df[f'SMA{slow}angle'] > 0), True, False)
    df['sell_signal'] = np.where(df[f'SMA{rapid}angle'] < -45, True, False)

    return signal_trading_manager_long(ticker, df)


def moving_average_trading_long_v2b(ticker, df, rapid, fast, medium, slow):

    df = exponential_moving_average(df, 'Close', rapid)
    # df = simple_moving_average(df, fast)
    # df = simple_moving_average(df, medium)
    # df = simple_moving_average(df, slow)
    df[f'EMA{rapid}angle'] = (df[f'EMA{rapid}'] - df.shift(1)[f'EMA{rapid}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    # df[f'SMA{fast}angle'] = (df[f'SMA{fast}'] - df.shift(1)[f'SMA{fast}']).apply(
    #     lambda x: np.arctan(x) * (180 / np.pi))
    # df[f'SMA{medium}angle'] = (df[f'SMA{medium}'] - df.shift(1)[f'SMA{medium}']).apply(
    #     lambda x: np.arctan(x) * (180 / np.pi))
    # df[f'SMA{slow}angle'] = (df[f'SMA{slow}'] - df.shift(1)[f'SMA{slow}']).apply(
    #     lambda x: np.arctan(x) * (180 / np.pi))

    df['buy_signal'] = np.where(df[f'EMA{rapid}angle'] > 0, True, False)
    df['sell_signal'] = np.where(df[f'EMA{rapid}angle'] < -45, True, False)

    return signal_trading_manager_long(ticker, df)


def moving_average_trading_long_v2c(ticker, df, rapid, fast, medium, slow):

    df = exponential_moving_average(df, 'Close', rapid)
    df = simple_moving_average(df, fast)
    df = simple_moving_average(df, medium)
    df = simple_moving_average(df, slow)
    df[f'EMA{rapid}angle'] = (df[f'EMA{rapid}'] - df.shift(1)[f'EMA{rapid}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{fast}angle'] = (df[f'SMA{fast}'] - df.shift(1)[f'SMA{fast}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{medium}angle'] = (df[f'SMA{medium}'] - df.shift(1)[f'SMA{medium}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{slow}angle'] = (df[f'SMA{slow}'] - df.shift(1)[f'SMA{slow}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))

    df['buy_signal'] = np.where((df[f'EMA{rapid}angle'] > 0) &
        (df[f'SMA{fast}angle'] > 0) &
                                (df[f'SMA{medium}angle'] > 0) &
                                (df[f'SMA{slow}angle'] > 0), True, False)
    df['sell_signal'] = np.where((df[f'EMA{rapid}angle'] < -30) &
                                 (df[f'SMA{fast}angle'] < 0), True, False)

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
                exit_ema_rapid_angle = df.iloc[i][f'EMA{rapid}angle']
                exit_sma_fast_angle = df.iloc[i][f'SMA{fast}angle']
                exit_sma_medium_angle = df.iloc[i][f'SMA{medium}angle']
                exit_sma_slow_angle = df.iloc[i][f'SMA{slow}angle']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'enter_ema_rapid_angle': enter_ema_rapid_angle,
                              'enter_sma_fast_angle': enter_sma_fast_angle,
                              'enter_sma_medium_angle': enter_sma_medium_angle,
                              'enter_sma_slow_angle': enter_sma_slow_angle,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'exit_ema_rapid_angle': exit_ema_rapid_angle,
                              'exit_sma_fast_angle': exit_sma_fast_angle,
                              'exit_sma_medium_angle': exit_sma_medium_angle,
                              'exit_sma_slow_angle': exit_sma_slow_angle,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['buy_signal']:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            enter_ema_rapid_angle = df.iloc[i][f'EMA{rapid}angle']
            enter_sma_fast_angle = df.iloc[i][f'SMA{fast}angle']
            enter_sma_medium_angle = df.iloc[i][f'SMA{medium}angle']
            enter_sma_slow_angle = df.iloc[i][f'SMA{slow}angle']
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


def moving_average_trading_long_v2d(ticker, df, rapid, fast, medium, slow):

    df = exponential_moving_average(df, 'Close', rapid)
    df = simple_moving_average(df, fast)
    df = simple_moving_average(df, medium)
    df = simple_moving_average(df, slow)
    df[f'EMA{rapid}angle'] = (df[f'EMA{rapid}'] - df.shift(1)[f'EMA{rapid}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{fast}angle'] = (df[f'SMA{fast}'] - df.shift(1)[f'SMA{fast}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{medium}angle'] = (df[f'SMA{medium}'] - df.shift(1)[f'SMA{medium}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{slow}angle'] = (df[f'SMA{slow}'] - df.shift(1)[f'SMA{slow}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))

    df['buy_signal'] = np.where((df[f'EMA{rapid}angle'] > 0) &
        (df[f'SMA{fast}angle'] > 0) &
                                (df[f'SMA{medium}angle'] > 0) &
                                (df[f'SMA{slow}angle'] > 0), True, False)
    df['sell_signal'] = np.where((df[f'EMA{rapid}angle'] < -30) &
                                 (df[f'SMA{fast}angle'] < 0), True, False)

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
                exit_ema_rapid_angle = df.iloc[i][f'EMA{rapid}angle']
                exit_sma_fast_angle = df.iloc[i][f'SMA{fast}angle']
                exit_sma_medium_angle = df.iloc[i][f'SMA{medium}angle']
                exit_sma_slow_angle = df.iloc[i][f'SMA{slow}angle']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'enter_ema_rapid_angle': enter_ema_rapid_angle,
                              'enter_sma_fast_angle': enter_sma_fast_angle,
                              'enter_sma_medium_angle': enter_sma_medium_angle,
                              'enter_sma_slow_angle': enter_sma_slow_angle,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'exit_ema_rapid_angle': exit_ema_rapid_angle,
                              'exit_sma_fast_angle': exit_sma_fast_angle,
                              'exit_sma_medium_angle': exit_sma_medium_angle,
                              'exit_sma_slow_angle': exit_sma_slow_angle,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['buy_signal']:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            enter_ema_rapid_angle = df.iloc[i][f'EMA{rapid}angle']
            enter_sma_fast_angle = df.iloc[i][f'SMA{fast}angle']
            enter_sma_medium_angle = df.iloc[i][f'SMA{medium}angle']
            enter_sma_slow_angle = df.iloc[i][f'SMA{slow}angle']
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


def moving_average_with_volume_trading_long(ticker, df, rapid, fast, medium, slow):

    df['Datetime'] = pd.to_datetime(df['Date'])
    df = exponential_moving_average(df, 'Close', rapid)
    df = exponential_moving_average(df, 'Close', fast)
    df = simple_moving_average(df, slow)
    df[f'avg_volume_{rapid}'] = df['Volume'].rolling(rapid).mean()
    df[f'avg_volume_{fast}'] = df['Volume'].rolling(fast).mean()
    df[f'EMA{rapid}angle'] = (df[f'EMA{rapid}'] - df.shift(1)[f'EMA{rapid}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'EMA{fast}angle'] = (df[f'EMA{fast}'] - df.shift(1)[f'EMA{fast}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{slow}angle'] = (df[f'SMA{slow}'] - df.shift(1)[f'SMA{slow}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'avg_volume_{rapid}_angle'] = (df[f'avg_volume_{rapid}'] - df.shift(1)[f'avg_volume_{rapid}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df[f'avg_volume_{fast}_angle'] = (df[f'avg_volume_{fast}'] - df.shift(1)[f'avg_volume_{fast}']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))

    df['buy_signal'] = np.where((df[f'EMA{rapid}angle'] > 0) &
                                (df[f'EMA{fast}angle'] > 0) &
                                (df[f'SMA{slow}angle'] > 0) &
                                (df.shift(1)[f'EMA{fast}angle'] > df.shift(1)[f'EMA{rapid}angle']) &
                                (df[f'EMA{fast}angle'] < df[f'EMA{rapid}angle']) &
                                (df[f'avg_volume_{rapid}_angle'] > 0) &
                                (df[f'avg_volume_{fast}_angle'] > 0), True, False)
    df['sell_signal'] = np.where((df[f'EMA{rapid}angle'] < 0) &
                                 (df[f'avg_volume_{rapid}_angle'] > 0), True, False)

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
                period_df = df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                              (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))].copy()
                period_max = period_df['High'].max()
                period_max_pct = ((period_max - enter_price)/enter_price)*100
                period_min = period_df['Low'].min()
                period_min_pct = ((period_min - enter_price) / enter_price) * 100
                period_max_idx = period_df['High'].idxmax()
                period_min_idx = period_df['Low'].idxmin()
                max_before_min = period_max_idx < period_min_idx
                try:
                    print(f'period_max: {period_max}\n'
                          f'rapid_angle: {df.loc[period_max_idx, f"EMA{rapid}angle"]}\n'
                          f'rapid_angle+day: {df.loc[period_max_idx+1, f"EMA{rapid}angle"]}\n'
                          f'fast_angle: {df.loc[period_max_idx, f"EMA{fast}angle"]}\n'
                          f'fast_angle+day: {df.loc[period_max_idx+1, f"EMA{fast}angle"]}\n'
                          f'avg_vol_rapid_angle: {df.loc[period_max_idx, f"avg_volume_{rapid}_angle"]}\n'
                          f'avg_vol_rapid_angle+day: {df.loc[period_max_idx+1, f"avg_volume_{rapid}_angle"]}\n'
                          f'avg_vol_fast_angle: {df.loc[period_max_idx, f"avg_volume_{fast}_angle"]}\n'
                          f'avg_vol_fast_angle+day: {df.loc[period_max_idx+1, f"avg_volume_{fast}_angle"]}\n')
                except IndexError:
                    print(period_max_idx)
                    print(len(df))
                    exit()
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'period_max': period_max,
                              'period_max_%': period_max_pct,
                              'period_min': period_min,
                              'period_min_%': period_min_pct,
                              'max_before_min': max_before_min,
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


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import time

    start_time = time.time()

    # tickers = list(set(get_all_snp_stocks() + get_all_nasdaq_100_stocks() + get_all_dow_jones_industrial_stocks() + ['SPY']))
    # tickers = get_all_nasdaq_100_stocks()
    tickers = ['SPY']
    ticker_returns = []
    all_trades = []

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        df = df[-1008:]
        trades, final_cap = moving_average_with_volume_trading_long(ticker, df, 20, 50, 100, 200)
        print(f'buy & hold: {((df.iloc[-1]["Close"]) / df.iloc[0]["Close"]) * 100.0}')
        # all_trades = all_trades + trades
        # ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0})
        # pd.DataFrame(all_trades).to_csv(save_under_results_path(f'moving_average_with_volume_trading_long_all_trades.csv'))
        # pd.DataFrame(ticker_returns).to_csv(save_under_results_path('moving_average_with_volume_trading_long_ticker_returns.csv'))

    print(time.time() - start_time)
