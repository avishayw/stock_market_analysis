import pandas as pd
import numpy as np
from utils.in_sample_tickers import *
from utils.download_stock_csvs import download_stock_day
import random
from utils.paths import save_under_results_path

days = list(range(21,253,21))

# ticker = random.choice(IN_SAMPLE_TICKERS)
ticker = 'ANET'
df = pd.read_csv(download_stock_day(ticker))

for day in days:
    df[f'{day}_days_high'] = df['High'].rolling(day).max()
    df[f'{day}_days_breakout'] = np.where(df['Close'] > df.shift(1)[f'{day}_days_high'], 1, 0)

breakout_columns = [c for c in df.columns.tolist() if 'breakout' in c]
df['total_breakouts'] = df[breakout_columns].sum(axis='columns')

df.to_csv(save_under_results_path(f'{ticker}_n_day_breakout.csv'))