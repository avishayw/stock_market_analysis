import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def rolling_ols(df, src, period):

    df['datetime'] = pd.to_datetime(df['Date'])
    df['epoch'] = df['datetime'].apply(lambda x: x.timestamp())
    df['linreg'] = np.nan

    df.reset_index(inplace=True)

    for i in range(period, len(df)):
        sample_df = pd.DataFrame.copy(df[i-period:i])
        x = sample_df['epoch'].to_numpy().reshape(-1, 1)
        y = sample_df[src].to_numpy()
        model = LinearRegression()
        try:
            model.fit(x, y)
        except ValueError:
            continue
        df.loc[i, 'linreg'] = model.predict(np.array(df.iloc[i]['epoch']).reshape(-1, 1))

    linreg = pd.DataFrame.copy(df['linreg'])
    df.drop(columns=['datetime', 'epoch', 'linreg'], inplace=True)

    return linreg


def rolling_ols_envelope(df, period, inplace=True):

    df['datetime'] = pd.to_datetime(df['Date'])
    df['epoch'] = df['datetime'].apply(lambda x: x.timestamp())
    df[f'linreg_high_{period}'] = np.nan
    df[f'linreg_low_{period}'] = np.nan

    df.reset_index(inplace=True)

    for i in range(period, len(df)):
        sample_df = pd.DataFrame.copy(df[i - period:i])
        x = sample_df['epoch'].to_numpy().reshape(-1, 1)
        y_high = sample_df['High'].to_numpy()
        y_low = sample_df['Low'].to_numpy()
        model_high = LinearRegression()
        model_low = LinearRegression()
        try:
            model_high.fit(x, y_high)
            model_low.fit(x, y_low)
        except ValueError:
            continue
        df.loc[i, f'linreg_high_{period}'] = model_high.predict(np.array(df.iloc[i]['epoch']).reshape(-1, 1))
        df.loc[i, f'linreg_low_{period}'] = model_low.predict(np.array(df.iloc[i]['epoch']).reshape(-1, 1))

    if inplace:
        df.drop(columns=['datetime', 'epoch'], inplace=True)
        return df
    else:
        linreg_high = pd.DataFrame.copy(df[f'linreg_high_{period}'])
        linreg_low = pd.DataFrame.copy(df[f'linreg_low_{period}'])
        return linreg_high, linreg_low


if __name__=="__main__":
    import datetime
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart

    ticker = 'PYPL'

    df = pd.read_csv(download_stock_day(ticker))[-2016:]

    ols_period = 200
    df = rolling_ols_envelope(df, ols_period, inplace=True)

    fig = candlestick_chart_fig(df, ticker)
    fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'linreg_high_{ols_period}'], f'linreg_high_{ols_period}')
    fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'linreg_low_{ols_period}'], f'linreg_low_{ols_period}')

    fig.show()
