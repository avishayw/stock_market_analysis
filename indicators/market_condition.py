import pandas as pd
import numpy as np
from indicators.momentum_indicators import simple_moving_average
from indicators.trend_indicators import exponential_moving_average
from utils.download_stock_csvs import download_stock_day


def get_market_trend_based_on_spy_and_stock_sma200(df, angle_period):
    f"""
    Market condition: bullish ("up trend") or bearish ("down trend")
    
    Bullish criteria:
    1. SPY SMA200 & EMA200 lines' angle is positive in the last {angle_period} days
    2. Stock SMA200 & EMA200 lines' angle is positive in the last {angle_period} days
    
    Bearish criteria:
    1. SPY SMA200 & EMA200 lines' angle is negative in the last {angle_period} days
    2. Stock SMA200 & EMA200 lines' angle is negative in the last {angle_period} days
    
    :param df: pd.DataFrame - ticker historical daily price
    :param angle_period: int - number of days for the angle to be positive (bullish) or negative (bearish)
    :return: df: pd.DataFrame additional 'up_trend' & 'down_trend' boolean columns
    """
    market = pd.read_csv(download_stock_day('SPY'))
    df['Datetime'] = pd.to_datetime(df['Date'])
    market['Datetime'] = pd.to_datetime(market['Date'])
    market = market.loc[(df.iloc[0]['Datetime'] <= market['Datetime']) & (market['Datetime'] <= df.iloc[-1]['Datetime'])]
    df = df.loc[(market.iloc[0]['Datetime'] <= df['Datetime']) & (df['Datetime'] <= market.iloc[-1]['Datetime'])]
    df = simple_moving_average(df, 200)
    df = exponential_moving_average(df, 'Close', 200)
    market = simple_moving_average(market, 200)
    market = exponential_moving_average(market, 'Close', 200)
    df[f'SMA{200}_angle'] = (df[f'SMA{200}'] - df.shift(1)[f'SMA{200}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'EMA{200}_angle'] = (df[f'EMA{200}'] - df.shift(1)[f'EMA{200}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    market[f'SMA{200}_angle'] = (market[f'SMA{200}'] - market.shift(1)[f'SMA{200}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    market[f'EMA{200}_angle'] = (market[f'EMA{200}'] - market.shift(1)[f'EMA{200}']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df[f'SMA{200}_angle_positive_{angle_period}_days'] = np.where(df[f'SMA{200}_angle'].rolling(angle_period).min() > 0, True, False)
    df[f'EMA{200}_angle_positive_{angle_period}_days'] = np.where(df[f'EMA{200}_angle'].rolling(angle_period).min() > 0, True, False)
    df[f'market_SMA{200}_angle_positive_{angle_period}_days'] = np.where(market[f'SMA{200}_angle'].rolling(angle_period).min() > 0, True, False)
    df[f'market_EMA{200}_angle_positive_{angle_period}_days'] = np.where(market[f'EMA{200}_angle'].rolling(angle_period).min() > 0, True, False)
    df[f'SMA{200}_angle_negative_{angle_period}_days'] = np.where(df[f'SMA{200}_angle'].rolling(angle_period).max() < 0, True, False)
    df[f'EMA{200}_angle_negative_{angle_period}_days'] = np.where(df[f'EMA{200}_angle'].rolling(angle_period).max() < 0, True, False)
    df[f'market_SMA{200}_angle_negative_{angle_period}_days'] = np.where(market[f'SMA{200}_angle'].rolling(angle_period).max() < 0, True, False)
    df[f'market_EMA{200}_angle_negative_{angle_period}_days'] = np.where(market[f'EMA{200}_angle'].rolling(angle_period).max() < 0, True, False)
    df['up_trend'] = np.where((df[f'SMA{200}_angle_positive_{angle_period}_days']) & (df[f'EMA{200}_angle_positive_{angle_period}_days']) & (df[f'market_SMA{200}_angle_positive_{angle_period}_days']) & (df[f'market_EMA{200}_angle_positive_{angle_period}_days']), True, False)
    df['down_trend'] = np.where((df[f'SMA{200}_angle_negative_{angle_period}_days']) & (df[f'EMA{200}_angle_negative_{angle_period}_days']) & (df[f'market_SMA{200}_angle_negative_{angle_period}_days']) & (df[f'market_EMA{200}_angle_negative_{angle_period}_days']), True, False)
    df.drop(columns=['Datetime', f'SMA200', 'EMA200', f'SMA{200}_angle', f'EMA{200}_angle',
                     f'SMA{200}_angle_positive_{angle_period}_days', f'EMA{200}_angle_positive_{angle_period}_days',
                     f'SMA{200}_angle_negative_{angle_period}_days', f'EMA{200}_angle_negative_{angle_period}_days',
                     f'market_SMA{200}_angle_positive_{angle_period}_days', f'market_EMA{200}_angle_positive_{angle_period}_days',
                     f'market_SMA{200}_angle_negative_{angle_period}_days', f'market_EMA{200}_angle_negative_{angle_period}_days'],
            axis=1, inplace=True)
    return df


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import json

    tickers = get_all_snp_stocks()

    ticker_returns = []

    all_trades = []

    pd.options.mode.chained_assignment = None # Disable SettingWithCopyWarning errors

    down_trend_tickers = []

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        df = df[-365:]
        df = get_market_trend(df)
        if df.iloc[-1]['down_trend']:
            down_trend_tickers.append(ticker)

    down_trend_tickers_dict = {}
    down_trend_tickers_dict['tickers'] = down_trend_tickers

    with open(save_under_results_path('down_trend_tickers.json'), 'w') as f:
        json.dump(down_trend_tickers_dict, f)


    # df = pd.read_csv(download_stock(ticker))
    #
    # df = get_market_trend(df)
    #
    # df.to_csv(save_under_results_path(f'{ticker}_market_condition.csv'))
    #
    # print(df.iloc[-1][['up_trend', 'down_trend']])