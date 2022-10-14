import numpy as np
import pandas as pd
from matplotlib import pyplot
import plotly.graph_objects as go
from utils.in_sample_tickers import *
from utils.download_stock_csvs import download_stock_day
from utils.paths import save_under_results_path
import random
from sklearn.linear_model import LinearRegression
import glob
import os


# results_dir = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results"
# htmls = glob.glob(results_dir + '/*.html')
# htmls = [h for h in htmls if 'channel' in h and 'different_channels' not in h]
# setups = {}
# for h in htmls:
#     name = str(os.path.basename(h)).replace('.html', '').split('_')
#     ticker = name[0]
#     candleid = int(name[1])

    # while True:
    # ticker = random.choice(IN_SAMPLE_TICKERS)
ticker = 'AA'
df = pd.read_csv(download_stock_day(ticker)).reset_index()

backcandles = 1000  # 6*8
brange = 300
# brange = int(np.floor(backcandles*0.9))  # backcandles//4 #should be less than backcandles
wind = 5
candleid = random.choice(list(range(backcandles+brange, len(df))))
# candleid = 14037

optbackcandles = None
sldiff = 10000

for r1 in range(backcandles - brange, backcandles + brange):
    maxim = np.array([])
    minim = np.array([])
    xxmin = np.array([])
    xxmax = np.array([])
    for i in range(candleid - r1, candleid + 1 - wind, wind):
        minim = np.append(minim, df.Low.iloc[i:i + wind].min())
        xxmin = np.append(xxmin, df.Low.iloc[i:i + wind].idxmin())
    for i in range(candleid - r1, candleid + 1 - wind, wind):
        maxim = np.append(maxim, df.High.loc[i:i + wind].max())
        xxmax = np.append(xxmax, df.High.iloc[i:i + wind].idxmax())
    slmin, intercmin = np.polyfit(xxmin, minim, 1)
    slmax, intercmax = np.polyfit(xxmax, maxim, 1)

    xx = np.arange(min(min(xxmin), min(xxmax)), candleid + 1, 1)
    avg_dist = np.mean((slmax * xx + intercmax) - (slmin * xx + intercmin))
    dist = (slmax * candleid + intercmax) - (slmin * candleid + intercmin)

    if abs(slmin - slmax) < sldiff:
        sldiff = abs(slmin - slmax)
        optbackcandles = r1
        slminopt = slmin
        slmaxopt = slmax
        intercminopt = intercmin
        intercmaxopt = intercmax
        maximopt = maxim.copy()
        minimopt = minim.copy()
        xxminopt = xxmin.copy()
        xxmaxopt = xxmax.copy()

# trend
if slmaxopt >= 0.001 and slminopt >= 0.001:
    direction = 'long'
    slope = slminopt
elif slmaxopt <= -0.001 and slminopt <= -0.001:
    direction = 'short'
    slope = slmaxopt
else:
    print(f'({candleid}/{len(df)}) no trend slope from channel', slmaxopt, slminopt)
    exit()

##### Adding OLS for the period to approve trend
sample_df = df[candleid-200: candleid+1].copy()
x = sample_df.index.to_numpy().reshape(-1, 1)
y = sample_df['Close'].to_numpy()
model = LinearRegression()
fit = False
try:
    model.fit(x, y)
    fit = True
except ValueError:
    print('no fit')

dfpl = df.copy()
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                                     open=dfpl['Open'],
                                     high=dfpl['High'],
                                     low=dfpl['Low'],
                                     close=dfpl['Close'])])

xxall = np.arange(max(min(xxminopt), min(xxmaxopt)), candleid + 1, 1)
xxalltest = np.arange(max(min(xxminopt), min(xxmaxopt)), candleid + 300, 1)
adjintercmax = (df.High.iloc[xxall] - slope * xxall).max()
adjintercmin = (df.Low.iloc[xxall] - slope * xxall).min()

