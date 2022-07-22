import pandas as pd
import yfinance as yf


def get_stock_daily_max_history_df(ticker):
    """
    Get stock daily max history from Yahoo Finance

    :param ticker: str - Stock symbol in capital letters
    :return: pd.DataFrame - Stock daily history
    """
    stock = yf.Ticker(ticker)
    return stock.history(period="max")


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
    ticker = 'AAPL'
    df = get_stock_minute_history_of_day(ticker,'2022-06-23')
    print(df)

