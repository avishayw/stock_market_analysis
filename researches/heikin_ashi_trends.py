import numpy as np
from dateutil.relativedelta import relativedelta

def heikin_ashi_streaks(df):

    df['Datetime'] = pd.to_datetime(df['Date'])
    df['ha_close'] = (df['Open'] + df['Close'] + df['High'] + df['Low'])/4  # Heikin Ashi close
    df['ha_open'] = (df.shift(1)['Open'] + df.shift(1)['Close'])/2  # Heikin Ashi open
    df['ha_green'] = np.where(df['ha_close'] > df['ha_open'], True, False)


    df.reset_index(inplace=True)
    df.drop(columns=['index'], inplace=True)

    for i in range(7):
        df[f'up_{i}'] = 0  # up streak with up to i successive down days allowed
        df[f'up_{i}_%'] = np.nan
        df[f'down_{i}'] = 0  # down streak with up to i successive up days allowed
        df[f'down_{i}_%'] = np.nan

        up_counter = 0
        up_streak_counter = 0
        down_counter = 0
        down_streak_counter = 0

        # up streak
        for j in range(len(df)):
            if df.iloc[j]['ha_close'] > df.iloc[j]['ha_open']:
                up_counter += 1
                if down_counter < i + 1:
                    up_counter += down_counter
                    down_counter = 0
            elif df.iloc[j]['ha_close'] < df.iloc[j]['ha_open'] and up_counter > 0:
                down_counter += 1
                if up_counter != 0 and down_counter > i:
                    df._set_value(j - down_counter, f'up_{i}', up_counter)
                    df._set_value(j - down_counter, f'up_{i}_%',
                                  ((df.iloc[j-down_counter]['Close'] - df.iloc[j-down_counter-up_counter]['Close'])/df.iloc[j-down_counter-up_counter]['Close'])*100)
                    up_counter = 0
                    down_counter = 0

        up_counter = 0
        down_counter = 0

        # down streak
        for j in range(len(df)):
            if df.iloc[j]['ha_close'] < df.iloc[j]['ha_open']:
                down_counter += 1
                if up_counter < i + 1:
                    down_counter += up_counter
                    up_counter = 0
            elif df.iloc[j]['ha_close'] > df.iloc[j]['ha_open'] and down_counter > 0:
                up_counter += 1
                if down_counter != 0 and up_counter > i:
                    df._set_value(j - up_counter, f'down_{i}', down_counter)
                    df._set_value(j - up_counter, f'down_{i}_%',
                                  ((df.iloc[j-up_counter]['Close'] - df.iloc[j-up_counter-down_counter]['Close']) / df.iloc[j-up_counter-down_counter]['Close']) * 100)
                    down_counter = 0
                    up_counter = 0

    return df


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import json

    # tickers = get_all_snp_companies()

    ticker = 'AAPL'
    df = pd.read_csv(download_stock_day(ticker))
    df = df[-756:]
    df = heikin_ashi_streaks(df)

    df.to_csv(save_under_results_path(f"{ticker}_heikin_ashi_trends.csv"))



