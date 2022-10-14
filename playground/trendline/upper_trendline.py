import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
from utils.download_stock_csvs import download_stock_day
from utils.in_sample_tickers import *
from machine_learning_stuff.linear_regression import backward_linear_regression


def plot_upper_trendline(df):
    backcandles = 100
    candleid = random.choice(list(range(backcandles, len(df))))

    brange = int(np.floor(backcandles*0.9))  # should be less than backcandles
    wind = 5

    optbackcandles = backcandles
    sldiff = 100000000
    sldist = 100000000
    max_touched_count_opt = 0
    min_touched_count_opt = 0
    xxmaxopt = np.array([])

    # candleid = 216
    # backcandles = 33
    for r1 in range(backcandles - brange, backcandles + brange):
        maxim = np.array([])
        xxmax = np.array([])

        if r1 > candleid:
            continue
        for i in range(candleid - r1, candleid + 1, wind):
            try:
                maxim = np.append(maxim, df.High.iloc[i:i + wind].max())
                xxmax = np.append(xxmax, df.High.iloc[i:i + wind].idxmax())
            except ValueError as e:
                print(e)
                print('i', i)
                print('len', len(df))
                print('r1', r1)
                print('candleid', candleid)
                exit()

        slmax, intercmax = np.polyfit(xxmax, maxim, 1)

        ################################## MINE ###########################################
        adjintercmax = (df.High.iloc[xxmax] - slmax * xxmax).max()

        max_breached = False
        max_touched_count = 0
        for i in range(int(min(xxmax)), int(max(xxmax))+1):
            y = df.High.iloc[i]
            y_tag = slmax*i+adjintercmax
            if y > y_tag*1.005:
                max_breached = True
                break
            elif y*0.995 <= y_tag <= y*1.005:
                max_touched_count += 1

        # print(r1, max_touched_count)

        if max_touched_count > max_touched_count_opt and not max_breached:
            ##########################
            max_touched_count_opt = max_touched_count
            optbackcandles = r1
            slmaxopt = slmax
            intercmaxopt = intercmax
            adjintercmaxopt = adjintercmax
            maximopt = maxim.copy()
            xxmaxopt = xxmax.copy()

    if max_touched_count_opt == 0:
        print('no match')
        exit()

    dfpl = df.copy()
    fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                                         open=dfpl['Open'],
                                         high=dfpl['High'],
                                         low=dfpl['Low'],
                                         close=dfpl['Close'])])

    xxmaxall = np.arange(min(xxmaxopt), max(xxmaxopt)+1, 1)
    xxmaxtest = np.arange(min(xxmaxopt), max(xxmaxopt)+300, 1)

    fig.add_trace(go.Scatter(x=xxmaxall, y=slmaxopt * xxmaxall + adjintercmaxopt, mode='lines', name='max slope'))
    fig.add_trace(go.Scatter(x=xxmaxtest, y=slmaxopt * xxmaxtest + adjintercmaxopt, mode='lines', name='max slope test'))
    fig.show()


# while True:
ticker = random.choice(IN_SAMPLE_TICKERS)
df = pd.read_csv(download_stock_day(ticker))[-1008:].reset_index()
plot_upper_trendline(df)
