import numpy as np
import pandas as pd
from astropy.stats import freedman_bin_width
from dateutil.relativedelta import relativedelta
from datetime import datetime
from indicators.my_indicators import percental_atr
from indicators.momentum_indicators import williams_r, rate_of_change
from indicators.trend_indicators import exponential_moving_average
from machine_learning_stuff.linear_regression import rolling_ols


def histogram_trading_v_0_1(ticker, df):
    """
    For each period I will find the most fair price, i.e. the price that was traded the most
    Those prices (from all the periods) will create a kind of 'fair price range' which can help me decide if the stock is cheap or
    expensive relative to this range.
    """
    if 'Datetime' not in df.columns.tolist():
        df['Datetime'] = pd.to_datetime(df['Date'])

    days_back_list = [5, 9, 20, 50, 100, 200]

    i = max(days_back_list)
    long_position = False
    tp = None
    sl = None
    cap = 100.0
    trades = []

    while i < len(df):

        if not long_position:
            price_range = []
            for days_back in days_back_list:

                start_date = df.iloc[i]['Datetime'] - relativedelta(days=days_back)
                end_date = df.iloc[i]['Datetime']
                sample_df = df.loc[(df['Datetime'] >= start_date) & (df['Datetime'] <= end_date)].copy().reset_index().drop(columns=['index'])

                prices = []

                for row in range(len(sample_df)):
                    high = sample_df.iloc[row]['High']
                    low = sample_df.iloc[row]['Low']
                    prices = prices + list(np.arange(low, high, .01))

                prices = sorted(prices)

                bin_width = freedman_bin_width(prices)
                nbins = int(np.ceil((np.max(prices) - np.min(prices)) / bin_width))
                bins = np.linspace(np.floor(min(prices)),
                                   np.ceil(max(prices)),
                                   nbins)

                # TODO: remove
                # print('check')

                try:
                    occurrences, price_ranges = np.histogram(prices, bins)
                except ValueError as e:
                    print(e)
                    print(f'min ceil: {np.floor(min(prices))} max floor: {np.ceil(max(prices))} nbins: {nbins}')
                    print(bins)
                    exit()

                histogram_dict = {}
                for j in range(len(occurrences)):
                    histogram_dict[occurrences[j]] = (round(price_ranges[j], 2), round(price_ranges[j + 1], 2))

                price_range = price_range + list(histogram_dict[max(occurrences)])

            if min(price_range) > df.iloc[i]['Close']:
                enter_price = df.shift(-1).iloc[i]['Open']
                enter_date = df.shift(-1).iloc[i]['Date']
                tp = np.mean(price_range)
                sl = enter_price*0.9
                long_position = True
                i += 1

        else:
            if tp < df.iloc[i]['High']:
                if tp < df.iloc[i]['Open']:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = tp
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': enter_price < exit_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False

            elif sl > df.iloc[i]['Low']:
                if sl > df.iloc[i]['Open']:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = sl
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': enter_price < exit_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False

        i += 1
    print(ticker, cap)
    return trades, cap


