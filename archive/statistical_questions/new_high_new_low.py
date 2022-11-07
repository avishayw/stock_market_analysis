"""
'52 week high!' '52 week low'. Common and alerting notifications from Yahoo Finance.
The statistical questions here are:
1. Given a new 52 week high reached, what's the probabilty for a positive change one day after?
2. Given a new 52 week low reached, what's the probabilty for a negative change one day after?
"""


def new_high_new_low(df, days_after=1):
    year_high = df['High'].rolling(252).max()
    year_low = df['Low'].rolling(252).min()
    new_high_count = len(df.loc[df['High'] > year_high.shift(1)])
    positive_change_after_count = len(df.loc[(df['High'] > year_high.shift(1)) &
                                           (df.shift(-days_after)['Close'] > df['Close'])])
    new_low_count = len(df.loc[df['Low'] < year_low.shift(1)])
    negative_change_after_count = len(df.loc[(df['Low'] < year_low.shift(1)) &
                                           (df.shift(-days_after)['Close'] < df['Close'])])
    # new_high_count = len(df.loc[(df['High'] > year_high.shift(1)) & (df.shift(-1)['High'] > year_high)])
    # positive_change_after_count = len(df.loc[(df['High'] > year_high.shift(1)) &
    #                                          (df.shift(-1)['High'] > year_high) &
    #                                          (df.shift(-2)['Close'] > df.shift(-1)['Close'])])
    # new_low_count = len(df.loc[(df['Low'] < year_low.shift(1)) & (df.shift(-1)['Low'] < year_low)])
    # negative_change_after_count = len(df.loc[(df['Low'] < year_low.shift(1)) &
    #                                          (df.shift(-1)['Low'] < year_low) &
    #                                          (df.shift(-2)['Close'] < df.shift(-1)['Close'])])
    return new_high_count, positive_change_after_count, new_low_count, negative_change_after_count


from utils.get_all_stocks import in_sample_tickers
from utils.download_stock_csvs import download_stock_day
import pandas as pd
import json
import os

tickers = in_sample_tickers()

total_new_high_count = 0
total_positive_change_after_count = 0
total_new_low_count = 0
total_negative_change_after_count = 0

for ticker in tickers:
    df = pd.read_csv(download_stock_day(ticker))
    new_high_count, positive_change_after_count, new_low_count, negative_change_after_count = new_high_new_low(df,
                                                                                                               days_after=2)
    if new_high_count > 0:
        print(ticker, 'high', positive_change_after_count/new_high_count)
    if new_low_count > 0:
        print(ticker, 'low', negative_change_after_count / new_low_count)
    total_new_high_count += new_high_count
    total_positive_change_after_count += positive_change_after_count
    total_new_low_count += new_low_count
    total_negative_change_after_count += negative_change_after_count

print(total_positive_change_after_count/total_new_high_count)
print(total_negative_change_after_count/total_new_low_count)