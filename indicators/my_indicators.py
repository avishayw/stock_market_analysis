import datetime

import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
from scipy.stats import gmean, hmean, skew, kurtosis
from machine_learning_stuff.linear_regression import rolling_ols
from sklearn.preprocessing import MinMaxScaler
from peakutils import baseline


def percental_atr(df, period):
    df['A'] = ((df['High'] - df['Low'])/df['Low'])*100.0
    df['B'] = (((df['High'] - df.shift(1)['Close']).abs())/df['Close'])*100.0
    df['C'] = (((df['Low'] - df.shift(1)['Close']).abs())/df['Close'])*100.0
    df = df[1:-1]
    start_idx = df.index[0]
    df['TR'] = df[['A','B','C']].max(axis=1)
    # atr = np.zeros(len(df))
    df[f'%ATR{period}'] = np.nan
    # atr[period-1] = df['TR'][0:period].mean()
    df.loc[start_idx + period - 1, f'%ATR{period}'] = df['TR'][0:period].mean()
    for i in range(period, len(df)):
        df.loc[start_idx + i, f'%ATR{period}'] = (df.iloc[i-1][f'%ATR{period}']*(period-1) + df.iloc[i]['TR'])/float(period)
        # atr[i] = (atr[i-1]*(period-1) + df.iloc[i]['TR'])/float(period)
    df.drop(columns=['A', 'B', 'C', 'TR'], inplace=True)
    # df[f'%ATR{period}'] = pd.Series(data=atr)
    # df[f'%ATR{period}'] = pd.Series(atr)
    # print(atr[-5:])
    # print(df[f'%ATR{period}'].tail())

    return df


def average_volume_diff(df, period_fast, period_slow):
    volume1 = df['Volume'].rolling(period_fast).mean()
    volume2 = df['Volume'].rolling(period_slow).mean()
    df['VolDiff'] = ((volume1 - volume2)/volume2)*100.0
    return df


def zlsma(df, period):

    df['lsma1'] = rolling_ols(df, 'Close', period)
    df['lsma2'] = rolling_ols(df, 'lsma1', period)
    df[f'zlsma{period}'] = 2*df['lsma1'] - df['lsma2']
    df.drop(columns=['lsma1', 'lsma2'])

    return df


def volume_weighted_average(df, src, period):
    start_index = df.index[0]
    volume_sum = df['Volume'].rolling(period).sum()
    print(volume_sum.iloc[period-1])
    df[f'{src}_VWA{period}'] = np.nan
    for i in range(period, len(df)):
        weighted_sum = 0
        for j in range(period):
            weighted_sum += df.iloc[i - period + j][src]*df.iloc[i-period+j]['Volume']/volume_sum.iloc[i-1]
        df.loc[start_index + i, f'{src}_VWA{period}'] = weighted_sum
    return df


def williams_r_all(df, period):
    """
    The Goals is to algorithmically understand where is the stock price action in relation to the limits (high & low)

    Options:
    1. ((Highest High - Close)/(Highest High - Lowest Low))*-100.0 # Default
    2. ((Close - Lowest Low)/(Highest High - Lowest Low))*100.0
    3. ((Highest High - Median)/(Highest High - Lowest Low))*-100.0
    4. ((Median - Lowest Low)/(Highest High - Lowest Low))*100.0
    5. ((Highest High - Low)/(Highest High - Lowest Low))*-100.0
    6. ((High - Lowest Low)/(Highest High - Lowest Low))*100.0
    """
    highest_high = df['High'].rolling(period).max()
    lowest_low = df['Low'].rolling(period).min()
    median = (df['High'] + df['Low'])/2
    df[f'Williams_R%_High_{period}'] = ((highest_high - df['High'])/(highest_high - lowest_low))*-100.0
    df[f'Williams_R%_Close_{period}'] = ((highest_high - df['Close'])/(highest_high - lowest_low))*-100.0
    df[f'Williams_R%_Median_{period}'] = ((highest_high - median) / (
                highest_high - lowest_low)) * -100.0
    df[f'Williams_R%_Open_{period}'] = ((highest_high - df['Open']) / (
                highest_high - lowest_low)) * -100.0
    df[f'Williams_R%_Low_{period}'] = ((highest_high - df['Low']) / (highest_high - lowest_low)) * -100.0
    return df