def histogram_trading_v_0_2(ticker, df):
    """
    For each period I will find the most fair price, i.e. the price that was traded the most
    Those prices (from all the periods) will create a kind of 'fair price range' which can help me decide if the stock is cheap or
    expensive relative to this range.

    v02: Added a condition for stop loss: abs(change) > %ATR10*2 AND change < 0
    """
    if 'Datetime' not in df.columns.tolist():
        df['Datetime'] = pd.to_datetime(df['Date'])

    # For stop loss
    df = percental_atr(df, 10)
    df['ROC'] = ((df['Close'] - df.shift(1)['Close'])/df.shift(1)['Close'])*100.0

    days_back_list = [5, 9, 20, 50, 100, 200]

    i = max(days_back_list)
    long_position = False
    tp = None
    sl = None
    cap = 100.0
    trades = []

    while i < len(df):

        if not long_position:
            price_range = []
            for days_back in days_back_list:

                start_date = df.iloc[i]['Datetime'] - relativedelta(days=days_back)
                end_date = df.iloc[i]['Datetime']
                sample_df = df.loc[(df['Datetime'] >= start_date) & (df['Datetime'] <= end_date)].copy().reset_index().drop(columns=['index'])

                prices = []

                for row in range(len(sample_df)):
                    high = sample_df.iloc[row]['High']
                    low = sample_df.iloc[row]['Low']
                    prices = prices + list(np.arange(low, high, .01))

                prices = sorted(prices)

                bin_width = freedman_bin_width(prices)
                nbins = int(np.ceil((np.max(prices) - np.min(prices)) / bin_width))
                bins = np.linspace(np.floor(min(prices)),
                                   np.ceil(max(prices)),
                                   nbins)

                try:
                    occurrences, price_ranges = np.histogram(prices, bins)
                except ValueError as e:
                    print(e)
                    print(f'min ceil: {np.floor(min(prices))} max floor: {np.ceil(max(prices))} nbins: {nbins}')
                    print(bins)
                    exit()

                histogram_dict = {}
                for j in range(len(occurrences)):
                    histogram_dict[occurrences[j]] = (round(price_ranges[j], 2), round(price_ranges[j + 1], 2))

                price_range = price_range + list(histogram_dict[max(occurrences)])

            if min(price_range) > df.iloc[i]['Close']:
                enter_price = df.shift(-1).iloc[i]['Open']
                enter_date = df.shift(-1).iloc[i]['Date']
                enter_datetime = df.shift(-1).iloc[i]['Datetime']
                tp = np.mean(price_range)
                sl = enter_price*0.9
                max_histogram_range = max(price_range)
                min_histogram_range = min(price_range)
                long_position = True
                i += 1

        else:
            if tp < df.iloc[i]['High']:
                if tp < df.iloc[i]['Open']:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = tp
                exit_date = df.iloc[i]['Date']
                exit_datetime = df.iloc[i]['Datetime']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = df.loc[(df['Datetime'] >= enter_datetime) &
                (df['Datetime'] <= exit_datetime)].copy().reset_index()
                period_max = period_df['High'].max()
                period_max_date = period_df.iloc[period_df['High'].idxmax()]['Date']
                period_min = period_df['High'].min()
                period_min_date = period_df.iloc[period_df['High'].idxmin()]['Date']
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': enter_price < exit_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'histogram_range_max': max_histogram_range,
                              'histogram_range_min': min_histogram_range,
                              'period_max': period_max,
                              'period_max_date': period_max_date,
                              'period_min': period_min,
                              'period_min_date': period_min_date}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False

            elif sl > df.iloc[i]['Low']:
                if sl > df.iloc[i]['Open']:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = sl
                exit_date = df.iloc[i]['Date']
                exit_datetime = df.iloc[i]['Datetime']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = df.loc[(df['Datetime'] >= enter_datetime) &
                                   (df['Datetime'] <= exit_datetime)].copy().reset_index()
                period_max = period_df['High'].max()
                period_max_date = period_df.iloc[period_df['High'].idxmax()]['Date']
                period_min = period_df['High'].min()
                period_min_date = period_df.iloc[period_df['High'].idxmin()]['Date']
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': enter_price < exit_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'histogram_range_max': max_histogram_range,
                              'histogram_range_min': min_histogram_range,
                              'period_max': period_max,
                              'period_max_date': period_max_date,
                              'period_min': period_min,
                              'period_min_date': period_min_date}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False

            elif abs(df.iloc[i]['ROC']) > df.iloc[i]['%ATR10']*2 and df.iloc[i]['ROC'] < 0:
                i += 1
                exit_price = df.iloc[i]['Open']
                exit_date = df.iloc[i]['Date']
                exit_datetime = df.iloc[i]['Datetime']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = df.loc[(df['Datetime'] >= enter_datetime) &
                                   (df['Datetime'] <= exit_datetime)].copy().reset_index()
                period_max = period_df['High'].max()
                period_max_date = period_df.iloc[period_df['High'].idxmax()]['Date']
                period_min = period_df['High'].min()
                period_min_date = period_df.iloc[period_df['High'].idxmin()]['Date']
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': enter_price < exit_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'histogram_range_max': max_histogram_range,
                              'histogram_range_min': min_histogram_range,
                              'period_max': period_max,
                              'period_max_date': period_max_date,
                              'period_min': period_min,
                              'period_min_date': period_min_date}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False

        i += 1
    print(ticker, cap)
    return trades, cap


