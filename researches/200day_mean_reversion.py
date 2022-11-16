"""
I want to check the mean reversion around 200d moving average across S&P stocks
"""
from utils.get_all_stocks import get_all_snp_stocks
from utils.download_stock_csvs import download_stock_day
import pandas as pd
from pandas.errors import EmptyDataError
import numpy as np
from datetime import datetime

tickers = get_all_snp_stocks()
tickers_crosses = []

for ticker in tickers:
    try:
        df = pd.read_csv(download_stock_day(ticker)).reset_index()
    except ValueError as e:
        continue

    df['Date'] = df['Date'].map(lambda x: str(x).split(' ')[0])
    df['SMA200'] = df['Close'].rolling(200).mean()
    df['Cross'] = np.where(((df['Close'] > df['SMA200']) & (df.shift(1)['Close'] < df.shift(1)['SMA200'])) |
                           ((df['Close'] < df['SMA200']) & (df.shift(1)['Close'] > df.shift(1)['SMA200'])), True, False)
    cross_df = df.loc[df['Cross']].copy()
    if not len(cross_df) < 2:
        if len(cross_df) % 2 != 0:
            cross_df = cross_df[:-1]
        for i in range(0, len(cross_df)-1):
            cross_start_date = cross_df.iloc[i]['Date']
            cross_start_idx = cross_df.index[i]
            cross_end_date = cross_df.iloc[i + 1]['Date']
            cross_end_idx = cross_df.index[i + 1]
            cross_days = (datetime.strptime(cross_end_date, '%Y-%m-%d') - datetime.strptime(cross_start_date,
                                                                            '%Y-%m-%d')).days
            period_df = df.loc[cross_start_idx:cross_end_idx].copy()
            period_df['Close_SMA200_pct'] = (period_df['Close'] / period_df['SMA200'] - 1) * 100.0
            if cross_df.iloc[i]['Close'] > cross_df.iloc[i]['SMA200']:
                cross_type = 'cross_above'
                max_diff = period_df['Close_SMA200_pct'].max()
                max_diff_idx = period_df['Close_SMA200_pct'].idxmax()
                max_diff_date = period_df.loc[max_diff_idx, 'Date']
            else:
                cross_type = 'cross_below'
                max_diff = period_df['Close_SMA200_pct'].min()
                max_diff_idx = period_df['Close_SMA200_pct'].idxmin()
                max_diff_date = period_df.loc[max_diff_idx, 'Date']
            days_to_max = (datetime.strptime(max_diff_date, '%Y-%m-%d') - datetime.strptime(cross_start_date,
                                                                                             '%Y-%m-%d')).days

            cross_dict = {'symbol': ticker,
                          'cross_type': cross_type,
                          'cross_start': cross_start_date,
                          'cross_end': cross_end_date,
                          'cross_days': cross_days,
                          'max_diff': max_diff,
                          'days_to_max': days_to_max}
            print(cross_dict)
            tickers_crosses.append(cross_dict)
            pd.DataFrame(tickers_crosses).to_csv('200d_mean_reversion_ticker_cross.csv')
