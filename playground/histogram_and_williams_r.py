from indicators.momentum_indicators import williams_r
import numpy as np
import pandas as pd
import math
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta
from astropy.stats import freedman_bin_width


ticker = 'AAPL'
stock = yf.Ticker(ticker)

stock_df = stock.history(period='max', interval='1d')[-1008:].reset_index()
stock_df['Datetime'] = pd.to_datetime(stock_df['Date'])

days_back_list = [5, 9, 20, 50, 100, 200]

for days_back in days_back_list:

    start_date = stock_df.iloc[-1]['Datetime'] - relativedelta(days=days_back)
    sample_df = stock_df.loc[stock_df['Datetime'] >= start_date].copy().reset_index().drop(columns=['index'])

    # print(f'First df close: {sample_df.iloc[0]["Date"]}, {sample_df.iloc[0]["Close"]}')
    # print(f'Last df close: {sample_df.iloc[-1]["Date"]}, {sample_df.iloc[-1]["Close"]}')
    prices = []

    for row in range(len(sample_df)):
        high = sample_df.iloc[row]['High']
        low = sample_df.iloc[row]['Low']
        prices = prices + list(np.arange(low, high, .01))

    prices = sorted(prices)

    # histogram
    # nbins = int(math.ceil(math.sqrt(len(prices))))
    bin_width = freedman_bin_width(prices)
    nbins = math.ceil((np.max(prices) - np.min(prices))/bin_width)
    # print(nbins, bin_width)
    bins = np.linspace(np.ceil(min(prices)),
                       np.floor(max(prices)),
                       nbins)

    occurrences, price_ranges = np.histogram(prices, bins)
    histogram_dict = {}

    for i in range(len(occurrences)):
        histogram_dict[occurrences[i]] = (round(price_ranges[i], 2), round(price_ranges[i+1], 2))

    print(f'stats: mean: {np.mean(occurrences)} stdev: {np.std(occurrences)} coefficient of variation: {np.std(occurrences)/np.mean(occurrences)}')

    print(f'days back: {days_back}')
    print(histogram_dict[max(occurrences)])