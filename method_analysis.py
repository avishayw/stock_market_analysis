import pandas as pd
import json
from doji_method import doji_method
from get_stock_daily_max_history_df import get_stock_daily_max_history_df
from get_all_snp_companies import get_all_snp_companies


success_per_ticker = {}
snp_tickers = get_all_snp_companies()['Symbol'].tolist()

for ticker in snp_tickers:
    try:
        stock_df = get_stock_daily_max_history_df(ticker)
        success_per_ticker[ticker] = doji_method(stock_df, 5.0, 10.0, 30) * 100
    except TypeError:
        pass
    with open("doji_method_success_per_ticker.json", 'w') as f:
        json.dump(success_per_ticker,f,indent=4)
