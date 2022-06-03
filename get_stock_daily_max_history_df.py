import pandas as pd
import yfinance as yf


def get_stock_daily_max_history_df(ticker):
    """
    Get stock daily history from Yahoo Finance

    :param sticker: str - Stock symbol in capital letters
    :param start_date: str - Start date in format 'YYYY-MM-DD'
    :param end_date: str - End date in format 'YYYY-MM-DD'
    :return: pd.DataFrame - Stock daily history
    """
    stock = yf.Ticker(ticker)
    return stock.history(period="max")


if __name__=="__main__":
    ticker = 'FB'
    history = get_stock_daily_max_history_df(ticker)
    history.to_csv(f"{ticker}_max_daily_history.csv")