def williams_r_all_v1(df, period):
    """
    The Goals is to algorithmically understand where is the stock price action in relation to the limits (high & low)

    Options:
    1. ((Highest High - Close)/(Highest High - Lowest Low))*-100.0 # Default
    2. ((Close - Lowest Low)/(Highest High - Lowest Low))*100.0
    3. ((Highest High - Median)/(Highest High - Lowest Low))*-100.0
    4. ((Median - Lowest Low)/(Highest High - Lowest Low))*100.0
    5. ((Highest High - Low)/(Highest High - Lowest Low))*-100.0
    6. ((High - Lowest Low)/(Highest High - Lowest Low))*100.0
    """
    highest_high = df['High'].rolling(period).max()
    lowest_low = df['Low'].rolling(period).min()
    median = (df['High'] + df['Low'])/2
    df[f'Williams_R%_High_{period}'] = ((highest_high - df['High'])/(highest_high - lowest_low))*-100.0
    df[f'Williams_R%_Close_{period}'] = ((highest_high - df['Close'])/(highest_high - lowest_low))*-100.0
    df[f'Williams_R%_Median_{period}'] = ((highest_high - median) / (
                highest_high - lowest_low)) * -100.0
    df[f'Williams_R%_Open_{period}'] = ((highest_high - df['Open']) / (
                highest_high - lowest_low)) * -100.0
    df[f'Williams_R%_Low_{period}'] = ((highest_high - df['Low']) / (highest_high - lowest_low)) * -100.0
    return df


def range_moving_average(df, period):
    start_idx = df.index[0]
    df[f'RMA{period}'] = np.nan
    for row in range(period, len(df)):
        prices = []
        for i in range(period):
            high = df.iloc[row-i]['High']
            low = df.iloc[row-i]['Low']
            prices = prices + list(np.arange(low, high, .01))
        df.loc[start_idx + row, f'RMA{period}'] = np.mean(prices)
    return df


def mode_price(df, period, nbins):
    start_idx = df.index[0]
    df[f'MODE{period}'] = np.nan

    for i in range(period, len(df)):
        sample_df = df[i-period:i].copy()
        prices = []

        for row in range(len(sample_df)):
            high = sample_df.iloc[row]['High']
            low = sample_df.iloc[row]['Low']
            prices = prices + list(np.arange(low, high, .01))

        prices = sorted(prices)

        # histogram
        bins = np.linspace(np.ceil(min(prices)),
                           np.floor(max(prices)),
                           nbins)

        occurrences, price_ranges = np.histogram(prices, bins)
        histogram_dict = {}

        for j in range(len(occurrences)):
            histogram_dict[occurrences[j]] = (round(price_ranges[j], 2), round(price_ranges[j + 1], 2))

        df.loc[start_idx + i, f'MODE{period}'] = np.mean(histogram_dict[max(occurrences)])

    return df


def geometric_mean(df, period):

    start_idx = df.index[0]
    df[f'GMEAN{period}'] = np.nan

    for i in range(period, len(df)):
        price_list = df[i-period:i]['Close'].tolist()
        df.loc[start_idx + i, f'GMEAN{period}'] = gmean(price_list)

    return df


def harmonic_mean(df, period):

    start_idx = df.index[0]
    df[f'HMEAN{period}'] = np.nan

    for i in range(period, len(df)):
        price_list = df[i-period:i]['Close'].tolist()
        df.loc[start_idx + i, f'HMEAN{period}'] = hmean(price_list)

    return df


def stdev_bands(df, period, stdevs=1):

    start_idx = df.index[0]
    df[f'{stdevs}+SMA{period}'] = np.nan
    df[f'{stdevs}-SMA{period}'] = np.nan

    for i in range(period, len(df)):
        sample_df = df[i - period:i].copy()
        prices = []

        for row in range(len(sample_df)):
            high = sample_df.iloc[row]['High']
            low = sample_df.iloc[row]['Low']
            prices = prices + list(np.arange(low, high, .01))

        mean = np.mean(prices)
        std = np.std(prices)
        top = mean + std*stdevs
        bottom = mean - std*stdevs
        df.loc[start_idx + i, f'{stdevs}+SMA{period}'] = top
        df.loc[start_idx + i, f'{stdevs}-SMA{period}'] = bottom

    return df


def prices_skewness(df, period):
    start_idx = df.index[0]
    df[f'Sk{period}'] = np.nan

    for i in range(period, len(df)):
        sample_df = df[i - period:i].copy()
        prices = []

        for row in range(len(sample_df)):
            high = sample_df.iloc[row]['High']
            low = sample_df.iloc[row]['Low']
            prices = prices + list(np.arange(low, high, .01))

        df.loc[start_idx + i, f'Sk{period}'] = skew(prices)

    return df


