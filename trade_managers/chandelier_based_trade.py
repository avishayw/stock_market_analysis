from indicators.exit_indicators import chandalier_exit_close, chandalier_exit_highest_high_lowest_low, chandalier_exit_highest_high_lowest_high
from indicators.trend_indicators import zero_lag_ema


def chandelier_based_trade(ticker, df, period, multiplier, short_enabled=False):

    # df['heikin_ashi_open'] = (df.shift(1)['Open'] + df.shift(1)['Close']) / 2
    # df['heikin_ashi_close'] = (df['High'] + df['Close'] + df['Low'] + df['Open']) / 4

    # df['original_open'] = df['Open']
    # df['original_close'] = df['Close']
    # df['Open'] = df['heikin_ashi_open']
    # df['Close'] = df['heikin_ashi_close']

    df = chandalier_exit_highest_high_lowest_low(df, period, multiplier)

    # df['Open'] = df['original_open']
    # df['Close'] = df['original_close']



    i = 0
    long_position = False
    short_position = False
    position_price = None
    position_date = None
    cap = 100.0

    trades = []

    if short_enabled:
        while i < len(df):
            if df.iloc[i]['CE_BUY']:
                if short_position:
                    exit_price = df.shift(-1).iloc[i]['Open']
                    exit_date = df.shift(-1).iloc[i]['Date']
                    cap = cap * (1.0 + ((position_price - exit_price) / position_price))
                    trades.append(
                        {'symbol': ticker, 'type': 'short', 'enter_date': position_date, 'enter_price': position_price,
                         'exit_date': exit_date, 'exit_price': exit_price, 'win': position_price > exit_price,
                         'change%': ((position_price - exit_price) / position_price) * 100})
                    short_position = False
                if not long_position:
                    position_price = df.shift(-1).iloc[i]['Open']
                    position_date = df.shift(-1).iloc[i]['Date']
                    long_position = True
            elif df.iloc[i]['CE_SELL']:
                if long_position:
                    exit_price = df.shift(-1).iloc[i]['Open']
                    exit_date = df.shift(-1).iloc[i]['Date']
                    cap = cap * (1.0 + ((exit_price - position_price) / position_price))
                    trades.append(
                        {'symbol': ticker, 'type': 'long', 'enter_date': position_date, 'enter_price': position_price,
                         'exit_date': exit_date, 'exit_price': exit_price, 'win': exit_price > position_price,
                         'change%': ((exit_price - position_price) / position_price) * 100})
                    long_position = False
                if not short_position:
                    position_price = df.shift(-1).iloc[i]['Open']
                    position_date = df.shift(-1).iloc[i]['Date']
                    short_position = True
            i += 1
        pass

    else:
        while i < len(df):
            if df.iloc[i]['CE_BUY']:
                if not long_position:
                    position_price = df.shift(-1).iloc[i]['Open']
                    position_date = df.shift(-1).iloc[i]['Date']
                    long_position = True
            elif df.iloc[i]['CE_SELL']:
                if long_position:
                    exit_price = df.shift(-1).iloc[i]['Open']
                    exit_date = df.shift(-1).iloc[i]['Date']
                    cap = cap * (1.0 + ((exit_price - position_price) / position_price))
                    trades.append(
                        {'symbol': ticker, 'type': 'long', 'enter_date': position_date, 'enter_price': position_price,
                         'exit_date': exit_date, 'exit_price': exit_price, 'win': exit_price > position_price,
                         'change%': ((exit_price - position_price) / position_price) * 100})
                    long_position = False
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

    tickers = get_all_snp_stocks()

    ticker_returns = []

    all_trades = []

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        df = df[-365:]
        # trades, final_cap = chandelier_based_trade(ticker, df, 1, 1.85, short_enabled=False)
        trades, final_cap = chandelier_zlema_based_trade(ticker, df, 1, 1.85, 32, short_enabled=False)
        all_trades = all_trades + trades
        all_trades_df = pd.DataFrame(all_trades)
        all_trades_df.to_csv(save_under_results_path(f'chandelier_highest_high_lowest_low_multiplier_1-85_zlema_32_no_short_results.csv'))
        ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0)/100.0)*100.0})
        ticker_returns_df = pd.DataFrame(ticker_returns)
        ticker_returns_df.to_csv(save_under_results_path('chandelier_highest_high_lowest_low_multiplier_1-85_zlema_32_no_short_ticker_returns.csv'))

    # ticker = 'PYPL'
    # df = pd.read_csv(download_stock(ticker))
    # df = df[-365:]
    #
    # trades, final_cap = chandelier_based_trade(ticker, df, short_enabled=True)