def histogram_trading_v_0_3(ticker, df):
    """
    For each period I will find the most fair price, i.e. the price that was traded the most
    Those prices (from all the periods) will create a kind of 'fair price range' which can help me decide if the stock
    is cheap or expensive relative to this range.

    v03: Added williams R% for each of the periods. This is so I will be able to check if there is a relation between
    the losses and the level of the entrance price R%. For example: I noticed a lot of successive losses within couple
    days. I assume that the entrance price in those trades has very low R% (I'd say <-90%).

    Update: The Williams R% values are not so different between winnning and losing trades. This makes sense. Just
    because the price is super low doesn't mean it can't go up from there.

    I have another thought: I will try to prevent entering trades where the market is volatile, which can translate
    to the %ATR. The assumption is that whenever the %ATR is too big, there is either speculation going on (i.e.
    short squeeze, super aggressive buy which can translate to extreme sell afterwards.
    For now I will only log the %ATR for each of the days and see if there is a correlation between high %ATR value
    and losing trade.

    Update: The %ATR thing looks interesting. I think I can get to higher winning rate if I will limit the entrance
    %ATR to be max. 5. However, that means I will also lose the most profitable trades. So for that I will
    add the ROC for each period. Maybe I can cross it with %ATR to classify the profitable trades.

    Update: I do get to a higher winning rate by limiting the ATR value (81%), but the high profits are cut.
    I went through the data and noticed an awful period of successive losses - which happened during the COVID-19
    crash. So I was thinking using the ^VIX index in order to "check the market waters" and see what is the overall
    sentiment. Basically, it looks as if the ^VIX goes up, there are more losses, and if it goes down - there are
    more winners. I will try to use EMA20 & LinReg10 to measure the ^VIX trend. if LinReg10 > EMA20 - exit trade
    and don't enter new ones, else - as usual.
    """
    if 'Datetime' not in df.columns.tolist():
        df['Datetime'] = pd.to_datetime(df['Date'])

    # For stop loss
    df['ROC'] = ((df['Close'] - df.shift(1)['Close'])/df.shift(1)['Close'])*100.0

    days_back_list = [5, 9, 20, 50, 100, 200]

    for days_back in days_back_list:
        df = percental_atr(df, days_back)
        df = rate_of_change(df, days_back)

    i = max(days_back_list)
    long_position = False
    tp = None
    sl = None
    cap = 100.0
    trades = []

    while i < (len(df) - 1):

        if not long_position:
            price_range = []
            for days_back in days_back_list:

                start_date = df.shift(days_back).iloc[i]['Datetime']
                end_date = df.iloc[i]['Datetime']
                sample_df = df.loc[(df['Datetime'] >= start_date) & (df['Datetime'] <= end_date)].copy().reset_index().drop(columns=['index'])

                prices = []

                for row in range(len(sample_df)):
                    high = sample_df.iloc[row]['High']
                    low = sample_df.iloc[row]['Low']
                    prices = prices + list(np.arange(low, high, .01))

                prices = sorted(prices)

                bin_width = freedman_bin_width(prices)
                nbins = int(np.ceil((np.max(prices) - np.min(prices)) / bin_width))
                bins = np.linspace(np.floor(min(prices)),
                                   np.ceil(max(prices)),
                                   nbins)

                try:
                    occurrences, price_ranges = np.histogram(prices, bins)
                except ValueError as e:
                    print(e)
                    print(f'min ceil: {np.floor(min(prices))} max floor: {np.ceil(max(prices))} nbins: {nbins}')
                    print(bins)
                    exit()

                histogram_dict = {}
                for j in range(len(occurrences)):
                    histogram_dict[occurrences[j]] = (round(price_ranges[j], 2), round(price_ranges[j + 1], 2))

                price_range = price_range + list(histogram_dict[max(occurrences)])

            if min(price_range) > df.iloc[i]['Close']:
                enter_price = df.shift(-1).iloc[i]['Open']
                enter_date = df.shift(-1).iloc[i]['Date']
                enter_datetime = df.shift(-1).iloc[i]['Datetime']
                atr_roc_dict = {}
                for days_back in days_back_list:
                    atr_roc_dict[f'%ATR{days_back}'] = df.iloc[i][f'%ATR{days_back}']
                    atr_roc_dict[f'ROC{days_back}'] = df.iloc[i][f'ROC{days_back}']
                tp = np.mean(price_range)
                sl = enter_price*0.9
                max_histogram_range = max(price_range)
                min_histogram_range = min(price_range)
                long_position = True
                i += 1

        else:
            if tp < df.iloc[i]['High']:
                if tp < df.iloc[i]['Open']:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = tp
                exit_date = df.iloc[i]['Date']
                exit_datetime = df.iloc[i]['Datetime']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = df.loc[(df['Datetime'] >= enter_datetime) &
                (df['Datetime'] <= exit_datetime)].copy().reset_index()
                period_max = period_df['High'].max()
                period_max_date = period_df.iloc[period_df['High'].idxmax()]['Date']
                period_min = period_df['High'].min()
                period_min_date = period_df.iloc[period_df['High'].idxmin()]['Date']
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': enter_price < exit_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'histogram_range_max': max_histogram_range,
                              'histogram_range_min': min_histogram_range,
                              'period_max': period_max,
                              'period_max_date': period_max_date,
                              'period_min': period_min,
                              'period_min_date': period_min_date}
                trade_dict.update(atr_roc_dict)
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False

            elif sl > df.iloc[i]['Low']:
                if sl > df.iloc[i]['Open']:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = sl
                exit_date = df.iloc[i]['Date']
                exit_datetime = df.iloc[i]['Datetime']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = df.loc[(df['Datetime'] >= enter_datetime) &
                                   (df['Datetime'] <= exit_datetime)].copy().reset_index()
                period_max = period_df['High'].max()
                period_max_date = period_df.iloc[period_df['High'].idxmax()]['Date']
                period_min = period_df['High'].min()
                period_min_date = period_df.iloc[period_df['High'].idxmin()]['Date']
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': enter_price < exit_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'histogram_range_max': max_histogram_range,
                              'histogram_range_min': min_histogram_range,
                              'period_max': period_max,
                              'period_max_date': period_max_date,
                              'period_min': period_min,
                              'period_min_date': period_min_date}
                trade_dict.update(atr_roc_dict)
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False

            elif abs(df.iloc[i]['ROC']) > df.iloc[i]['%ATR9']*2 and df.iloc[i]['ROC'] < 0:
                i += 1
                exit_price = df.iloc[i]['Open']
                exit_date = df.iloc[i]['Date']
                exit_datetime = df.iloc[i]['Datetime']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = df.loc[(df['Datetime'] >= enter_datetime) &
                                   (df['Datetime'] <= exit_datetime)].copy().reset_index()
                period_max = period_df['High'].max()
                period_max_date = period_df.iloc[period_df['High'].idxmax()]['Date']
                period_min = period_df['High'].min()
                period_min_date = period_df.iloc[period_df['High'].idxmin()]['Date']
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': enter_price < exit_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'histogram_range_max': max_histogram_range,
                              'histogram_range_min': min_histogram_range,
                              'period_max': period_max,
                              'period_max_date': period_max_date,
                              'period_min': period_min,
                              'period_min_date': period_min_date}
                trade_dict.update(atr_roc_dict)
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False

        i += 1
    print(ticker, cap)
    return trades, cap


