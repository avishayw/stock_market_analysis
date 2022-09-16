import pandas as pd
import numpy as np
from indicators.momentum_indicators import simple_moving_average, rsi, stochastic
from indicators.market_condition import get_market_trend_based_on_spy_and_stock_sma200


def bearish_bullish_sma_rsi_stoch(ticker, df, sma200_angle_period, price_above_below_sma50_period, price_above_below_sma200_period, take_profit_pct, stop_loss_pct):
    f"""
    Trading stocks based on market condition.
    
    Bullish and Bearish criteria based on {get_market_trend_based_on_spy_and_stock_sma200} function
    
    Enter LONG conditions:
    1. Market Up trend & prices are above SMA200 in the last {price_above_below_sma200_period} days
    2. Prices above SMA50 in the last {price_above_below_sma50_period} days
    3. SMA3 angle is positive
    4. RSI < 30 # Skipping for now
    5. RSI angle is positive # Skipping for now
    6. Stochastic < 20
    7. Stochastic angle is positive
    
    Take profit LONG:
    Profit reached {take_profit_pct}
    
    Stop loss LONG:
    Loss reached {stop_loss_pct}
    
    
    Enter SHORT conditions:
    1. Market Up trend & prices are below SMA200 in the last {price_above_below_sma200_period} days
    2. Prices below SMA50 in the last {price_above_below_sma50_period} days
    3. SMA3 angle is negative
    4. RSI > 70 # Skipping for now
    5. RSI angle is negative # Skipping for now
    6. Stochastic > 80
    7. Stochastic angle is negative
    
    Take profit SHORT:
    Profit reached {take_profit_pct}
    
    Stop loss SHORT:
    Loss reached {stop_loss_pct}
    
    :param ticker: 
    :param df: 
    :return: 
    """

    df = get_market_trend_based_on_spy_and_stock_sma200(df, sma200_angle_period)
    df = rsi(df, 14)
    df = stochastic(df, 14)
    df = simple_moving_average(df, 200)
    df = simple_moving_average(df, 50)
    df = simple_moving_average(df, 3)

    # LONG conditions
    df['Price above SMA200'] = np.where(df['Low'] > df['SMA200'], 1, 0)
    df['Price above SMA50'] = np.where(df['Low'] > df['SMA50'], 1, 0)
    df[f'Price above SMA200 in the last {price_above_below_sma200_period} days'] = \
        np.where(df['Price above SMA200'].rolling(price_above_below_sma200_period).sum() == price_above_below_sma200_period, True, False)
    df[f'Price above SMA50 in the last {price_above_below_sma50_period} days'] = \
        np.where(
            df['Price above SMA50'].rolling(price_above_below_sma50_period).sum() == price_above_below_sma50_period,
            True, False)
    df['SMA3 angle'] = (df['SMA3'] - df.shift(1)['SMA3']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df['SMA3 angle positive'] = np.where(df['SMA3 angle'] > 0, True, False)
    df['RSI angle'] = (df['RSI'] - df.shift(1)['RSI']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df['RSI < 30 & angle positive'] = np.where((df['RSI'] < 30) & (df['RSI angle'] > 0), True, False)
    df['Stochastic angle'] = (df['stochastic'] - df.shift(1)['stochastic']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df['Stochastic < 20 & angle positive'] = np.where((df['stochastic'] < 20) & (df['Stochastic angle'] > 0), True, False)
    # df['BUY'] = np.where(
    #     (df[f'Price above SMA200 in the last {price_above_below_sma200_period} days']) &
    #     (df[f'Price above SMA50 in the last {price_above_below_sma50_period} days']) &
    #     df['SMA3 angle positive'] &
    #     df['RSI < 30 & angle positive'] &
    #     df['Stochastic < 20 & angle positive'], True, False
    # )
    df['BUY'] = np.where(
        (df[f'Price above SMA200 in the last {price_above_below_sma200_period} days']) &
        (df[f'Price above SMA50 in the last {price_above_below_sma50_period} days']) &
        df['SMA3 angle positive'] &
        df['Stochastic < 20 & angle positive'], True, False
    )

    # TODO: remove prints
    # LONG prints
    # print(f'Len DataFrame: {len(df)}')
    # print(f'Price above SMA200: {len(df.loc[df["Price above SMA200"] == 1])}')
    # print(f'Price above SMA50: {len(df.loc[df["Price above SMA50"] == 1])}')
    # print(f'Price above SMA200 in the last {price_above_below_sma200_period} days:'
    #       f'{len(df.loc[df[f"Price above SMA200 in the last {price_above_below_sma200_period} days"]])}')
    # print(f'Price above SMA50 in the last {price_above_below_sma50_period} days:'
    #       f'{len(df.loc[df[f"Price above SMA50 in the last {price_above_below_sma50_period} days"]])}')
    # print(f'SMA3 angle positive: {len(df.loc[df["SMA3 angle positive"]])}')
    # print(f'RSI < 30 & angle positive: {len(df.loc[df["RSI < 30 & angle positive"]])}')
    # print(f'Stochastic < 20 & angle positive: {len(df.loc[df["Stochastic < 20 & angle positive"]])}')

    # SHORT conditions
    df['Price below SMA200'] = np.where(df['High'] < df['SMA200'], 1, 0)
    df['Price below SMA50'] = np.where(df['High'] < df['SMA50'], 1, 0)
    df[f'Price below SMA200 in the last {price_above_below_sma200_period} days'] = \
        np.where(
            df['Price below SMA200'].rolling(price_above_below_sma200_period).sum() == price_above_below_sma200_period,
            True, False)
    df[f'Price below SMA50 in the last {price_above_below_sma50_period} days'] = \
        np.where(
            df['Price below SMA50'].rolling(price_above_below_sma50_period).sum() == price_above_below_sma50_period,
            True, False)
    df['SMA3 angle'] = (df['SMA3'] - df.shift(1)['SMA3']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df['SMA3 angle negative'] = np.where(df['SMA3 angle'] < 0, True, False)
    df['RSI angle'] = (df['RSI'] - df.shift(1)['RSI']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df['RSI > 70 & angle negative'] = np.where((df['RSI'] > 70) & (df['RSI angle'] < 0), True, False)
    df['Stochastic angle'] = (df['stochastic'] - df.shift(1)['stochastic']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df['Stochastic > 80 & angle negative'] = np.where((df['stochastic'] > 80) & (df['Stochastic angle'] < 0), True,
                                                      False)
    # df['SELL'] = np.where(
    #     (df[f'Price below SMA200 in the last {price_above_below_sma200_period} days']) &
    #     (df[f'Price below SMA50 in the last {price_above_below_sma50_period} days']) &
    #     df['SMA3 angle negative'] &
    #     df['RSI > 70 & angle negative'] &
    #     df['Stochastic > 80 & angle negative'], True, False
    # )
    df['SELL'] = np.where(
        (df[f'Price below SMA200 in the last {price_above_below_sma200_period} days']) &
        (df[f'Price below SMA50 in the last {price_above_below_sma50_period} days']) &
        df['SMA3 angle negative'] &
        df['Stochastic > 80 & angle negative'], True, False
    )

    # TODO: remove prints
    # SHORT prints
    # print(f'Len DataFrame: {len(df)}')
    # print(f'Price below SMA200: {len(df.loc[df["Price below SMA200"] == 1])}')
    # print(f'Price below SMA50: {len(df.loc[df["Price below SMA50"] == 1])}')
    # print(f'Price below SMA200 in the last {price_above_below_sma200_period} days:'
    #       f'{len(df.loc[df[f"Price below SMA200 in the last {price_above_below_sma200_period} days"]])}')
    # print(f'Price below SMA50 in the last {price_above_below_sma50_period} days:'
    #       f'{len(df.loc[df[f"Price below SMA50 in the last {price_above_below_sma50_period} days"]])}')
    # print(f'SMA3 angle negative: {len(df.loc[df["SMA3 angle negative"]])}')
    # print(f'RSI > 70 & angle negative: {len(df.loc[df["RSI > 70 & angle negative"]])}')
    # print(f'Stochastic > 80 & angle negative: {len(df.loc[df["Stochastic > 80 & angle negative"]])}')

    i = 0
    long_position = False
    short_position = False
    position_price = None
    position_date = None
    stop_loss = None
    take_profit = None
    cap = 100.0

    trades = []

    while i < len(df):
        if not (long_position or short_position):
            if df.iloc[i]['BUY']:
                print('Entered LONG')
                position_price = df.shift(-1).iloc[i]['Open']
                position_date = df.shift(-1).iloc[i]['Date']
                stop_loss = position_price*(1 - (float(stop_loss_pct)/100.0))
                take_profit = position_price*(1 + (float(take_profit_pct)/100.0))
                long_position = True
            elif df.iloc[i]['SELL']:
                print('Entered SHORT')
                position_price = df.shift(-1).iloc[i]['Open']
                position_date = df.shift(-1).iloc[i]['Date']
                stop_loss = position_price * (1 + (float(stop_loss_pct) / 100.0))
                take_profit = position_price * (1 - (float(take_profit_pct) / 100.0))
                short_position = True
        elif long_position:
            if df.iloc[i]['Low'] < stop_loss < df.iloc[i]['High']:
                exit_price = stop_loss
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((exit_price - position_price) / position_price))
                trade_dict = {'symbol': ticker, 'type': 'long', 'enter_date': position_date, 'enter_price': position_price,
                     'stop_loss': stop_loss, 'take_profit': take_profit,
                     'exit_date': exit_date, 'exit_price': exit_price, 'win': exit_price > position_price,
                     'change%': ((exit_price - position_price) / position_price) * 100}
                trades.append(trade_dict)
                print(trade_dict)
                long_position = False
                stop_loss = None
                take_profit = None
            elif df.iloc[i]['Low'] < take_profit < df.iloc[i]['High']:
                exit_price = take_profit
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((exit_price - position_price) / position_price))
                trade_dict = {'symbol': ticker, 'type': 'long', 'enter_date': position_date,
                              'enter_price': position_price,
                              'stop_loss': stop_loss, 'take_profit': take_profit,
                              'exit_date': exit_date, 'exit_price': exit_price, 'win': exit_price > position_price,
                              'change%': ((exit_price - position_price) / position_price) * 100}
                trades.append(trade_dict)
                print(trade_dict)
                long_position = False
                stop_loss = None
                take_profit = None
        elif short_position:
            if df.iloc[i]['Low'] < stop_loss < df.iloc[i]['High']:
                exit_price = stop_loss
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((position_price - exit_price) / position_price))
                trade_dict = {'symbol': ticker, 'type': 'short', 'enter_date': position_date,
                              'enter_price': position_price,
                              'stop_loss': stop_loss, 'take_profit': take_profit,
                              'exit_date': exit_date, 'exit_price': exit_price, 'win': position_price > exit_price,
                              'change%': ((position_price - exit_price) / position_price) * 100}
                trades.append(trade_dict)
                print(trade_dict)
                short_position = False
                stop_loss = None
                take_profit = None
            elif df.iloc[i]['Low'] < take_profit < df.iloc[i]['High']:
                exit_price = take_profit
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((position_price - exit_price) / position_price))
                trade_dict = {'symbol': ticker, 'type': 'short', 'enter_date': position_date,
                              'enter_price': position_price,
                              'stop_loss': stop_loss, 'take_profit': take_profit,
                              'exit_date': exit_date, 'exit_price': exit_price, 'win': position_price > exit_price,
                              'change%': ((position_price - exit_price) / position_price) * 100}
                trades.append(trade_dict)
                print(trade_dict)
                short_position = False
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

    sma200_angle_period = 5
    price_above_below_sma50_period = 5
    price_above_below_sma200_period = 10
    take_profit_pct = 15
    stop_loss_pct = 5

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        print(f'\n\n{ticker}')
        df = df[-1095:]
        # trades, final_cap = chandelier_based_trade(ticker, df, 1, 1.85, short_enabled=False)
        trades, final_cap = bearish_bullish_sma_rsi_stoch(ticker, df, sma200_angle_period, price_above_below_sma50_period, price_above_below_sma200_period, take_profit_pct, stop_loss_pct)
        all_trades = all_trades + trades
        all_trades_df = pd.DataFrame(all_trades)
        all_trades_df.to_csv(save_under_results_path(f'bearish_bullish_sma_rsi_stochastic.csv'))
        ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0)/100.0)*100.0})
        ticker_returns_df = pd.DataFrame(ticker_returns)
        ticker_returns_df.to_csv(save_under_results_path('bearish_bullish_sma_rsi_stochastic_ticker_returns.csv'))

    # ticker = 'PYPL'
    # df = pd.read_csv(download_stock(ticker))
    # df = df[-1095:]
    # trades, final_cap = bearish_bullish_sma_rsi_stoch(ticker, df, sma200_angle_period, price_above_below_sma50_period,
    #                                                   price_above_below_sma200_period, take_profit_pct, stop_loss_pct)