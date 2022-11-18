# Here I'll be taking some time back from now and plot a histogram of the prices.
# I'll make a list of all the different prices (open, high, low & close) and plot the histogram
import yfinance as yf
import pandas as pd
import plotly.express as px
from matplotlib import pyplot as plt
import numpy as np
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from astropy.stats import freedman_bin_width
from scipy.stats import skew, kurtosis


def price_histogram(ticker, df, idx, period):

    sample_df = df[idx-period:idx].copy()

    prices = []

    for row in range(len(sample_df)):
        high = sample_df.iloc[row]['High']
        low = sample_df.iloc[row]['Low']
        prices = prices + list(np.arange(low, high, .01))

    prices = sorted(prices)

    # histogram
    # nbins = int(math.ceil(math.sqrt(len(prices))))
    bin_width = freedman_bin_width(prices)
    # nbins = math.ceil((np.max(prices) - np.min(prices)) / bin_width)
    nbins = 100
    # print(nbins, bin_width)
    bins = np.linspace(np.ceil(min(prices)),
                       np.floor(max(prices)),
                       nbins)

    occurrences, price_ranges = np.histogram(prices, bins)
    # histogram_dict = {}

    # for i in range(len(occurrences)):
    #     histogram_dict[occurrences[i]] = (round(price_ranges[i], 2), round(price_ranges[i + 1], 2))

    print(
        f'stats: mean: {np.mean(prices)} stdev: {np.std(prices)} coefficient of variation: {np.std(prices) / np.mean(prices)}'
        f' 10th: {np.percentile(prices, 10)} 90th: {np.percentile(prices, 90)}')

    # print(f'days back: {period}')
    # print(histogram_dict[max(occurrences)])

    prices_skew = np.round(skew(prices), 3)
    prices_kurtosis = np.round(kurtosis(prices), 3)
    stdev = np.std(prices)
    close = df.shift(1).iloc[idx]['Close']

    plt.xlim([min(min(prices), close)*0.98, max(max(prices), close)*1.02])
    plt.hist(prices, bins=bins, alpha=0.5)
    plt.title(ticker)
    plt.axvline(np.mean(prices), color='r')
    plt.axvline(np.mean(prices) + stdev, color='k')
    plt.axvline(np.mean(prices) - stdev, color='k')
    plt.axvline(close, color='m')
    plt.axvline(np.percentile(prices, 10), color='y')
    plt.axvline(np.percentile(prices, 90), color='y')
    # for mode in modes:
    #     plt.axvline(mode, color='g')
    plt.axvline(np.median(prices), color='b')
    plt.text(np.percentile(prices, 30), (max(occurrences)+2), f'skew: {prices_skew} kurtosis: {prices_kurtosis}')

    # plt.savefig(fr"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\histograms\{ticker}_{df.iloc[idx]['Date']}_{period}.html")
    plt.show()
    plt.close()


# ticker = 'AAPL'
# stock = yf.Ticker(ticker)
#
# stock_df = stock.history(period='max', interval='1d')[-1008:].reset_index()
# stock_df['Datetime'] = pd.to_datetime(stock_df['Date'])
#
# days_back_list = [5, 9, 20, 50, 100, 200]
#
# for days_back in days_back_list:
#
#     start_date = stock_df.iloc[-1]['Datetime'] - relativedelta(days=days_back)
#     sample_df = stock_df.loc[stock_df['Datetime'] >= start_date].copy().reset_index().drop(columns=['index'])
#
#     # print(f'First df close: {sample_df.iloc[0]["Date"]}, {sample_df.iloc[0]["Close"]}')
#     # print(f'Last df close: {sample_df.iloc[-1]["Date"]}, {sample_df.iloc[-1]["Close"]}')
#     prices = []
#
#     for row in range(len(sample_df)):
#         high = sample_df.iloc[row]['High']
#         low = sample_df.iloc[row]['Low']
#         prices = prices + list(np.arange(low, high, .01))
#
#     prices = sorted(prices)
#
#     # histogram
#     # nbins = int(math.ceil(math.sqrt(len(prices))))
#     bin_width = freedman_bin_width(prices)
#     nbins = math.ceil((np.max(prices) - np.min(prices))/bin_width)
#     # print(nbins, bin_width)
#     bins = np.linspace(np.ceil(min(prices)),
#                        np.floor(max(prices)),
#                        nbins)
#
#     occurrences, price_ranges = np.histogram(prices, bins)
#     histogram_dict = {}
#
#     for i in range(len(occurrences)):
#         histogram_dict[occurrences[i]] = (round(price_ranges[i], 2), round(price_ranges[i+1], 2))
#
#     print(f'stats: mean: {np.mean(occurrences)} stdev: {np.std(occurrences)} coefficient of variation: {np.std(occurrences)/np.mean(occurrences)}')
#
#     print(f'days back: {days_back}')
#     print(histogram_dict[max(occurrences)])

# Take the highest three occurrences
# max_occur = sorted(occurrences)[-3:]

# Take the occurrences with 1.5 stdev above avg
# occur_threshold = 1.5*np.std(occurrences) + np.mean(occurrences)
# max_occur = [occur for occur in occurrences if occur > occur_threshold]

# Take the occurrences which are 70% of max occurrence but above average
# percentile = 0.95
# occur_threshold = float(max(occurrences) - np.mean(occurrences))*percentile + np.mean(occurrences)
# max_occur = [occur for occur in occurrences if occur > occur_threshold]
# print(len(max_occur))
#
# frequent_prices = []
#
# for occur in max_occur:
#     frequent_prices = frequent_prices + list(histogram_dict[occur])
#
# frequent_prices = sorted(frequent_prices)
#
# print((frequent_prices[0], frequent_prices[-1], frequent_prices[-1]-frequent_prices[0]))

# plt.xlim([min(prices), max(prices)])
# plt.hist(prices, bins=bins, alpha=0.5)
#
# plt.show()

# price_histograms = []
# for row in range(length, len(stock_df)):
#     for i in range(length):

#
# prices = stock_df['High'].tolist() + stock_df['Close'].tolist() + stock_df['Open'].tolist() + stock_df['Low'].tolist()
# print(prices)
# print(len(prices))
#
# df = pd.DataFrame({'price': prices})
# fig = px.histogram(df, x='price', nbins=20)
# fig.show()

if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart
    import pandas as pd
    import time
    from utils.get_all_stocks import in_sample_tickers

    tickers = in_sample_tickers()
    for ticker in tickers:
        df = pd.read_csv(download_stock_day(ticker)).reset_index()
        # fig = candlestick_chart_fig(df, ticker)
        # fig.show()

        # for i in range(1008, len(df)):
        print(df.iloc[-1]['Date'])
        print('Open', df.iloc[-1]['Open'])
        print('Close', df.iloc[-2]['Close'])
        price_histogram(ticker, df, len(df) - 2, 200)
