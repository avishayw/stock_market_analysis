"""
Upper band: open + (high[1] - low[1]) * .5
Lower band: open - (high[1] - low[1]) * .5

Results:

above_pct=1.001, below_pct=1.0, upperband_pct=0.99, lowerband_pct=1.01
final_high 0.11541345793314298
final_low 0.12019661007893788
"""
import pandas as pd
import numpy as np
from utils.download_stock_csvs import download_stock_day


def close_between_bands(df, above_pct=1.0, below_pct=1.0, upperband_pct=1.0, lowerband_pct=1.0):
    df['upperband'] = df['Open'] + (df.shift(1)['High'] - df.shift(1)['Low']) * 0.5
    df['lowerband'] = df['Open'] - (df.shift(1)['High'] - df.shift(1)['Low']) * 0.5
    df['high_above_upper_band'] = np.where((df['High'] > df['upperband']*below_pct) &
                                           (df['High'] < df['upperband']*above_pct), True, False)
    df['high_above_upper_band_and_close_between_bands'] = np.where(df['high_above_upper_band'] &
                                                             (df['Close'] < df['upperband'] * upperband_pct) &
                                                             (df['Close'] > df['lowerband'] * lowerband_pct), True, False)
    df['low_below_lower_band'] = np.where((df['Low'] < df['lowerband']*above_pct) &
                                          (df['Low'] > df['lowerband']*below_pct), True, False)
    df['low_below_lower_band_and_close_between_bands'] = np.where(df['low_below_lower_band'] &
                                                             (df['Close'] < df['upperband'] * upperband_pct) &
                                                             (df['Close'] > df['lowerband'] * lowerband_pct), True, False)

    high_above_upper_band = len(df.loc[df['high_above_upper_band']])
    high_above_upper_band_and_close_between_bands = len(df.loc[df['high_above_upper_band_and_close_between_bands']])
    low_below_lower_band = len(df.loc[df['low_below_lower_band']])
    low_below_lower_band_and_close_between_bands = len(df.loc[df['low_below_lower_band_and_close_between_bands']])

    return high_above_upper_band, high_above_upper_band_and_close_between_bands, low_below_lower_band, low_below_lower_band_and_close_between_bands


def run_function(ticker):

    df = pd.read_csv(download_stock_day(ticker))

    return close_between_bands(df, above_pct=1.001, below_pct=1.0, upperband_pct=0.99, lowerband_pct=1.01)


if __name__=='__main__':
    import concurrent.futures
    from utils.get_all_stocks import in_sample_tickers
    import time
    from utils.download_stock_csvs import download_stock_day

    t0 = time.time()

    tickers = in_sample_tickers()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(run_function, tickers)

        total_high_above_upper_band = 0
        total_high_above_upper_band_and_close_between_bands = 0
        total_low_below_lower_band = 0
        total_low_below_lower_band_and_close_between_bands = 0

        for result in results:
            total_high_above_upper_band += result[0]
            total_high_above_upper_band_and_close_between_bands += result[1]
            total_low_below_lower_band += result[2]
            total_low_below_lower_band_and_close_between_bands += result[3]
            if result[0] > 0:
                print('high', result[1] / result[0])
            if result[2] > 0:
                print('low', result[3] / result[2])

    print('final_high', total_high_above_upper_band_and_close_between_bands/total_high_above_upper_band)
    print('final_low', total_low_below_lower_band_and_close_between_bands/total_low_below_lower_band)

    print(time.time() - t0)