import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def rolling_ols(df, src, period):

    start_idx = df.index[0]
    df['datetime'] = pd.to_datetime(df['Date'])
    df['epoch'] = df['datetime'].apply(lambda x: x.timestamp())
    df['linreg'] = np.nan

    for i in range(period, len(df)):
        sample_df = pd.DataFrame.copy(df[i-period:i])
        x = sample_df['epoch'].to_numpy().reshape(-1, 1)
        y = sample_df[src].to_numpy()
        model = LinearRegression()
        try:
            model.fit(x, y)
        except ValueError:
            continue
        df.loc[start_idx + i, 'linreg'] = model.predict(np.array(df.iloc[i]['epoch']).reshape(-1, 1))

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


def backward_linear_regression(df, src, idx, period):
    """
    Function which will return the coefficient (slope) - which can be used to estimate the trend, and the score,
    which can be used to estimate the reliability of the coefficient
    """
    sample_df = df[idx-period:idx].copy()
    sample_df_datetime = pd.to_datetime(sample_df['Date'])
    sample_df_epoch = sample_df_datetime.apply(lambda x: x.timestamp())
    # epoch daily for coefficient convenience
    sample_df_epoch = sample_df_epoch
    x = sample_df_epoch.to_numpy().reshape(-1, 1)
    y = sample_df[src].to_numpy()
    model = LinearRegression()
    try:
        model.fit(x, y)
    except ValueError as e:
        print(e)
        return None
    y1 = model.predict([x[1]])[0]
    y0 = model.predict([x[0]])[0]
    roc = ((y1-y0)/y0)*100.0
    return roc, model.coef_, model.score(x, y), model


def rolling_backward_linear_regression(df, src, period):

    start_idx = df.index[0]
    df[f'coefficient{period}'] = np.nan
    df[f'score{period}'] = np.nan
    df[f'roc{period}'] = np.nan

    for i in range(period, len(df)):
        df.loc[start_idx + i, f'roc{period}'], \
        df.loc[start_idx + i, f'coefficient{period}'], \
        df.loc[start_idx + i, f'score{period}'] = backward_linear_regression(df, src, i,
                                                                                                          period)

    return df


def linear_regression_score_per_period(ticker, df, min_period=5, max_period=200, period_step=5):
    from utils.paths import save_under_results_path

    score_dict = {'period': [], 'score': [], 'coefficient': [], 'roc': [], 'linear_change': []}
    for period in range(min_period, max_period, period_step):
        roc, coefficient, score = backward_linear_regression(df, 'Close', len(df), period)
        score_dict['period'].append(period)
        score_dict['score'].append(score)
        score_dict['coefficient'].append(coefficient[0])
        score_dict['roc'].append(roc)
        score_dict['linear_change'].append((np.power(1+(roc/100.0), period)-1)*100.0)
    pd.DataFrame(score_dict).to_csv(save_under_results_path(f'{ticker}_score_df.csv'))


def detect_trend_using_linreg(df, score_th=0.6, overfit=0.95, initial_period=5):
    """
    Function which will find linear regressions with score > 0.7 for the whole df
    """
    start_idx = df.index[0]
    df_epoch = pd.to_datetime(df['Date']).apply(lambda x: x.timestamp())
    idx = len(df)
    previous_idx = idx-1
    while idx > initial_period and idx != previous_idx:
        previous_idx = idx
        print(idx)
        period = initial_period
        score = 0
        while period < idx and not (score_th < score < overfit):
            period += 1
            roc, coef, score, model = backward_linear_regression(df, 'Close', idx, period)
        if score >= score_th:
            df.loc[start_idx + idx - period, f'linreg_{score_th}<score<{overfit}'] = df.iloc[idx-period]['Close']
            for i in reversed(range(1,period)):
                df.loc[start_idx + idx - i, f'linreg_{score_th}<score<{overfit}'] = model.predict([[df_epoch.iloc[idx - i - 1]]])
            idx = idx - period

    return df


if __name__=="__main__":
    import datetime
    import pandas as pd
    import yfinance as yf
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    from utils.paths import save_under_results_path
    from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart

    # measuring market condition
    ticker = 'AMZN'

    df = pd.read_csv(download_stock_day(ticker))
    score_th = 0.65
    overfit = 0.75
    df = detect_trend_using_linreg(df, score_th=score_th, overfit=overfit)

    fig = candlestick_chart_fig(df, ticker)
    fig = add_line_to_candlestick_chart(fig, df['Date'], df[f'linreg_{score_th}<score<{overfit}'], f'linreg_{score_th}<score<{overfit}')
    fig.show()

