import pandas as pd
import numpy as np
from utils.download_stock_csvs import download_stock_day
from utils.in_sample_tickers import *
from plotting.candlestick_chart import multiple_windows_chart, add_markers_to_candlestick_chart
from scipy.integrate import simpson

ticker = 'BA'
df = pd.read_csv(download_stock_day(ticker))

window = 10

# df['candle_change'] = (df['Close']/df['Open'] - 1)*100.0
df['candle_change'] = (df['Close']/df.shift(1)['Close'] - 1)*100.0
df['positive_candle_change'] = np.where(df['candle_change'] > 0, df['candle_change'], np.nan)
df['negative_candle_change'] = np.where(df['candle_change'] < 0, df['candle_change'], np.nan)
df['bullish_bearish_oscillator'] = np.nan
df['50%'] = 50.0
start_idx = df.index[0]
for i in range(window, len(df)):
    sample_df = df[i-window:i].copy()
    positive_sample = sample_df.loc[sample_df['candle_change'] > 0]
    negative_sample = sample_df.loc[sample_df['candle_change'] < 0]
    bullish = (positive_sample['candle_change']*positive_sample['Volume']).sum()
    bearish = (negative_sample['candle_change'].abs()*negative_sample['Volume']).sum()
    df.loc[start_idx+i, 'bullish_bearish_oscillator'] = bullish*100.0/(bullish+bearish)

avg_fast = 5
avg_slow = 20
df[f'{avg_fast}_avg_oscillator'] = df['bullish_bearish_oscillator'].rolling(avg_fast).mean()
df[f'{avg_slow}_avg_oscillator'] = df['bullish_bearish_oscillator'].rolling(avg_slow).mean()

# Rolling area under curve
area_window = 50
df['area'] = np.nan
for i in range(area_window, len(df)):
    sample_df = df[i-area_window:i].copy()
    above_50_array = sample_df.loc[sample_df['bullish_bearish_oscillator'] >= 50]['bullish_bearish_oscillator'].to_numpy()
    below_50_array = sample_df.loc[sample_df['bullish_bearish_oscillator'] < 50]['bullish_bearish_oscillator'].to_numpy()
    if (len(above_50_array) + len(below_50_array)) != 50:
        continue
    below_50_array = 100 - below_50_array
    if len(above_50_array) > 1:
        above_area = simpson(above_50_array, dx=len(above_50_array))
    else:
        above_area = 0
    if len(below_50_array) > 1:
        below_area = simpson(below_50_array, dx=len(below_50_array))
    else:
        below_area = 0
    df.loc[start_idx+i, 'area'] = above_area*100/(below_area+above_area)

# Rate of change
roc_window = 20
df['osc_roc'] = (df['bullish_bearish_oscillator'] - df.shift(roc_window)['bullish_bearish_oscillator'])


fig = multiple_windows_chart(ticker, df, {(2, 'Bullish Bearish Oscillator'): ['bullish_bearish_oscillator',
                                                                              '50%',
                                                                              f'{avg_fast}_avg_oscillator',
                                                                              f'{avg_slow}_avg_oscillator'],
                                          (3, 'Oscillator Area'): ['area', '50%'],
                                          (4, 'Oscillator Rate of Change'): ['osc_roc']})
fig.show()
