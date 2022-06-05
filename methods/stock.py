import yfinance as yf


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
        return self.stock.history(period="1d", interval="1m", end=date).reset_index()
