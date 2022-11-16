import pandas as pd
import numpy as np


def efficiency_ratio(df, src, period, inplace=True, threshold=None):

    net_change = (df[src] - df.shift(period)[src]).abs()
    change = (df[src] - df.shift(1)[src]).abs()
    sum_of_individual_changes = change.rolling(period).sum()
    er = net_change/sum_of_individual_changes
    if inplace:
        df[f'{src}ER{period}'] = er
        if threshold:
            er_th = np.where(er > threshold, True, False)
            df[f'{src}ER{period}>{threshold}'] = er_th
            return df
        return df
    else:
        if threshold:
            return pd.Series(np.where(er > threshold, True, False))
        else:
            return er


def price_density(df, period, inplace=True, threshold=None):
    highest_high = df['High'].rolling(period).max()
    lowest_low = df['Low'].rolling(period).min()
    box_range = highest_high - lowest_low
    day_range = df['High'] - df['Low']
    sum_of_individual_changes = day_range.rolling(period).sum()
    # my formula. Cuz if sum_of_individual_changes = box_range*n then the density will be 1, otherwise 0<density<1
    density = sum_of_individual_changes/(box_range*period)
    # density = sum_of_individual_changes/box_range  # TSaM formula
    if inplace:
        df[f'PriceDensity{period}'] = density
        if threshold:
            density_th = np.where(density > threshold, True, False)
            df[f'PriceDensity{period}>{threshold}'] = density_th
            return df
        return df
    else:
        if threshold:
            return pd.Series(np.where(density > threshold, True, False))
        else:
            return density


def fractal_dimension(df, period, inplace=True, threshold=None):
    dx2 = (1/period)**2
    highest_high = df['High'].rolling(period).max()
    lowest_low = df['Low'].rolling(period).min()
    box_range = highest_high - lowest_low


if __name__ == "__main__":
    from plotting.candlestick_chart import multiple_windows_chart
    from utils.download_stock_csvs import download_stock_day

    ticker = 'APH'
    df = pd.read_csv(download_stock_day(ticker)).reset_index()

    period = 14
    df['ER'] = efficiency_ratio(df, 'Close', period, inplace=False)
    df['PriceDensity'] = price_density(df, period, inplace=False)

    chart_dict = {(2, 'Efficiency Ratio (Close)'): ['ER'],
                  (3, 'Price Density'): ['PriceDensity']}

    fig = multiple_windows_chart(ticker, df, chart_dict)
    fig.show()
