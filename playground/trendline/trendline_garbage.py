import numpy as np
from plotting.candlestick_chart import candlestick_chart_fig, add_markers_to_candlestick_chart, multiple_windows_chart


def z_score_local_extremas(df, window, z_score_th):  # not usable
    """
    Taking a rolling window, checking the average, standard deviation, and z score to decide which point are
    toughs or peaks.
    """
    df['mean_low'] = df['Low'].rolling(window).mean()
    df['mean_high'] = df['High'].rolling(window).mean()
    df['stdev_low'] = df['Low'].rolling(window).std()
    df['stdev_high'] = df['High'].rolling(window).std()
    df['z_score_low'] = (df['Low'] - df['mean_low']).abs()
    df['z_score_high'] = (df['High'] - df['mean_high']).abs()
    df['z_score_th'] = z_score_th
    df['tough'] = np.where((df['z_score_low'] >= z_score_th) &
                           (df['Low'] < df['mean_low']), df['Low']*0.995, np.nan)
    df['peak'] = np.where((df['z_score_high'] >= z_score_th) &
                           (df['High'] > df['mean_high']), df['Low']*0.995, np.nan)

    chart_dict = {(1,''): ['mean_low', 'mean_high'],
                  (2, 'Standard Deviation'): ['stdev_low', 'stdev_high'],
                  (3, 'Z score'): ['z_score_low', 'z_score_high', 'z_score_th']}
    fig = multiple_windows_chart('no_ticker', df, chart_dict)
    fig = add_markers_to_candlestick_chart(fig, df['Date'], df['tough'], 'toughs', 0)
    fig.show()