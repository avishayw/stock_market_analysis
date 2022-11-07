from utils.download_stock_csvs import download_stock_day
from utils.get_all_stocks import get_all_snp_stocks
from utils.paths import save_under_results_path
import pandas as pd
from datetime import datetime


tickers = get_all_snp_stocks()
tickers_stats = []

for ticker in tickers:
    try:
        df = pd.read_csv(download_stock_day(ticker)).reset_index()
    except ValueError:
        continue

    if len(df) < 5*252 +1:
        continue

    df['Date'] = df['Date'].map(lambda x: str(x).split(' ')[0])
    df['Datetime'] = pd.to_datetime(df['Date'])
    last_close = df.iloc[-1]['Close']

    stats = {'Ticker': ticker, 'All-Time High': (last_close / (df['High'].max()) - 1) * 100.0,
             'All-Time Low': (last_close / (df['Low'].min()) - 1) * 100.0,
             '5 Years High': (last_close / (df['High'].rolling(5 * 252).max().iloc[-1]) - 1) * 100.0,
             '5 Years Low': (last_close / (df['Low'].rolling(5 * 252).min().iloc[-1]) - 1) * 100.0,
             '52 Weeks High': (last_close / (df['High'].rolling(252).max().iloc[-1]) - 1) * 100.0,
             '52 Weeks Low': (last_close / (df['Low'].rolling(252).min().iloc[-1]) - 1) * 100.0,
             'YTD High': (last_close / (
                 df.loc[df['Datetime'] >= datetime(datetime.now().year,1,1,0,0,0)]['High'].max()) - 1) * 100.0,
             'YTD Low': (last_close / (
                 df.loc[df['Datetime'] >= datetime(datetime.now().year, 1, 1, 0, 0, 0)]['Low'].min()) - 1) * 100.0}

    str_to_print = f'{ticker}: '
    for stat in stats.keys():
        str_to_print = str_to_print + f'|{stat}: {stats[stat]} '

    print(str_to_print)

    tickers_stats.append(stats)

pd.DataFrame(tickers_stats).to_csv(save_under_results_path("ticker_stats.csv"))
