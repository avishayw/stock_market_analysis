from utils.download_stock_csvs import download_stock_day
import pandas as pd
import numpy as np
from indicators.momentum_indicators import rate_of_change
from indicators.my_indicators import percental_atr
from utils.get_all_stocks import get_all_nasdaq_100_stocks
from datetime import datetime

pd.set_option('display.max_columns', None)

tickers = get_all_nasdaq_100_stocks()
# tickers = ['BBBY']


for ticker in tickers:
    try:
        df = pd.read_csv(download_stock_day(ticker))
        df = df[-2004:]
    except ValueError:
        continue
    print(ticker)
    df['Datetime'] = pd.to_datetime(df['Date'])
    df.drop(columns=['Dividends', 'Stock Splits', 'Date'], inplace=True)
    df['change%'] = ((df['Close'] - df['Open'])/df['Open'])*100
    df = percental_atr(df, 5)
    df['tommorows_gap%'] = ((df.shift(-1)['Open'] - df['Close'])/df['Close'])*100
    # df['friday_jump'] = np.where((df['change%'] > df['%ATR5']*2) & (df['Datetime'].dt.day_name() == 'Friday'), True, False)

    research_df = df.loc[df['change%'] > 30.0]

    if not research_df.empty:
        print(research_df)

# ticker = 'BBBY'
# df = pd.read_csv(download_stock_day(ticker))
# df['Datetime'] = pd.to_datetime(df['Date'])
# df.drop(columns=['Dividends', 'Stock Splits', 'Date'], inplace=True)
# df['change%'] = ((df['Close'] - df['Open'])/df['Open'])*100
# df = percental_atr(df, 5)
# df['tommorows_gap%'] = ((df.shift(-1)['Open'] - df['Close'])/df['Close'])*100
# df['friday_jump'] = np.where((df['change%'] > df['%ATR5']*2) & (df['Datetime'].dt.day_name() == 'Friday'), True, False)
#
# print(df[-20:])