import yfinance as yf
from datetime import datetime, timedelta


class Stock:

    def __init__(self, ticker):
        self.stock = yf.Ticker(ticker)

    def max_daily_history(self):
        """
        :return: pandas.DataFrame
        """
        return self.stock.history(period="max").reset_index()

    def minute_history_of_date(self, date):
        """
        :param date: str YYYY-mm-dd
        :return: pandas.DataFrame
        """
        start = date
        end = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        return self.stock.history(period="1d", interval="1m", start=start, end=end).reset_index()


if __name__=="__main__":

    stock = Stock('AAPL')
    print(stock.minute_history_of_date('2014-06-01'))