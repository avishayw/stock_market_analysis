import numpy as np
from indicators.momentum_indicators import rate_of_change
from indicators.my_indicators import percental_atr
import yfinance as yf


def detect_aggressive_sell(df):
    """
    From my experience, aggressive sell is accompanied with short term negative ROC and higher volume than usual.
    I think the aggressive sell can be detected before the substantial decrease in the price as the volume might
    start to increase due to smart money sell off.

    I will describe a few suggestion to detect such sell and check them:
    1. Take the maximum volume every three days, then do average every 20 days. If today's volume pass the average
    by 30% - it's a sell off. Result: Too many false alarms. Only 3% of volume signals approved by ROC
    2. If the ROC <-10 and Volume > average 20 it's hard sell off. Result: shit
    3. If abs(ROC) > %ATR(10) and ROC < 0 - it's a sell off. Result:

    Ways to test:
    1. View some graphs
    2. I consider "aggressive sell" to cause at least -30% over max. 3 days. So change ROC every day up to 3 days
    after signal
    """
    atr_period = 10
    roc_atr_ratio = 2
    df = percental_atr(df, atr_period)
    approved_aggressive_sell_change = -40.0

    check_days_after = 10

    detected_signals = []

    for i in range(atr_period, len(df)-check_days_after):
        today_close = df.iloc[i]['Close']
        yesterday_close = df.shift(1).iloc[i]['Close']
        roc = ((today_close - yesterday_close)/yesterday_close)*100.0
        if abs(roc)/df.iloc[i][f'%ATR{atr_period}'] > roc_atr_ratio and roc < 0:
            ratio = abs(roc)/df.iloc[i][f'%ATR{atr_period}']
            date = df.iloc[i]['Date']
            j = 1
            min_change = 1000
            max_change = -1000
            while j < check_days_after:
                change = ((df.shift(1).iloc[i+j]['Close'] - df.shift(1).iloc[i]['Close'])/df.shift(1).iloc[i]['Close'])*100
                if change < min_change:
                    min_change = change
                if change > max_change:
                    max_change = change
                if change <= approved_aggressive_sell_change:
                    print(date, ratio, min_change, max_change, 'approved')
                    detected_signals.append(1)
                    break
                elif j == check_days_after - 1:
                    print(date, ratio, min_change, max_change, 'not approved')
                    detected_signals.append(0)
                j += 1

    print(np.mean(detected_signals))


ticker = 'PYPL'
df = yf.Ticker(ticker).history(period='max', interval='1d')[-2016:]
df.reset_index(inplace=True)

detect_aggressive_sell(df)