inner_safety_margin_ratio = 0.15
outer_safety_margin_ratio = 0.15
channel_candleid_range = (slope * candleid + adjintercmax) - (slope * candleid + adjintercmin)
# inner_margin = (adjintercmax - adjintercmin) * inner_safety_margin_ratio
# outer_margin = (adjintercmax - adjintercmin) * outer_safety_margin_ratio
inner_margin = channel_candleid_range * inner_safety_margin_ratio
outer_margin = channel_candleid_range * outer_safety_margin_ratio
innermarginintercmax = adjintercmax - inner_margin
innermarginintercmin = adjintercmin + inner_margin
outermarginintercmax = adjintercmax + outer_margin
outermarginintercmin = adjintercmin - outer_margin

candle_mid = ((slope*candleid + adjintercmax) + (slope*candleid + adjintercmin))*0.5
midinterc = candle_mid - slope*candleid
# midinterc = (adjintercmin + adjintercmax)*0.5

print(candleid, optbackcandles, ticker)
# print('max', slmaxopt, adjintercmax)
# print('min', slminopt, adjintercmin)

fig.add_trace(go.Scatter(x=xxall, y=slope * xxall + adjintercmin, mode='lines', name='min slope'))
fig.add_trace(go.Scatter(x=xxall, y=slope * xxall + adjintercmax, mode='lines', name='max slope'))
fig.add_trace(go.Scatter(x=xxalltest, y=slope * xxalltest + adjintercmin, mode='lines', name='min slope test', line={'dash': 'dash'}))
fig.add_trace(go.Scatter(x=xxalltest, y=slope * xxalltest + adjintercmax, mode='lines', name='max slope test', line={'dash': 'dash'}))
fig.add_trace(go.Scatter(x=xxalltest, y=slope * xxalltest + innermarginintercmin, mode='lines', name='min slope test inner margin', line={'dash': 'dash'}))
fig.add_trace(go.Scatter(x=xxalltest, y=slope * xxalltest + innermarginintercmax, mode='lines', name='max slope test inner margin', line={'dash': 'dash'}))
fig.add_trace(go.Scatter(x=xxalltest, y=slope * xxalltest + outermarginintercmin, mode='lines', name='min slope test outer margin', line={'dash': 'dash'}))
fig.add_trace(go.Scatter(x=xxalltest, y=slope * xxalltest + outermarginintercmax, mode='lines', name='max slope test outer margin', line={'dash': 'dash'}))
fig.add_trace(go.Scatter(x=xxalltest, y=slope * xxalltest + midinterc, mode='lines', name='mid slope test'))

if fit:
    slopeols, intercols = model.coef_[0], model.intercept_
    print('ols', slopeols, intercols)
    xxols = np.arange(candleid-200, candleid, 1)
    fig.add_trace(go.Scatter(x=xxols, y=slopeols * xxols + intercols, mode='lines', name='OLS slope test'))

fig.update(layout_xaxis_rangeslider_visible=False)
fig.show()

### Checking how many times the layers were touched in 5 window spans
channel_df = df[candleid-optbackcandles: candleid+1].copy()
channel_df['max_line'] = channel_df.index * slope + adjintercmax
channel_df['max_line_inner_margin'] = channel_df.index * slope + innermarginintercmax
channel_df['min_line'] = channel_df.index * slope + adjintercmin
channel_df['min_line_inner_margin'] = channel_df.index * slope + innermarginintercmin
upper_layer_count = 0
lower_layer_count = 0
for i in range(0, len(channel_df), 5):
    sample_df = channel_df.iloc[i:i+5].copy()
    if not sample_df.loc[sample_df['High'] > sample_df['max_line_inner_margin']].empty:
        upper_layer_count += 1
    if not sample_df.loc[sample_df['Low'] < sample_df['min_line_inner_margin']].empty:
        lower_layer_count += 1

print('upper layer touched', upper_layer_count)
print('lower layer touched', lower_layer_count)
print('score', (upper_layer_count+lower_layer_count)/np.floor(optbackcandles/5))

### Calculating price density
sample_df = df[candleid-optbackcandles:candleid+1].copy()
sample_df['high_line'] = sample_df.index*slope + adjintercmax
sample_df['low_line'] = sample_df.index*slope + adjintercmin
band = (sample_df['high_line'] - sample_df['low_line']).sum()
price = (sample_df['High'] - sample_df['Low']).sum()
price_density = price/band
print('price density', price_density)

# TODO: add variance calculation in order to measure the spread of the prices in the channel. The price density won't do
