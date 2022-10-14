import numpy as np
import math
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt


def fractal_candlestick_pattern(df):

    # determine bullish fractal
    def is_support(df,i):
        cond1 = df.iloc[i]['Low'] < df.iloc[i - 1]['Low']
        cond2 = df.iloc[i]['Low'] < df.iloc[i + 1]['Low']
        cond3 = df.iloc[i + 1]['Low'] < df.iloc[i + 2]['Low']
        cond4 = df.iloc[i - 1]['Low'] < df.iloc[i - 2]['Low']
        return cond1 and cond2 and cond3 and cond4

    # determine bearish fractal
    def is_resistance(df, i):
        cond1 = df.iloc[i]['High'] > df.iloc[i - 1]['High']
        cond2 = df.iloc[i]['High'] > df.iloc[i + 1]['High']
        cond3 = df.iloc[i + 1]['High'] > df.iloc[i + 2]['High']
        cond4 = df.iloc[i - 1]['High'] > df.iloc[i - 2]['High']
        return cond1 and cond2 and cond3 and cond4

    # to make sure the new level area does not exist already
    def is_far_from_level(value, levels, df):
        ave = np.mean(df['High'] - df['Low'])
        return np.sum([abs(value - level) < ave for _, level in levels]) == 0

    # a list to store resistance and support levels
    levels = []
    for i in range(2, df.shape[0] - 2):
        if is_support(df, i):
            low = df.iloc[i]['Low']
            if is_far_from_level(low, levels, df):
                levels.append((i, low))
        elif is_resistance(df, i):
            high = df.iloc[i]['High']
            if is_far_from_level(high, levels, df):
                levels.append((i, high))

    return levels


def plot_all(levels, df):
    fig, ax = plt.subplots(figsize=(16, 9))
    MOCHLV = zip(df.Date, df.Open, df.Close, df.High, df.Low, df.Volume)
    candlestick_ohlc(ax, MOCHLV, width=0.6, colorup='green',
                     colordown='red', alpha=0.8)
    date_format = mpl_dates.DateFormatter('%d %b %Y')
    ax.xaxis.set_major_formatter(date_format)
    for level in levels:
        plt.hlines(level[1], xmin=df['Date'][level[0]], xmax=
        max(df['Date']), colors='blue', linestyle='--')
    fig.show()


def resistance_level_v0(df):
    rolling_period = 3
    df['avg_high'] = df['High'].rolling(rolling_period).mean()
    df['avg_high'] = df.shift(-1)['avg_high']

    resistance_levels = []

    for i in range(2, len(df) - 2):
        if df.iloc[i - 2]['avg_high'] > df.iloc[i - 1]['avg_high']:
            continue
        elif df.iloc[i - 1]['avg_high'] > df.iloc[i]['avg_high']:
            continue
        elif df.iloc[i]['avg_high'] < df.iloc[i + 1]['avg_high']:
            continue
        elif df.iloc[i + 1]['avg_high'] < df.iloc[i + 2]['avg_high']:
            continue
        resistance_levels.append(df.iloc[i]['High'])

    resistance_levels = sorted(resistance_levels)

    resistance_levels_refine = []

    i = 0
    while i < len(resistance_levels) - 1:
        refined_resistance = 0
        same_level = True
        while same_level and i < len(resistance_levels) - 1:
            if resistance_levels[i + 1] * 0.97 < resistance_levels[i] < resistance_levels[i + 1] * 1.03:
                refined_resistance = (resistance_levels[i + 1] + resistance_levels[i]) / 2
                i += 1
            else:
                same_level = False
                if refined_resistance == 0:
                    resistance_levels_refine.append(resistance_levels[i])
                    i += 1
                else:
                    resistance_levels_refine.append(refined_resistance)
                    i += 2

    fig = candlestick_chart_fig(df)
    fig = add_line_to_candlestick_chart(fig, df['Date'], df['avg_high'], 'avg_high')

    for i, resistance in enumerate(resistance_levels_refine):
        df[f'resistance{i}'] = resistance
        fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'resistance{i}'], f'resistance{i}')

    fig.show()


if __name__ == "__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart
    import pandas as pd
    import numpy as np

    ticker = 'NVDA'

    df = pd.read_csv(download_stock_day(ticker))

    df = df[-1008:]

    plot_all(fractal_candlestick_pattern(df), df)
