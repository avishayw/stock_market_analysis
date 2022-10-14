import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
from utils.download_stock_csvs import download_stock_day, download_stock_week
from utils.in_sample_tickers import *
from machine_learning_stuff.linear_regression import backward_linear_regression


def plot_both_trendlines(df, backcandles=100):
    candleid = random.choice(list(range(backcandles, len(df))))

    brange = int(np.floor(backcandles*0.9))  # should be less than backcandles
    wind = 5

    ############## MAX
    max_touched_count_opt = 0
    xxmaxopt = np.array([])

    for r1 in range(backcandles - brange, backcandles + brange):
        maxim = np.array([])
        xxmax = np.array([])

        if r1 > candleid:
            continue
        for i in range(candleid - r1, candleid + 1 - wind, wind):
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
            slmaxopt = slmax
            adjintercmaxopt = adjintercmax
            xxmaxopt = xxmax.copy()

    if max_touched_count_opt == 0:
        print('no match')
        exit()

    ############## MIN
    min_touched_count_opt = 0
    xxminopt = np.array([])

    for r1 in range(backcandles - brange, backcandles + brange):
        minim = np.array([])
        xxmin = np.array([])

        if r1 > candleid:
            continue
        for i in range(candleid - r1, candleid + 1 - wind, wind):
            try:
                minim = np.append(minim, df.Low.iloc[i:i + wind].min())
                xxmin = np.append(xxmin, df.Low.iloc[i:i + wind].idxmin())
            except ValueError as e:
                print(e)
                print('i', i)
                print('len', len(df))
                print('r1', r1)
                print('candleid', candleid)
                exit()

        slmin, intercmin = np.polyfit(xxmin, minim, 1)

        ################################## MINE ###########################################
        adjintercmin = (df.Low.iloc[xxmin] - slmin * xxmin).min()

        min_breached = False
        min_touched_count = 0
        for i in range(int(min(xxmin)), int(max(xxmin)) + 1):
            y = df.Low.iloc[i]
            y_tag = slmin * i + adjintercmin
            if y < y_tag * 0.995:
                min_breached = True
                break
            elif y * 0.995 <= y_tag <= y * 1.005:
                min_touched_count += 1

        # print(r1, min_touched_count)

        if min_touched_count > min_touched_count_opt and not min_breached:
            ##########################
            min_touched_count_opt = min_touched_count
            slminopt = slmin
            adjintercminopt = adjintercmin
            xxminopt = xxmin.copy()

    if min_touched_count_opt == 0:
        print('no match')
        exit()

    dfpl = df.copy()
    fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                                         open=dfpl['Open'],
                                         high=dfpl['High'],
                                         low=dfpl['Low'],
                                         close=dfpl['Close'])])

    # xxmaxall = np.arange(min(xxmaxopt), max(xxmaxopt)+1, 1)
    # xxmaxtest = np.arange(min(xxmaxopt), max(xxmaxopt)+300, 1)
    # xxminall = np.arange(min(xxminopt), max(xxminopt) + 1, 1)
    # xxmintest = np.arange(min(xxminopt), max(xxminopt) + 300, 1)
    xxmaxall = np.arange(min(xxmaxopt), candleid + 1, 1)
    xxmaxtest = np.arange(min(xxmaxopt), candleid + 300, 1)
    xxminall = np.arange(min(xxminopt), candleid + 1, 1)
    xxmintest = np.arange(min(xxminopt), candleid + 300, 1)

    fig.add_trace(go.Scatter(x=xxmaxall, y=slmaxopt * xxmaxall + adjintercmaxopt, mode='lines', name='max slope'))
    fig.add_trace(go.Scatter(x=xxmaxtest, y=slmaxopt * xxmaxtest + adjintercmaxopt, mode='lines', name='max slope test'))
    fig.add_trace(go.Scatter(x=xxminall, y=slminopt * xxminall + adjintercminopt, mode='lines', name='min slope'))
    fig.add_trace(go.Scatter(x=xxmintest, y=slminopt * xxmintest + adjintercminopt, mode='lines', name='min slope test'))
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.show()


# while True:
ticker = random.choice(IN_SAMPLE_TICKERS)
df = pd.read_csv(download_stock_day(ticker))[-1008:].reset_index()
plot_both_trendlines(df, backcandles=100)
