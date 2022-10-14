import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
from utils.download_stock_csvs import download_stock_day
from utils.in_sample_tickers import *
from machine_learning_stuff.linear_regression import backward_linear_regression


ticker = random.choice(IN_SAMPLE_TICKERS)
ticker = 'WISH'
df = pd.read_csv(download_stock_day(ticker))[-1008:].reset_index()

backcandles = 100
candleid = random.choice(list(range(backcandles, len(df))))

brange = 90  # should be less than backcandles
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
# for r1 in range(backcandles, backcandles + 1):
    maxim = np.array([])
    # minim = np.array([])
    # xxmin = np.array([])
    xxmax = np.array([])

    # for i in range(candleid - r1, candleid + 1, wind):
    #     minim = np.append(minim, df.Low.iloc[i:i + wind].min())
    #     xxmin = np.append(xxmin, df.Low.iloc[i:i + wind].idxmin())
    for i in range(candleid - r1, candleid + 1, wind):
        maxim = np.append(maxim, df.High.iloc[i:i + wind].max())
        xxmax = np.append(xxmax, df.High.iloc[i:i + wind].idxmax())
    # slmin, intercmin = np.polyfit(xxmin, minim, 1)
    slmax, intercmax = np.polyfit(xxmax, maxim, 1)

    ################################## MINE ###########################################
    adjintercmax = (df.High.iloc[xxmax] - slmax * xxmax).max()
    # adjintercmin = (df.Low.iloc[xxmin] - slmin * xxmin).min()

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

    # min_breached = False
    # min_touched_count = 0
    # for i in range(int(min(xxmin)), int(max(xxmin))+1):
    #     y = df.Low.iloc[i]
    #     y_tag = slmin*i+adjintercmin
    #     if y < y_tag*0.995:
    #         min_breached = True
    #         break
    #     elif y*0.995 <= y_tag <=0.995:
    #         min_touched_count += 1

    # print(r1, min_touched_count, max_touched_count)
    print(r1, max_touched_count)
    ############################################################################################

    # dist = (slmax * candleid + intercmax) - (slmin * candleid + intercmin)
    # if (dist < sldist) and abs(slmin-slmax)<sldiff:  # abs(slmin-slmax)<sldiff and
    # if max_touched_count > max_touched_count_opt and min_touched_count > min_touched_count_opt and not max_breached and not min_breached:
    if max_touched_count > max_touched_count_opt and not max_breached:
        ##########################
        max_touched_count_opt = max_touched_count
        # min_touched_count_opt = min_touched_count
        ##########################
        # sldiff = abs(slmin-slmax)
        # sldist = dist
        optbackcandles = r1
        # slminopt = slmin
        slmaxopt = slmax
        # intercminopt = intercmin
        intercmaxopt = intercmax
        adjintercmaxopt = adjintercmax
        maximopt = maxim.copy()
        # minimopt = minim.copy()
        # xxminopt = xxmin.copy()
        xxmaxopt = xxmax.copy()

if max_touched_count_opt == 0:
    print('no match')
    exit()
# print('ticker', ticker)
# print('candle id', candleid)
# print('optbackcandles', optbackcandles)
# dfpl = df[candleid - wind - optbackcandles - backcandles:candleid + optbackcandles]
dfpl = df.copy()
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                                     open=dfpl['Open'],
                                     high=dfpl['High'],
                                     low=dfpl['Low'],
                                     close=dfpl['Close'])])

# adjintercmax = (df.High.iloc[xxmaxopt] - slmaxopt * xxmaxopt).max()
# adjintercmin = (df.Low.iloc[xxminopt] - slminopt * xxminopt).min()
# adjintercmax = intercmaxopt
# adjintercmin = intercminopt
xxmaxall = np.arange(min(xxmaxopt), max(xxmaxopt)+1, 1)
xxmaxtest = np.arange(min(xxmaxopt), max(xxmaxopt)+300, 1)
# xxminall = np.arange(min(xxminopt), max(xxminopt)+1, 1)
# xxall = np.arange(max(min(xxmaxopt), min(xxminopt)), min(max(xxmaxopt)+1, max(xxminopt)+1), 1)
# Limit the mean square root error
# rmse = (df.High.iloc[xxmaxall] - slmaxopt * xxmaxall).abs().pow(2).sum()
# adjintercmax = (df.High.iloc[xxmaxopt] - slmaxopt * xxmaxopt).mean() + (df.High.iloc[xxmaxopt] - slmaxopt * xxmaxopt).std()
# adjintercmin = (df.Low.iloc[xxminopt] - slminopt * xxminopt).mean() - (df.Low.iloc[xxminopt] - slminopt * xxminopt).std()

# fig.add_trace(go.Scatter(x=xxall, y=slminopt * xxall + adjintercmin, mode='lines', name='min slope'))
fig.add_trace(go.Scatter(x=xxmaxall, y=slmaxopt * xxmaxall + adjintercmaxopt, mode='lines', name='max slope'))
fig.add_trace(go.Scatter(x=xxmaxtest, y=slmaxopt * xxmaxtest + adjintercmaxopt, mode='lines', name='max slope test'))
fig.show()