def histogram_trading_v_0_4(ticker, df, vix_df):
    """
    For each period I will find the most fair price, i.e. the price that was traded the most
    Those prices (from all the periods) will create a kind of 'fair price range' which can help me decide if the stock
    is cheap or expensive relative to this range.

    v03: Added williams R% for each of the periods. This is so I will be able to check if there is a relation between
    the losses and the level of the entrance price R%. For example: I noticed a lot of successive losses within couple
    days. I assume that the entrance price in those trades has very low R% (I'd say <-90%).

    Update: The Williams R% values are not so different between winnning and losing trades. This makes sense. Just
    because the price is super low doesn't mean it can't go up from there.

    I have another thought: I will try to prevent entering trades where the market is volatile, which can translate
    to the %ATR. The assumption is that whenever the %ATR is too big, there is either speculation going on (i.e.
    short squeeze, super aggressive buy which can translate to extreme sell afterwards.
    For now I will only log the %ATR for each of the days and see if there is a correlation between high %ATR value
    and losing trade.

    Update: The %ATR thing looks interesting. I think I can get to higher winning rate if I will limit the entrance
    %ATR to be max. 5. However, that means I will also lose the most profitable trades. So for that I will
    add the ROC for each period. Maybe I can cross it with %ATR to classify the profitable trades.

    Update: I do get to a higher winning rate by limiting the ATR value (81%), but the high profits are cut.
    I went through the data and noticed an awful period of successive losses - which happened during the COVID-19
    crash. So I was thinking using the ^VIX index in order to "check the market waters" and see what is the overall
    sentiment. Basically, it looks as if the ^VIX goes up, there are more losses, and if it goes down - there are
    more winners. I will try to use EMA20 & LinReg10 to measure the ^VIX trend. if LinReg10 > EMA20 - exit trade
    and don't enter new ones, else - as usual.
    """
    if 'Date' not in df.columns.tolist():
        df.reset_index(inplace=True)
    if 'Datetime' not in df.columns.tolist():
        df['Datetime'] = pd.to_datetime(df['Date'])

    if 'Date' not in vix_df.columns.tolist():
        vix_df.reset_index(inplace=True)
    if 'Datetime' not in vix_df.columns.tolist():
        vix_df['Datetime'] = pd.to_datetime(vix_df['Date'])

    # Matching dataframes dates
    vix_start_date = datetime.strptime(str(vix_df.iloc[0]['Date'])[:10], '%Y-%m-%d')
    vix_end_date = datetime.strptime(str(vix_df.iloc[-1]['Date'])[:10], '%Y-%m-%d')
    stock_start_date = datetime.strptime(str(df.iloc[0]['Date'])[:10], '%Y-%m-%d')
    stock_end_date = datetime.strptime(str(df.iloc[-1]['Date'])[:10], '%Y-%m-%d')

    if stock_start_date != vix_start_date:
        if stock_start_date > vix_start_date:
            vix_df = vix_df.loc[vix_df['Datetime'] >= stock_start_date].copy()
        else:
            df = df.loc[df['Datetime'] >= vix_start_date].copy()

    if stock_end_date != vix_end_date:
        if stock_end_date > vix_end_date:
            df = df.loc[df['Datetime'] <= vix_end_date]
        else:
            vix_df = vix_df.loc[vix_df['Datetime'] <= stock_end_date]

    if len(df) != len(vix_df):
        print('lens match but still different dataframe size')
        exit()

    vix_df['linreg10'] = rolling_ols(vix_df, 'Close', 10)
    vix_df = exponential_moving_average(vix_df, 'Close', 20)

    vix_df['sentiment'] = np.where(vix_df['linreg10'] < vix_df['EMA20'], 'GREED', 'FEAR')

    # For stop loss
    df['ROC'] = ((df['Close'] - df.shift(1)['Close'])/df.shift(1)['Close'])*100.0

    days_back_list = [5, 9, 20, 50, 100, 200]

    for days_back in days_back_list:
        df = percental_atr(df, days_back)
        df = rate_of_change(df, days_back)

    i = max(days_back_list)
    long_position = False
    tp = None
    sl = None
    cap = 100.0
    trades = []

    while i < (len(df) - 1):

        if not long_position:
            price_range = []
            for days_back in days_back_list:

                start_date = df.shift(days_back).iloc[i]['Datetime']
                end_date = df.iloc[i]['Datetime']
                sample_df = df.loc[(df['Datetime'] >= start_date) & (df['Datetime'] <= end_date)].copy().reset_index().drop(columns=['index'])

                prices = []

                for row in range(len(sample_df)):
                    high = sample_df.iloc[row]['High']
                    low = sample_df.iloc[row]['Low']
                    prices = prices + list(np.arange(low, high, .01))

                prices = sorted(prices)

                bin_width = freedman_bin_width(prices)
                nbins = int(np.ceil((np.max(prices) - np.min(prices)) / bin_width))
                bins = np.linspace(np.floor(min(prices)),
                                   np.ceil(max(prices)),
                                   nbins)

                try:
                    occurrences, price_ranges = np.histogram(prices, bins)
                except ValueError as e:
                    print(e)
                    print(f'min ceil: {np.floor(min(prices))} max floor: {np.ceil(max(prices))} nbins: {nbins}')
                    print(bins)
                    exit()

                histogram_dict = {}
                for j in range(len(occurrences)):
                    histogram_dict[occurrences[j]] = (round(price_ranges[j], 2), round(price_ranges[j + 1], 2))

                price_range = price_range + list(histogram_dict[max(occurrences)])

            if min(price_range) > df.iloc[i]['Close'] and vix_df.iloc[i]['EMA20'] > vix_df.iloc[i]['linreg10']:
                enter_price = df.shift(-1).iloc[i]['Open']
                enter_date = df.shift(-1).iloc[i]['Date']
                enter_datetime = df.shift(-1).iloc[i]['Datetime']
                atr_roc_dict = {}
                for days_back in days_back_list:
                    atr_roc_dict[f'%ATR{days_back}'] = df.iloc[i][f'%ATR{days_back}']
                    atr_roc_dict[f'ROC{days_back}'] = df.iloc[i][f'ROC{days_back}']
                tp = np.mean(price_range)
                sl = enter_price*0.9
                max_histogram_range = max(price_range)
                min_histogram_range = min(price_range)
                long_position = True
                i += 1

        else:
            if tp < df.iloc[i]['High']:
                if tp < df.iloc[i]['Open']:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = tp
                exit_date = df.iloc[i]['Date']
                exit_datetime = df.iloc[i]['Datetime']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = df.loc[(df['Datetime'] >= enter_datetime) &
                (df['Datetime'] <= exit_datetime)].copy().reset_index()
                period_max = period_df['High'].max()
                period_max_date = period_df.iloc[period_df['High'].idxmax()]['Date']
                period_min = period_df['High'].min()
                period_min_date = period_df.iloc[period_df['High'].idxmin()]['Date']
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': enter_price < exit_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'histogram_range_max': max_histogram_range,
                              'histogram_range_min': min_histogram_range,
                              'period_max': period_max,
                              'period_max_date': period_max_date,
                              'period_min': period_min,
                              'period_min_date': period_min_date}
                trade_dict.update(atr_roc_dict)
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False

            elif sl > df.iloc[i]['Low']:
                if sl > df.iloc[i]['Open']:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = sl
                exit_date = df.iloc[i]['Date']
                exit_datetime = df.iloc[i]['Datetime']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = df.loc[(df['Datetime'] >= enter_datetime) &
                                   (df['Datetime'] <= exit_datetime)].copy().reset_index()
                period_max = period_df['High'].max()
                period_max_date = period_df.iloc[period_df['High'].idxmax()]['Date']
                period_min = period_df['High'].min()
                period_min_date = period_df.iloc[period_df['High'].idxmin()]['Date']
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': enter_price < exit_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'histogram_range_max': max_histogram_range,
                              'histogram_range_min': min_histogram_range,
                              'period_max': period_max,
                              'period_max_date': period_max_date,
                              'period_min': period_min,
                              'period_min_date': period_min_date}
                trade_dict.update(atr_roc_dict)
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False

            elif vix_df.iloc[i]['EMA20'] < vix_df.iloc[i]['linreg10']:
                i += 1
                exit_price = df.iloc[i]['Open']
                exit_date = df.iloc[i]['Date']
                exit_datetime = df.iloc[i]['Datetime']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = df.loc[(df['Datetime'] >= enter_datetime) &
                                   (df['Datetime'] <= exit_datetime)].copy().reset_index()
                period_max = period_df['High'].max()
                period_max_date = period_df.iloc[period_df['High'].idxmax()]['Date']
                period_min = period_df['High'].min()
                period_min_date = period_df.iloc[period_df['High'].idxmin()]['Date']
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': enter_price < exit_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'histogram_range_max': max_histogram_range,
                              'histogram_range_min': min_histogram_range,
                              'period_max': period_max,
                              'period_max_date': period_max_date,
                              'period_min': period_min,
                              'period_min_date': period_min_date}
                trade_dict.update(atr_roc_dict)
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False

        i += 1
    print(ticker, cap)
    return trades, cap


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import time

    start_time = time.time()

    # tickers = list(set(get_all_snp_stocks() + get_all_nasdaq_100_stocks() + get_all_dow_jones_industrial_stocks() + ['SPY']))
    tickers = get_all_nasdaq_100_stocks()

    if len(tickers) < 102:
        print(len(tickers))
        print('exited')
        exit()
    # tickers = ['SPY']
    ticker_returns = []
    all_trades = []

    for i, ticker in enumerate(tickers):
        try:
            vix_df = pd.read_csv(download_stock_day('^VIX'))
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError as e:
            print(e)
            continue
        print(f'{i}/{len(tickers)}')
        df = df[-1008:]
        vix_df = vix_df[-1008:]
        trades, final_cap = histogram_trading_v_0_4(ticker, df, vix_df)
        buy_and_hold = ((df.iloc[-1]["Close"])/df.iloc[0]["Close"])*100.0
        print(f'buy & hold: {buy_and_hold}')
        all_trades = all_trades + trades
        ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0, 'buy&hold': buy_and_hold})
        pd.DataFrame(all_trades).to_csv(
            save_under_results_path(f'histogram_trading_v_0_4_nasdaq100_all_trades.csv'))
        pd.DataFrame(ticker_returns).to_csv(
            save_under_results_path('histogram_trading_v_0_4_nasdaq100_ticker_returns.csv'))

    print(time.time() - start_time)
