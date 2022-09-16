import numpy as np
import pandas as pd


def gappy_stock(df, major_gap_ratio=0.2):

    df['gap'] = (df.shift(1)['Open'] - df['Close']).abs()/df.shift(1)['Open']
    major_gaps = df.loc[df['gap'] > major_gap_ratio]
    if major_gaps.empty:
        return 0
    return len(major_gaps)


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    import pandas as pd

    tickers = get_all_snp_stocks()

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))[-1008:]
        except ValueError:
            continue
        print(f'{ticker}: {gappy_stock(df, major_gap_ratio=0.15)}')
