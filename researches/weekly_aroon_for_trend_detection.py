from indicators.trend_indicators import aroon
from utils.download_stock_csvs import download_stock_day, download_stock_week
import pandas as pd
import numpy as np

ticker = 'BBBY'

df = pd.read_csv(download_stock_week(ticker))[-208:]
aroon_period = 20
df = aroon(df, aroon_period)
df['aroon_up_angle'] = (df['aroon_up'] - df.shift(1)['aroon_up']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
df['aroon_down_angle'] = (df['aroon_down'] - df.shift(1)['aroon_down']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
df['optional_uptrend'] = np.where((df.shift(1)['aroon_up'] < df.shift(1)['aroon_down']) &
                                  (df['aroon_up'] > df['aroon_down']), True, False)


# Statistics for uptrend after aroons crossing

uptrend_after_crossing = []

for i in range(len(df)):
    if df.iloc[i]['optional_uptrend']:
        uptrend = True
        uptrend_count = 0
        j = 0
        while uptrend:
            if df.shift(-j-1).iloc[i]['High'] > df.shift(-j).iloc[i]['High']:
                uptrend_count += 1
                j += 1
            else:
                uptrend_after_crossing.append(uptrend_count)
                uptrend = False

if uptrend_after_crossing:
    print(1-((uptrend_after_crossing.count(0)/len(uptrend_after_crossing))))
else:
    print('no_crossings')
