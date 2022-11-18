import pandas as pd
import json
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
from plotting.candlestick_chart import multiple_windows_chart
from datetime import datetime


def fractal_candlestick_pattern_method(df, levels=[]):

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
        # ave = np.mean(df['High'] - df['Low'])
        # ave = np.mean(df['High'] - df['Low'])/2
        ave = np.mean(df['High'] - df['Low']) * 2
        return np.sum([abs(value - level) < ave for _, level in levels]) == 0

    # a list to store resistance and support levels
    start_idx = df.index[0]
    for i in range(2, df.shape[0] - 2):
        if is_support(df, i):
            low = df.iloc[i]['Low']
            if is_far_from_level(low, levels, df):
                # levels.append((i, low))
                levels.append((start_idx + i, low))
        elif is_resistance(df, i):
            high = df.iloc[i]['High']
            if is_far_from_level(high, levels, df):
                # levels.append((i, high))
                levels.append((start_idx + i, high))

    return levels


def window_shifting_method(df, levels=[]):
    def is_far_from_level(value, levels, df):
        # ave = np.mean(df['High'] - df['Low'])
        # ave = np.mean(df['High'] - df['Low']) / 2
        ave = np.mean(df['High'] - df['Low']) * 2
        return np.sum([abs(value - level) < ave for _, level in levels]) == 0

    max_list = []
    min_list = []
    for i in range(5, len(df) - 5):
        # taking a window of 9 candles
        high_range = df['High'][i - 5:i + 4]
        current_max = high_range.max()
        # if we find a new maximum value, empty the max_list
        if current_max not in max_list:
            max_list = []
        max_list.append(current_max)
        # if the maximum value remains the same after shifting 5 times
        if len(max_list) == 5 and is_far_from_level(current_max, levels, df):
            levels.append((high_range.idxmax(), current_max))

        low_range = df['Low'][i - 5:i + 5]
        current_min = low_range.min()
        if current_min not in min_list:
            min_list = []
        min_list.append(current_min)
        if len(min_list) == 5 and is_far_from_level(current_min, levels, df):
            levels.append((low_range.idxmin(), current_min))

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


def resistance_level_v0_1(ticker, df, er_threshold=0.7):
    """
    In this function I will first reduce the 'High' prices noise using efficiency ratio.
    Then I will check for local maximums, i.e. day before price < candidate price > day after price.
    From there I need to figure out how to filter maximums which appear twice. My current thinking is to merge
    resistance points by given percentage, but that can cause rolling closeness. i.e. R1 is within 2% of R2, R2 is
    within 2% of R3, but R1 is not within 2% of R3, so where should I merge R2 to? mmm.. maybe to the closest within the
    threshold percentage range...
    """

    class EfficiencyCalculationError(Exception):
        pass

    class NoConditionError(Exception):
        pass

    def measure_er(sample_df, src='High'):
        net_change = abs(sample_df.iloc[-1][src] - sample_df.iloc[0][src])
        sum_of_individual_changes = ((sample_df[src] - sample_df.shift(1)[src]).abs()).sum()
        if sum_of_individual_changes == 0:
            if net_change == 0:
                return 1.0
            else:
                raise EfficiencyCalculationError(
                    "Efficiency ratio: Sum of individual changes is zero but the net change is not.")
        return net_change / sum_of_individual_changes

    def line(sample_df, source):
        y1 = sample_df.iloc[-1][source]
        y0 = sample_df.iloc[0][source]
        x0 = 0
        x1 = len(sample_df) - 1
        if x1 - x0 == 0:
            return None
        m = (y1 - y0) / (x1 - x0)
        c = y1 - m * x1
        return m, c

    df_start_idx = df.index[0]
    i = 2
    movement_id = 0
    current_idx = 0
    max_movement_period = 10
    source = 'High'
    while i < len(df):
        sample_df = df[current_idx:i].copy()
        er = measure_er(sample_df, source)
        if er >= er_threshold:
            movement_er = er
            i += 1
        elif er < er_threshold:
            slope, intercept = line(df[current_idx:i-1].copy(), source)
            for j in range(current_idx, i - 1):
                df.loc[df_start_idx + j, 'movement_id'] = movement_id
                df.loc[df_start_idx + j, 'movement_er'] = movement_er
                df.loc[df_start_idx + j, 'movement_price'] = slope*(j - current_idx) + intercept
            current_idx = i - 1
            movement_id += 1
            i = current_idx + 2
        elif i - current_idx >= max_movement_period:
            current_idx += 1
            i = current_idx + 1
        else:
            raise NoConditionError("None of the conditions met")

    df['Date'] = df['Date'].map(lambda x: str(x).split(' ')[0])
    resistance_prices_dict = {'Date': [], 'Price': []}
    resistance_prices_counter = 0
    i = 1
    while i < len(df):
        if df.shift(1).iloc[i]['movement_price'] < df.iloc[i]['movement_price'] > df.shift(-1).iloc[i]['movement_price']:
            resistance_prices_dict['Date'].append(datetime.strptime(df.iloc[i]['Date'], '%Y-%m-%d'))
            resistance_prices_dict['Price'].append(df.iloc[i]['movement_price'])
            # df[f'R{resistance_prices_counter}'] = df.iloc[i]['movement_price']
            # resistance_prices_counter += 1
        i += 1

    resistance_prices_ranges = {}
    ranges_counter = 0
    resistance_prices = zip(resistance_prices_dict['Date'], resistance_prices_dict['Price'])
    # Sorting by price
    resistance_prices = sorted(resistance_prices, key=lambda tup: tup[1])

    i = 0
    pct_th = 2
    safety_pct = 0.5
    while i < len(resistance_prices)-1:
        in_range = True
        resistance_range = [resistance_prices[i]]
        while in_range and i < len(resistance_prices)-1:
            if resistance_prices[i][1]*(1-pct_th/100.0) <= resistance_prices[i+1][1] < resistance_prices[i][1]*(1+pct_th/100.0):
                resistance_range.append(resistance_prices[i+1])
                i += 1
            else:
                range_min = resistance_range[0][1] * (1-safety_pct/100.0)
                range_max = resistance_range[-1][1] * (1+safety_pct/100.0)
                # Sorting by date
                resistance_range = sorted(resistance_range, key=lambda tup: tup[0])
                range_date_start = resistance_range[0][0].strftime('%Y-%m-%d')
                range_date_end = resistance_range[-1][0].strftime('%Y-%m-%d')
                prices = [tup[1] for tup in resistance_range]
                resistance_prices_ranges[ranges_counter] = {'range_min': range_min,
                                                            'range_max': range_max,
                                                            'range_pct': (range_max/range_min - 1)*100.0,
                                                            'range_date_start': range_date_start,
                                                            'range_date_end': range_date_end,
                                                            'prices': prices}
                in_range = False
                ranges_counter += 1
                i += 1

    # Saving the resistance ranges to csv file
    with open(f'{ticker}_resistance_ranges.json', 'w') as f:
        json.dump(resistance_prices_ranges, f, indent=4)

    # Saving all the resistance found to csv file
    resistance_df = pd.DataFrame(resistance_prices_dict)
    resistance_df.to_csv(f'{ticker}_resistance_prices_v0_1_er_th_{str(er_threshold).replace(".", "_")}.csv')

    # Adding to figure the average of each resistance range
    # for i, price_range in enumerate(resistance_prices_ranges.values()):
    #     average_resistance = (price_range['range_min'] + price_range['range_max'])/2
    #     df[f'R{i}'] = average_resistance

    # chart_dict = {(1, ''): ['movement_price'] + [f'R{r}' for r in range(len(resistance_prices_ranges))]}
    # fig = multiple_windows_chart(ticker, df, chart_dict)
    # fig.show()


