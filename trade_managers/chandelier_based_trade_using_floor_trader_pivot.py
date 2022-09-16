from indicators.exit_indicators import chandalier_exit_close, chandalier_exit_highest_high_lowest_low, chandalier_exit_highest_high_lowest_high, floor_trader_pivot
from indicators.trend_indicators import zero_lag_ema
from utils.paths import save_under_results_path


def chandelier_based_trade_break_resistance(ticker, df, period, multiplier, support_level, resistance_level):

    df = chandalier_exit_highest_high_lowest_low(df, period, multiplier)
    df = floor_trader_pivot(df)

    df.to_csv(save_under_results_path(f"{ticker}_ce_ftp_dataframe.csv"))

    i = 0
    long_position = False
    buy = False
    position_price = None
    position_date = None
    enter_high = None
    enter_low = None
    enter_open = None
    enter_close = None
    enter_previous_resistance = None
    cap = 100.0

    trades = []

    while i < len(df):
        if buy:
            if df.shift(1).iloc[i][resistance_level] < df.iloc[i]['High']:
                if df.iloc[i]['Open'] >= df.shift(1).iloc[i][resistance_level]:
                    position_price = df.iloc[i]['Open']
                else:
                    position_price = df.shift(1).iloc[i][resistance_level]
                position_date = df.iloc[i]['Date']
                enter_high = df.iloc[i]['High']
                enter_low = df.iloc[i]['Low']
                enter_open = df.iloc[i]['Open']
                enter_close = df.iloc[i]['Close']
                enter_previous_resistance = df.shift(1).iloc[i][resistance_level]
                long_position = True
            buy = False
        elif long_position:
            if df.iloc[i]['Low'] < df.shift(1).iloc[i][support_level]:
                if df.iloc[i]['Open'] <= df.shift(1).iloc[i][support_level]:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = df.shift(1).iloc[i][support_level]
                exit_date = df.iloc[i]['Date']
                exit_high = df.iloc[i]['High']
                exit_low = df.iloc[i]['Low']
                exit_open = df.iloc[i]['Open']
                exit_close = df.iloc[i]['Close']
                exit_previous_support = df.shift(1).iloc[i][support_level]
                cap = cap * (1.0 + ((exit_price - position_price) / position_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': position_date,
                              'enter_price': position_price,
                              'enter_high': enter_high,
                              'enter_low': enter_low,
                              'enter_open': enter_open,
                              'enter_close': enter_close,
                              'enter_previous_resistance': enter_previous_resistance,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'exit_high': exit_high,
                              'exit_low': exit_low,
                              'exit_open': exit_open,
                              'exit_close': exit_close,
                              'exit_previous_support': exit_previous_support,
                              'win': exit_price > position_price,
                              'change%': ((exit_price - position_price) / position_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['CE_BUY']:
            if not buy:
                buy = True
        i += 1

    print(ticker, cap)
    return trades, cap


def chandelier_zlema_based_trade(ticker, df, ce_period, ce_multiplier, zlema_period, short_enabled=False):

    df = chandalier_exit_highest_high_lowest_low(df, ce_period, ce_multiplier)
    df = zero_lag_ema(df, zlema_period)

    i = 0
    long_position = False
    short_position = False
    position_price = None
    position_date = None
    stop_loss = None
    take_profit = None
    cap = 100.0

    trades = []

    if short_enabled:
        pass

    else:
        while i < len(df):
            if df.iloc[i]['CE_BUY'] & (df.iloc[i]['Low'] < df.iloc[i][f'ZLEMA{zlema_period}'] < df.iloc[i]['High']):
                if not long_position:
                    position_price = df.shift(-1).iloc[i]['Open']
                    position_date = df.shift(-1).iloc[i]['Date']
                    stop_loss = df['Low'].rolling(10).min().iloc[i]
                    take_profit = abs(position_price - stop_loss)*2 + position_price
                    long_position = True
            if long_position:
                if df.iloc[i]['Low'] < stop_loss < df.iloc[i]['High']:
                    exit_price = stop_loss
                    exit_date = df.iloc[i]['Date']
                    cap = cap * (1.0 + ((exit_price - position_price) / position_price))
                    trades.append(
                        {'symbol': ticker, 'type': 'long', 'enter_date': position_date, 'enter_price': position_price,
                         'stop_loss': stop_loss, 'take_profit': take_profit,
                         'exit_date': exit_date, 'exit_price': exit_price, 'win': exit_price > position_price,
                         'change%': ((exit_price - position_price) / position_price) * 100})
                    long_position = False
                    stop_loss = None
                    take_profit = None
                elif df.iloc[i]['Low'] < take_profit < df.iloc[i]['High']:
                    exit_price = take_profit
                    exit_date = df.iloc[i]['Date']
                    cap = cap * (1.0 + ((exit_price - position_price) / position_price))
                    trades.append(
                        {'symbol': ticker, 'type': 'long', 'enter_date': position_date, 'enter_price': position_price,
                         'stop_loss': stop_loss, 'take_profit': take_profit,
                         'exit_date': exit_date, 'exit_price': exit_price, 'win': exit_price > position_price,
                         'change%': ((exit_price - position_price) / position_price) * 100})
                    long_position = False
                    stop_loss = None
                    take_profit = None
            i += 1

    print(ticker, cap)
    return trades, cap


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import itertools

    tickers = get_all_snp_stocks()

    ticker_returns = []

    all_trades = []

    # ticker_returns_s_r_long = []
    # ticker_returns_r_s_long = []
    # all_trades_s_r_long = []
    # all_trades_r_s_long = []

    # support = 'S1'
    # resistance = 'R3'
    ce_period = 1
    atr_multiplier = 1.85

    support_levels = ['S1', 'S2', 'S3']
    resistance_levels = ['R1', 'R2', 'R3']
    support_resistance_pairs = list(itertools.product(support_levels, resistance_levels))

    for pair in support_resistance_pairs:
        support, resistance = pair[0], pair[1]

        ticker_returns_s_r_long = []
        ticker_returns_r_s_long = []
        all_trades_s_r_long = []
        all_trades_r_s_long = []

        for ticker in tickers:
            try:
                df = pd.read_csv(download_stock_day(ticker))
            except ValueError:
                continue
            df = df[-1008:]
            # trades, final_cap = chandelier_based_trade(ticker, df, 1, 1.85, short_enabled=False)
            trades, final_cap = chandelier_based_trade_break_resistance(ticker, df, ce_period, atr_multiplier, support, resistance)
            all_trades_s_r_long = all_trades_s_r_long + trades
            all_trades_df = pd.DataFrame(all_trades_s_r_long)
            all_trades_df.to_csv(save_under_results_path(
                f'all_tickers_chandelier_based_trade_ce_1_multiplier_1-85_break_resistance_{support}_{resistance}_fixed.csv'))
            ticker_returns_s_r_long.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0})
            ticker_returns_df = pd.DataFrame(ticker_returns_s_r_long)
            ticker_returns_df.to_csv(save_under_results_path(
                f'ticker_returns_chandelier_based_trade_ce_1_multiplier_1-85_break_resistance_{support}_{resistance}_fixed.csv'))

            trades, final_cap = chandelier_based_trade_break_resistance(ticker, df, ce_period, atr_multiplier, resistance, support)
            all_trades_r_s_long = all_trades_r_s_long + trades
            all_trades_df = pd.DataFrame(all_trades_r_s_long)
            all_trades_df.to_csv(save_under_results_path(
                f'all_tickers_chandelier_based_trade_ce_1_multiplier_1-85_break_resistance_{resistance}_{support}_fixed.csv'))
            ticker_returns_r_s_long.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0})
            ticker_returns_df = pd.DataFrame(ticker_returns_r_s_long)
            ticker_returns_df.to_csv(save_under_results_path(
                f'ticker_returns_chandelier_based_trade_ce_1_multiplier_1-85_break_resistance_{resistance}_{support}_fixed.csv'))

    # ticker = 'PYPL'
    # df = pd.read_csv(download_stock(ticker))
    # df = df[-365:]
    #
    # trades, final_cap = chandelier_based_trade(ticker, df, short_enabled=True)