def prices_kurtosis(df, period):
    start_idx = df.index[0]
    df[f'K{period}'] = np.nan

    for i in range(period, len(df)):
        sample_df = df[i - period:i].copy()
        prices = []

        for row in range(len(sample_df)):
            high = sample_df.iloc[row]['High']
            low = sample_df.iloc[row]['Low']
            prices = prices + list(np.arange(low, high, .01))

        df.loc[start_idx + i, f'K{period}'] = kurtosis(prices)

    return df


def rolling_baseline(df, src, period):
    start_idx = df.index[0]
    df[f'baseline{period}'] = np.nan

    for i in range(period, len(df), period):
        sample_df = df[i-period: i].copy()
        current_baseline = baseline(sample_df[src])
        for j in range(period):
            df.loc[start_idx + i + j, f'baseline{period}'] = current_baseline[j]

    return df


def volume_profile(df, idx, period, percentile=5):
    sample_df = df[idx-period:idx].copy()
    volume_profile_dict = {}
    close_prices = sample_df['Close'].tolist()
    volume = sample_df['Volume'].tolist()
    close_ranges = []
    close_list = [x for x in close_prices if (x > 0) and (x <= np.percentile(close_prices, percentile))]
    if len(close_list) > 0:
        close_ranges.append(close_list)
    total_volume_list = []
    for i in range(percentile, 100, percentile):
        close_list = [x for x in close_prices if (x > np.percentile(close_prices, i)) and (x <= np.percentile(close_prices, i+percentile))]
        if len(close_list) > 0:
            close_ranges.append(close_list)
    for close_range in close_ranges:
        total_volume = 0
        for close in close_range:
            total_volume += volume[close_prices.index(close)]
        total_volume_list.append(total_volume)
        volume_profile_dict[total_volume] = close_range
    total_volume_list = sorted(total_volume_list, reverse=True)
    volume_profile_dict_sorted = {}
    for total_volume in total_volume_list:
        # TODO: remove print
        if len(volume_profile_dict[total_volume]) == 0:
            print('empty volume')
        volume_profile_dict_sorted[f'{total_volume/1000000}M'] = (np.mean(volume_profile_dict[total_volume]), volume_profile_dict[total_volume])

    return volume_profile_dict_sorted


def volume_profile_pct(df, idx, period, percentile=5):

    volume_dict = volume_profile(df, idx, period, percentile)
    current_close = df.iloc[idx]['Close']
    volume_list_sorted_by_closeness_to_price = []
    for key in volume_dict.keys():
        mean_price = volume_dict[key][0]
        pct = (mean_price/current_close - 1)*100
        pct_abs = abs(pct)
        volume_list_sorted_by_closeness_to_price.append((pct_abs, pct, mean_price))
    volume_list_sorted_by_closeness_to_price.sort(key=lambda tup: tup[0])
    final_volume_list = [x[1] for x in volume_list_sorted_by_closeness_to_price]
    if len(final_volume_list) > 3:
        return idx, final_volume_list[:3]
    return idx, final_volume_list


def my_rsi(df, window):

    df['candle_change'] = (df['Close'] / df.shift(1)['Close'] - 1) * 100.0
    df['positive_candle_change'] = np.where(df['candle_change'] > 0, df['candle_change'], np.nan)
    df['negative_candle_change'] = np.where(df['candle_change'] < 0, df['candle_change'], np.nan)
    df[f'myRSI{window}'] = np.nan
    start_idx = df.index[0]
    for i in range(window, len(df)):
        sample_df = df[i - window:i].copy()
        positive_sample = sample_df.loc[sample_df['candle_change'] > 0]
        negative_sample = sample_df.loc[sample_df['candle_change'] < 0]
        bullish = (positive_sample['candle_change'] * positive_sample['Volume']).sum()
        bearish = (negative_sample['candle_change'].abs() * negative_sample['Volume']).sum()
        df.loc[start_idx + i, f'myRSI{window}'] = bullish * 100.0 / (bullish + bearish)

    df.drop(columns=['negative_candle_change', 'positive_candle_change', 'candle_change'], inplace=True)

    return df


