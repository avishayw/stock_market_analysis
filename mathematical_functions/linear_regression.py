from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
import statsmodels.formula.api as smf
from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart
import pandas as pd
import numpy as np


def linreg_slope_intercept(X, Y, N):
    """
    X = The independent variable which is the Market
    Y = The dependent variable which is the Stock
    N = The length of the Window

    It returns the alphas and the betas of
    the rolling regression
    """

    # all the observations
    obs = len(X)

    # initiate the betas with null values
    betas = np.full(obs, np.nan)

    # initiate the alphas with null values
    alphas = np.full(obs, np.nan)

    for i in range((obs - N)):
        regressor = LinearRegression()
        regressor.fit(X.to_numpy()[i: i + N + 1].reshape(-1, 1), Y.to_numpy()[i: i + N + 1])

        betas[i + N] = regressor.coef_[0]
        alphas[i + N] = regressor.intercept_

    return (alphas, betas)


def linreg(df, src, period):
    df['Datetime'] = pd.to_datetime(df['Date'])
    df['time'] = df['Datetime'].apply(lambda x: x.value)
    intercepts, slopes = linreg_slope_intercept(df['time'], df['Close'], period)
    df['intercept'] = intercepts.tolist()
    df['slope'] = slopes.tolist()
    df['linreg'] = df['intercept'] + df['slope']*(df['time'])
    # df.drop(columns=['Datetime', 'time', 'intercept', 'slope'])
    return df


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import numpy as np


    ticker = 'AAPL'
    df = pd.read_csv(download_stock_day(ticker))
    df = df[-365:]
    df = linreg(df, 50)
    pd.set_option('display.max_columns', None)
    print(df.tail())
    # df.to_csv(save_under_results_path(f"{ticker}_linreg.csv"))

    fig = candlestick_chart_fig(df)
    fig = add_line_to_candlestick_chart(fig, df['Date'], df['linreg'])

    fig.show()