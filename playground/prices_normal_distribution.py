from scipy.stats import normaltest
import yfinance as yf
import pandas as pd
from utils.paths import save_under_results_path
import time

ticker = 'AAPL'
period = 252
df = yf.Ticker(ticker).history(period='max', interval='1d')

if 'Date' not in df.columns.tolist():
    df.reset_index(inplace=True)

alpha = 1e-3
prices_list = {'Date': [], 'k2': [], 'p': [], '<alpha': []}

for i in range(period, len(df)):
    start = time.time()
    k2, p = normaltest(df[i-period: i]['Close'].tolist())
    print(f'{i}: {time.time() - start}')
    prices_list['Date'].append(df.iloc[i]['Date'])
    prices_list['k2'].append(k2)
    prices_list['p'].append(p)
    prices_list['<alpha'].append(p < alpha)

pd.DataFrame(prices_list).to_csv(save_under_results_path(f'{ticker}_normal_test.csv'))


