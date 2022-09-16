import pandas as pd
import numpy as np


def max_profit_sanity_long(df):
    change_decimal = pd.DataFrame(np.where(df['Open'] < df['Close'], (df['Close']-df['Open'])/df['Open'], np.nan))
    change_decimal.dropna(inplace=True)
    multiplier = change_decimal + 1.0
    return multiplier.prod().tolist()[0]


def max_profit_sanity_short(df):
    change_decimal = pd.DataFrame(np.where(df['Open'] > df['Close'], (df['Open']-df['Close'])/df['Open'], np.nan))
    change_decimal.dropna(inplace=True)
    multiplier = change_decimal + 1.0
    return multiplier.prod().tolist()[0]


def max_profit_sanity_total(df):
    change_decimal = pd.DataFrame(np.where(df['Open'] < df['Close'], (df['Close']-df['Open'])/df['Open'], (df['Open']-df['Close'])/df['Open']))
    multiplier = change_decimal + 1.0
    return multiplier.prod().tolist()[0]


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import json

    ticker = 'AAPL'

    df = pd.read_csv(download_stock_day(ticker))

    df = df[-1008:]

    print(max_profit_sanity_long(df), max_profit_sanity_short(df), max_profit_sanity_total(df))