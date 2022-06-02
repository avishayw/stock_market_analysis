import pandas as pd

class Stock:

    def __init__(self, stock_csv, market_csv):
        self.df = pd.read_csv(stock_csv)
        self.market_df = pd.read_csv(stock_csv)

    