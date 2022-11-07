"""
Given some days period, price histogram can be taken from the prices list, which is derived from taking every
day, creating a range of prices from low to high in .01 steps, and adding up all the list from the different days.
After getting the price distribution, skew and cov (stdev/mean) can be drawn to get info about the distribution.
If the skew is positive (specifically greater than 0.3) it mean that there is a leg to the right and most of the
active area happens in lower prices.
If the cov is smaller than 0.7, then it means that the mean is somewhat reliable.
However, cov greater than 0.9 can also present opportunities. If the today's close is smaller than the 10th
percentile of prices, it means that something bad affected the stock prices (probably some bad news) and negative
change can be expected for the following days.
If today's close is greater than the 90th percentile, skew is positive and cov is smaller than 0.7, it might indicate
on unusual high price for the stock, and an aggressive sell can be expected.

This script is intended to check the probabilities of these two cases
"""
import numpy as np
from scipy.stats import skew, kurtosis


def price_distribution(df, period):

    start_idx = df.index[0]
    df['mean'] = np.nan
    df['median'] = np.nan
    df['stdev'] = np.nan
    df['cov'] = np.nan
    df['skew'] = np.nan
    df['kurtosis'] = np.nan
    df['mean+1stdev'] = np.nan
    df['mean-1stdev'] = np.nan
    df['mean+2stdev'] = np.nan
    df['mean-2stdev'] = np.nan
    df['10%'] = np.nan
    df['90%'] = np.nan
    df['change_next_day'] = np.nan

    for i in range(period, len(df)):
        sample_df = df[i - period:i].copy()

        prices = []

        for row in range(len(sample_df)):
            high = sample_df.iloc[row]['High']
            low = sample_df.iloc[row]['Low']
            prices = prices + list(np.arange(low, high, .01))

        prices = sorted(prices)

        df.loc[start_idx + i, 'mean'] = np.mean(prices)
        df.loc[start_idx + i, 'median'] = np.median(prices)
        df.loc[start_idx + i, 'stdev'] = np.std(prices)
        df.loc[start_idx + i, 'cov'] = np.std(prices)/np.mean(prices)
        df.loc[start_idx + i, 'skew'] = skew(prices)
        df.loc[start_idx + i, 'kurtosis'] = kurtosis(prices)
        df.loc[start_idx + i, 'mean+1stdev'] = np.mean(prices) + np.std(prices)
        df.loc[start_idx + i, 'mean-1stdev'] = np.mean(prices) - np.std(prices)
        df.loc[start_idx + i, 'mean+2stdev'] = np.mean(prices) + np.std(prices)*2
        df.loc[start_idx + i, 'mean-2stdev'] = np.mean(prices) - np.std(prices)*2
        df.loc[start_idx + i, '10%'] = np.percentile(prices, 10)
        df.loc[start_idx + i, '90%'] = np.percentile(prices, 90)
        df.loc[start_idx + i, 'change_next_day'] = ((df.shift(-1).iloc[i]['Close'] - df.shift(-1).iloc[i]['Open'])/df.shift(-1).iloc[i]['Open'])*100

    return df


def method_probabilities(df):
    method1 = """
    1. Given:
    a. Close > 90%*1.1
    b. cov < 0.02
    c. kurtosis < -0.5

    What's the probability for negative change the next day
    """
    # print('method1')
    condition1_df = df.loc[(df['Close'] > df['90%']*1.05) & (df['cov'] < 0.02) & (df['kurtosis'] < -0.5)].copy()
    if not condition1_df.empty:
        print(len(condition1_df.loc[condition1_df['change_next_day'] < 0])/len(condition1_df))
    # else:
    #     print('no occurrences of condition 1')

    """
    2. Given:
    a. Close < 10%
    b. cov > 0.9

    What's the probability for negative change the next day 
    """
    condition2_df = df.loc[(df['Close'] < df['10%']) & (df['cov'] > 0.9)].copy()
    # print('method2')
    if not condition2_df.empty:
        print(len(condition2_df.loc[condition2_df['change_next_day'] < 0]) / len(condition2_df))
    # else:
    #     print('no occurrences of condition 2')

    return {'1': (len(condition1_df), len(condition1_df.loc[condition1_df['change_next_day'] < 0])),
            '2': (len(condition2_df), len(condition2_df.loc[condition2_df['change_next_day'] < 0]))}


if __name__=='__main__':
    from utils.paths import get_in_sample_data_csvs
    from utils.get_ticker_from_csv import get_ticker_from_csv
    import pandas as pd
    import os
    from utils.download_stock_csvs import download_stock_day

    csvs = get_in_sample_data_csvs()

    method1_occurrences = 0
    method1_confirmed = 0
    method2_occurrences = 0
    method2_confirmed = 0

    for csv in csvs:
        ticker = get_ticker_from_csv(csv)
        df = pd.read_csv(download_stock_day(ticker))
        df = price_distribution(df, 10)
        results = method_probabilities(df)
        method1_occurrences += results['1'][0]
        method1_confirmed += results['1'][1]
        method2_occurrences += results['2'][0]
        method2_confirmed += results['2'][1]
        if method1_occurrences > 0:
            print('1', method1_confirmed/method1_occurrences)
        if method2_occurrences > 0:
            print('2', method2_confirmed/method2_occurrences)