from indicators.momentum_indicators import rate_of_change
from indicators.my_indicators import percental_atr
from utils.download_stock_csvs import download_stock_day
from utils.get_all_stocks import get_all_nasdaq_100_stocks
from utils.paths import save_under_results_path
import pandas as pd


tickers = get_all_nasdaq_100_stocks()

tickers = ['AAPL', 'PYPL', 'ASRT']

for ticker in tickers:
    df = pd.read_csv(download_stock_day(ticker))
    df = percental_atr(df, 20)
    df = rate_of_change(df, 1)
    # TODO: consider to shift ROC in order to check if there are "effects" to low %ATR

    # if df.iloc[-1]['max_%ATR_5_days'] < 1.4 and df.iloc[-1]['Volume'] > 2000000.0:
    df = df[-2004:]
    df.to_csv(f'{ticker}_ATR_ROC_relationship.csv')
