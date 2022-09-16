import pandas as pd
from utils.download_stock_csvs import download_stock_day

# Dow Jones Industrial
dji_stocks = ['UNH', 'GS', 'HD', 'MSFT', 'MCD', 'AMGN', 'V', 'HON', 'CAT', 'CRM', 'JNJ', 'BA'
              , 'AAPL', 'TRV', 'AXP', 'CVX', 'PG', 'MMM', 'WMT', 'IBM', 'JPM', 'NKE', 'DIS', 'MRK'
              , 'KO', 'DOW', 'CSCO', 'VZ', 'INTC', 'WBA']



dji_dataframes = {}

for stock in dji_stocks:
    try:
        df = pd.read_csv(download_stock_day(stock))
    except ValueError:
        continue
    df = df[-100:]
    dji_dataframes[stock] = pd.DataFrame.copy(df[['Date', 'Volume']])



