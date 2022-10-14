import numpy as np
from indicators.momentum_indicators import rate_of_change, simple_moving_average
from indicators.trend_indicators import exponential_moving_average


def successive_trends_detector(df):
    df['median'] = (df['High'] - df['Low'])/2 + df['Low']
    df['up'] = np.where(df['median'] > df.shift(1)['median'], 1, 0)
    df = df[1:-1]
    df.reset_index(inplace=True)
    df['uptrend'] = np.zeros(len(df))
    df['uptrend_roc'] = np.nan
    df['downtrend'] = np.zeros(len(df))
    df['downtrend_roc'] = np.nan
    up_counter = 0
    down_counter = 0
    for i in range(len(df)):
        if df.iloc[i]['up'] == 1:
            down_counter = 0
            up_counter += 1
            df.loc[i, 'uptrend'] = up_counter
            df.loc[i, 'uptrend_roc'] = (df.iloc[i]['median'] - df.shift(up_counter).iloc[i]['median'])/df.shift(up_counter).iloc[i]['median']
        else:
            up_counter = 0
            down_counter += 1
            df.loc[i, 'downtrend'] = down_counter
            df.loc[i, 'downtrend_roc'] = (df.iloc[i]['median'] - df.shift(down_counter).iloc[i]['median'])/df.shift(down_counter).iloc[i]['median']
    df.drop(columns=['up'], inplace=True)

    return df


def primary_trend_detector(df):
    df = simple_moving_average(df,200)
    df = rate_of_change(df, 100)
    df['SMA_trend']


if __name__ == "__main__":
    from utils.get_all_stocks import get_all_nasdaq_100_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart
    from indicators.momentum_indicators import simple_moving_average
    from indicators.trend_indicators import exponential_moving_average
    import pandas as pd

    # tickers = get_all_nasdaq_100_stocks()

    ticker = 'AAPL'

    df = pd.read_csv(download_stock_day(ticker))
    df = df[-1008:]
    df = successive_trends_detector(df)
    df = simple_moving_average(df, 200)
    df = exponential_moving_average(df, 'median', 50)
    df = exponential_moving_average(df, 'median', 20)

    # df.to_csv(save_under_results_path(f'{ticker}_trends.csv'))

    fig = candlestick_chart_fig(df)

    # fig = add_line_to_candlestick_chart(fig, df['Date'], df['median'])
    # fig = add_line_to_candlestick_chart(fig, df['Date'], df['SMA200'])
    # fig = add_line_to_candlestick_chart(fig, df['Date'], df['EMA50'])
    # fig = add_line_to_candlestick_chart(fig, df['Date'], df['EMA20'])

    fig.show()
