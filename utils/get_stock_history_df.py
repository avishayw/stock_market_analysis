import pandas as pd
import yfinance as yf


def get_stock_minute_max_history_df(ticker):
    """
    Get stock daily max history from Yahoo Finance

    :param ticker: str - Stock symbol in capital letters
    :return: pd.DataFrame - Stock daily history
    """
    stock = yf.Ticker(ticker)
    return stock.history(period="max", interval='1m')


def get_stock_daily_max_history_df(ticker):
    """
    Get stock daily max history from Yahoo Finance

    :param ticker: str - Stock symbol in capital letters
    :return: pd.DataFrame - Stock daily history
    """
    stock = yf.Ticker(ticker)
    return stock.history(period="max")


def get_stock_weekly_max_history_df(ticker):
    """
    Get stock weekly max history from Yahoo Finance

    :param ticker: str - Stock symbol in capital letters
    :return: pd.DataFrame - Stock weekly history
    """
    stock = yf.Ticker(ticker)
    return stock.history(period="max", interval="1wk")


def get_stock_monthly_max_history_df(ticker):
    """
    Get stock monthly max history from Yahoo Finance

    :param ticker: str - Stock symbol in capital letters
    :return: pd.DataFrame - Stock monthly history
    """
    stock = yf.Ticker(ticker)
    return stock.history(period="max", interval="1mo")


def get_stock_minute_history_of_day(ticker, date):
    """
    Get stock minute history of specified day from Yahoo Finance

    :param ticker: str - Stock symbol in capital letters
    :param date: str - format: %Y-%m-%d
    :return: pd.DataFrame - Stock minute history
    """
    stock = yf.Ticker(ticker)
    return stock.history(period="1d", interval="1m", end=date)


if __name__=="__main__":
    import yfinance as yf
    import pandas as pd
    from utils.paths import save_under_results_path
    from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart
    from machine_learning_stuff.linear_regression import rolling_ols
    from indicators.trend_indicators import exponential_moving_average
    from indicators.momentum_indicators import simple_moving_average

    ticker = '^VIX'
    df = yf.Ticker(ticker).history(period='max')[-4032:]
    print(df.tail())
    df.reset_index(inplace=True)
    df['linreg10'] = rolling_ols(df, 'Close', 10)
    df['linreg50'] = rolling_ols(df, 'Close', 50)
    df = exponential_moving_average(df, 'Close', 10)
    df = exponential_moving_average(df, 'Close', 20)
    df = exponential_moving_average(df, 'Close', 50)
    df = simple_moving_average(df, 20)
    df = simple_moving_average(df, 50)

    fig = candlestick_chart_fig(df, ticker)
    fig = add_line_to_candlestick_chart(fig, df['Date'], df['linreg10'], 'linreg10')
    fig = add_line_to_candlestick_chart(fig, df['Date'], df['linreg50'], 'linreg50')
    fig = add_line_to_candlestick_chart(fig, df['Date'], df['Low'], 'Low')
    fig = add_line_to_candlestick_chart(fig, df['Date'], df['EMA10'], 'EMA10')
    fig = add_line_to_candlestick_chart(fig, df['Date'], df['EMA20'], 'EMA20')
    fig = add_line_to_candlestick_chart(fig, df['Date'], df['EMA50'], 'EMA50')
    fig = add_line_to_candlestick_chart(fig, df['Date'], df['SMA20'], 'SMA20')
    fig = add_line_to_candlestick_chart(fig, df['Date'], df['SMA50'], 'SMA50')
    fig.show()

