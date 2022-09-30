from utils.download_stock_csvs import download_stock_day
from machine_learning_stuff.linear_regression import rolling_backward_linear_regression
from trade_managers._signal_trading_manager import signal_trading_manager, signal_trading_manager_long, signal_trading_manager_short
import pandas as pd
import numpy as np

ticker = 'SPY'

df = pd.read_csv(download_stock_day(ticker))[-4032:]
df = rolling_backward_linear_regression(df, 'Close', 200)
roc_period = 20
df['score_roc'] = ((df['score'] - df.shift(roc_period)['score'])/df.shift(roc_period)['score'])*100.0
# df['buy_long_signal'] = np.where((df['score'] >= 0.5) & (df['score'] < 0.6), True, False)
# df['sell_long_signal'] = np.where((df['score'] > 0.8) | (df['score_roc'] < -5.0), True, False)
# df['sell_short_signal'] = np.where((df['score'] < 0.5) & (df['score'] > 0.01) & (df['score_roc'] < -5.0), True, False)
# df['buy_short_signal'] = np.where((df['score'] < 0.01) | (df['score_roc'] > 5.0), True, False)
# trades, final_cap = signal_trading_manager(ticker, df)
df['buy_signal'] = np.where((df['coefficient'] > 1) & (df['score'] >= 0.5) & (df['score'] < 0.6), True, False)
df['sell_signal'] = np.where((df['score'] > 0.8) | (df['score_roc'] < -5.0), True, False)
signal_trading_manager_long(ticker, df)
