import numpy as np
import pandas as pd
from indicators.trend_indicators import exponential_moving_average
from indicators.momentum_indicators import simple_moving_average


def ema_diff(df, ema1=20, ema2=200):
    """
    Question to be asked:

    After the faster ema goes above the slower ema - what was the maximum difference before the faster ema went below
    the slower ema?

    Due to different stock prices difference will be measured in percentages.

    """
    df = exponential_moving_average(df, 'Close', ema1)
    df = exponential_moving_average(df, 'Close', ema2)
    df['Datetime'] = pd.to_datetime(df['Date'])
    df['emas_ratio'] = ((df[f'EMA{ema1}'] - df[f'EMA{ema2}'])/df[f'EMA{ema1}'])*100.0
    df['upcross'] = np.where((df.shift(1)[f'EMA{ema1}'] < df.shift(1)[f'EMA{ema2}']) &
                             (df[f'EMA{ema1}'] > df[f'EMA{ema2}']), True, False)
    df['downcross'] = np.where((df.shift(1)[f'EMA{ema1}'] > df.shift(1)[f'EMA{ema2}']) &
                             (df[f'EMA{ema1}'] < df[f'EMA{ema2}']), True, False)

    differences = []
    after_cross = False
    for i in range(len(df)):
        if df.iloc[i]['upcross']:
            start_date = df.iloc[i]['Datetime']
            after_cross = True
        elif df.iloc[i]['downcross'] and after_cross:
            end_date = df.iloc[i]['Datetime']
            period_df = df.loc[(df['Datetime'] >= start_date) & (df['Datetime'] <= end_date)]
            differences.append(period_df['emas_ratio'].max())
            after_cross = False

    return differences


def ema_diff_2(ticker, df, ema1=20, ema2=200):
    """
    Question to be asked:

    What are the statistics for the time ema fast is above ema slow for different long term trend angles

    """
    df = exponential_moving_average(df, 'Close', ema1)
    df = exponential_moving_average(df, 'Close', ema2)
    df = simple_moving_average(df, 200)
    df['SMA200angle'] = (df[f'SMA200'] - df.shift(1)[f'SMA200']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
    df['Datetime'] = pd.to_datetime(df['Date'])
    df['emas_ratio'] = ((df[f'EMA{ema1}'] - df[f'EMA{ema2}'])/df[f'EMA{ema1}'])*100.0
    df['upcross'] = np.where((df.shift(1)[f'EMA{ema1}'] < df.shift(1)[f'EMA{ema2}']) &
                             (df[f'EMA{ema1}'] > df[f'EMA{ema2}']), True, False)
    df['downcross'] = np.where((df.shift(1)[f'EMA{ema1}'] > df.shift(1)[f'EMA{ema2}']) &
                             (df[f'EMA{ema1}'] < df[f'EMA{ema2}']), True, False)

    after_cross = False
    differences = []
    for i in range(len(df)):
        if df.iloc[i]['upcross']:
            start_date = df.iloc[i]['Datetime']
            after_cross = True
        elif df.iloc[i]['downcross'] and after_cross:
            end_date = df.iloc[i]['Datetime']
            period_df = df.loc[(df['Datetime'] >= start_date) & (df['Datetime'] <= end_date)]
            period_dict = {'ticker': ticker,
                                'max_ema_ratio': period_df['emas_ratio'].max(),
                                'duration_time': (period_df.iloc[-1]['Datetime'] - period_df.iloc[0]['Datetime']).days,
                                'mean_sma200_angle': period_df['SMA200angle'].mean()}
            print(period_dict)
            differences.append(period_dict)
            after_cross = False

    return differences


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import statistics
    import json

    tickers = list(set(get_all_snp_stocks() + get_all_nasdaq_100_stocks() + get_all_dow_jones_industrial_stocks() + ['SPY']))
    # all_tickers_differences = {}

    # for ticker in tickers:
    #     try:
    #         df = pd.read_csv(download_stock_day(ticker))[-2520:]
    #     except ValueError:
    #         continue
    #     ticker_differences = ema_diff(df)
    #     if len(ticker_differences) > 2:
    #         max_difference = max(ticker_differences)
    #         min_difference = min(ticker_differences)
    #         mean_difference = statistics.mean(ticker_differences)
    #         median_diffference = statistics.median(ticker_differences)
    #         standard_deviation = statistics.stdev(ticker_differences)
    #         print(ticker, max_difference, min_difference, mean_difference, median_diffference, standard_deviation)
    #         all_tickers_differences[ticker] = {'differences': ticker_differences,
    #                                            'max': max_difference,
    #                                            'min': min_difference,
    #                                            'mean': mean_difference,
    #                                            'median': median_diffference,
    #                                            'stdev': standard_deviation}
    #
    #         with open(save_under_results_path('ema_diff_20_200.json'), 'w') as f:
    #             json.dump(all_tickers_differences, f, indent=4)

    all_tickers_differences = []

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        if len(df) < 3528:
            continue
        all_tickers_differences = all_tickers_differences + ema_diff_2(ticker, df[-3528:-1008], ema1=20, ema2=50)
        pd.DataFrame(all_tickers_differences).to_csv(save_under_results_path('ema_diff_stats_20_50.csv'))
