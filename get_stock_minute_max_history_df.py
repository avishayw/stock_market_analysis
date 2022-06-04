import pandas as pd
import yfinance as yf
from datetime import datetime
from datetime import timedelta

def get_stock_minute_history_df(ticker):
    """
    Get stock 1990-Today minute history from Yahoo Finance

    :param sticker: str - Stock symbol in capital letters
    :return: pd.DataFrame - Stock daily history
    """
    end_date = datetime.today()
    end_date_str = end_date.strftime("%Y-%m-%d")

    stock = yf.Ticker(ticker)
    history = stock.history(period="7d", interval="1m", end=end_date_str).reset_index()

    while end_date > datetime(1990, 1, 1):
        end_date = end_date - timedelta(days=7)
        end_date_str = end_date.strftime("%Y-%m-%d")
        history = pd.concat([history, stock.history(period="7d", interval="1m", end=end_date_str).reset_index()], ignore_index=True)


    return history


if __name__=="__main__":
    ticker = 'FB'
    history = get_stock_minute_history_df(ticker)
    print(len(history))