if __name__ == "__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart, multiple_windows_chart
    import pandas as pd
    import numpy as np

    def plot_support_resistance(df, levels, safety_margin=None):
        chart_dict = {(1, ''): []}
        if safety_margin is None:
            for level_tup in levels:
                idx = level_tup[0]
                level = level_tup[1]
                df.loc[idx:df.index[-1], f'R_S_{idx}'] = level
                chart_dict[(1, '')].append(f'R_S_{idx}')
        else:
            for level_tup in levels:
                idx = level_tup[0]
                level = level_tup[1]
                df.loc[idx:df.index[-1], f'R_S_{idx}'] = level
                df.loc[idx:df.index[-1], f'R_S_{idx}+'] = level*(1+safety_margin/100)
                df.loc[idx:df.index[-1], f'R_S_{idx}-'] = level * (1 - safety_margin / 100)
                chart_dict[(1, '')] = chart_dict[(1, '')] + [f'R_S_{idx}', f'R_S_{idx}+', f'R_S_{idx}-']

        # chart_dict = {(1, ''): [f'R_S_{i}' for i in range(len(support_resistance_levels))]}
        fig = multiple_windows_chart(ticker, df, chart_dict)
        fig.show()

    ticker = 'NVDA'

    df = pd.read_csv(download_stock_day(ticker))

    df = df[-1008:]
    start_idx = df.index[0]
    final_idx = df.index[-1]
    support_resistance_levels_1 = fractal_candlestick_pattern_method(df)
    support_resistance_levels_2 = window_shifting_method(df, levels=support_resistance_levels_1)
    # support_resistance_levels_2 = window_shifting_method(df)
    # support_resistance_levels_1 = fractal_candlestick_pattern_method(df, levels=support_resistance_levels_2)

    print(len(support_resistance_levels_1), support_resistance_levels_1)
    print(len(support_resistance_levels_2), support_resistance_levels_2)
    # support_resistance_levels = list(set(support_resistance_levels_1 + support_resistance_levels_2))
    # print(len(support_resistance_levels), support_resistance_levels)
    # plot_support_resistance(df, support_resistance_levels_1)
    plot_support_resistance(df, support_resistance_levels_2, safety_margin=1.0)
    # plot_support_resistance(df, support_resistance_levels)
    # for i, level_tup in enumerate(support_resistance_levels):
    #     idx = level_tup[0]
    #     level = level_tup[1]
    #     df.loc[start_idx+idx:final_idx, f'R_S_{i}'] = level
    #
    # chart_dict = {(1, ''): [f'R_S_{i}' for i in range(len(support_resistance_levels))]}
    # fig = multiple_windows_chart(ticker, df, chart_dict)
    # fig.show()

    # levels = np.array([tup[1] for tup in support_resistance_levels])
    # last_price = df.iloc[-1]['Close']
    # print(last_price)
    # print(levels)
    # difference_list = np.array(levels) - last_price
    # print(difference_list)
    # closest_resistance = levels[np.where(difference_list == np.min(difference_list[np.where(difference_list > 0)]))][0]
    # closest_support = levels[np.where(difference_list == np.max(difference_list[np.where(difference_list < 0)]))][0]
    # print(closest_resistance, closest_support)