if __name__=="__main__":
    from utils.get_all_stocks import get_all_nasdaq_100_stocks, get_all_nyse_composite_stocks, in_sample_tickers
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    from machine_learning_stuff.linear_regression import rolling_ols
    from plotting.candlestick_chart import multiple_windows_chart, add_markers_to_candlestick_chart
    from trade_managers._signal_trading_manager import signal_trading_manager_long, signal_trading_manager_short
    import pandas as pd
    import numpy as np
    import yfinance as yf
    import json
    import random
    import time
    from datetime import datetime
    import concurrent.futures
    from itertools import repeat

    # start = time.time()
    #
    # tickers = in_sample_tickers()
    # ticker = 'SPY'
    # # all_trades = []
    # # for ticker in tickers:

    #
    # # Adding the dataframe the percentage from the volume, sorted by distance from closing price
    # period = 200
    #
    # idxs = list(range(period, len(df)))
    # start_idx = df.index[0]
    # df['volume0_pct'] = np.nan
    # df['volume1_pct'] = np.nan
    # df['volume2_pct'] = np.nan
    #
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     results = executor.map(volume_profile_pct,
    #                            repeat(df),
    #                            idxs,
    #                            repeat(period))
    #
    #     for result in results:
    #         idx = result[0]
    #         volumes = result[1]
    #         df.loc[start_idx + idx, 'volume0_pct'] = volumes[0]
    #         df.loc[start_idx + idx, 'volume1_pct'] = volumes[1]
    #         df.loc[start_idx + idx, 'volume2_pct'] = volumes[2]
    #
    # df.to_csv(save_under_results_path(f'{ticker}_volumes.csv'))

    # df = pd.read_csv(r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\SPY_volumes.csv")
    ticker = 'VTI'
    # df['avg_volume_pct'] = (df['volume0_pct'] + df['volume1_pct'] + df['volume2_pct'])/3
    # df['sma_volume_fast'] = df['avg_volume_pct'].rolling(10).mean()
    # df['sma_volume_slow'] = df['avg_volume_pct'].rolling(30).mean()

    df = pd.read_csv(download_stock_day(ticker)).reset_index()
    # stochastic_period = 14
    # stochastic_fast = 5
    # stochastic_slow = 20
    # high = df['High'].rolling(stochastic_period).max()
    # low = df['Low'].rolling(stochastic_period).min()
    # df['%K'] = ((df['Close'] - low) / (high - low)) * 100.0
    # df['%DF'] = df['%K'].rolling(stochastic_fast).mean()
    # df['%DS'] = df['%K'].rolling(stochastic_slow).mean()

    # chart_dict = {(2, 'Volume %'): ['volume0_pct',
    #                                     'volume1_pct',
    #                                     'volume2_pct',
    #                                     'avg_volume_pct',
    #                                     'sma_volume_fast',
    #                                     'sma_volume_slow'],
    #               (3, 'Stochastic'): ['%K', '%DF', '%DS']}
    #
    # fig = multiple_windows_chart(ticker, df, chart_dict)
    # fig.show()

    # Volume signals
    # df['buy_signal'] = np.where(df['sma_volume_fast'] < df['sma_volume_slow'], True, False)
    # df['sell_signal'] = np.where((df['sma_volume_fast'] > df['sma_volume_slow']), True, False)

    # Stochastic Signals
    # df['buy_signal'] = np.where(df['%DS'] < df['%DF'], True, False)
    # df['sell_signal'] = np.where(df['%DS'] > df['%DF'], True, False)

    # Volume & Stochastic
    # df['buy_signal'] = np.where((df['sma_volume_fast'] < df['sma_volume_slow']) &
    #                             (df['%DS'] < df['%DF']), True, False)
    # df['sell_signal'] = np.where((df['sma_volume_fast'] > df['sma_volume_slow']) &
    #                              (df['%DS'] > df['%DF']), True, False)

    # SPY Stochastic
    df['Datetime'] = pd.to_datetime(df['Date'])
    df['52max'] = df['High'].rolling(252).max()
    df['52min'] = df['Low'].rolling(252).min()
    # df['change%'] = (df['Close']/df.shift(1)['Close'] - 1)*100
    # df['avg_change%'] = df['change%'].rolling(10).mean()
    df['buy_signal'] = np.where(df['Close'] > df['52min']*1.3, True, False)
    df['sell_signal'] = np.where(df['Close'] < df['52max']*0.8, True, False)
    trades, final_cap = signal_trading_manager_long(ticker, df)

    first_trade_price = trades[0]['enter_price']
    last_trade_price = trades[-1]['exit_price']
    print('buy & hold:', (last_trade_price/first_trade_price - 1))

    # pd.DataFrame(all_trades).to_csv(save_under_results_path('volume_profile_trading_all_trades.csv'))
