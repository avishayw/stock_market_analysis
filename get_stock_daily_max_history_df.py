import pandas as pd
import yfinance as yf


def get_stock_daily_max_history_df(ticker):
    """
    Get stock daily max history from Yahoo Finance

    :param sticker: str - Stock symbol in capital letters
    :return: pd.DataFrame - Stock daily history
    """
    stock = yf.Ticker(ticker)
    return stock.history(period="max")


if __name__=="__main__":
    ticker = 'FB'
    history = get_stock_daily_max_history_df(ticker)
    history.to_csv(f"{ticker}_max_daily_history.csv")

