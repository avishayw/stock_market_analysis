import numpy as np
import pandas as pd
from utils.download_stock_csvs import download_stock_day
from sklearn.linear_model import LinearRegression
import pathos
from itertools import repeat
from utils.paths import save_under_results_path


def channel_mid_trading(ticker, inner_safety_margin_ratio=0.15, outer_safety_margin_ratio=0.15):

    def detect_channel_and_trade(df,
                                 candleid,
                                 backcandles=100,
                                 brange=90,
                                 wind=5,
                                 inner_safety_margin_ratio=inner_safety_margin_ratio,
                                 outer_safety_margin_ratio=outer_safety_margin_ratio):


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

            if abs(slmin - slmax) < sldiff:
                sldiff = abs(slmin - slmax)
                optbackcandles = r1
                slminopt = slmin
                slmaxopt = slmax
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
            # print(f'({candleid}/{len(df)}) no trend slope from channel', slmaxopt, slminopt)
            return None

        xxall = np.arange(max(min(xxminopt), min(xxmaxopt)), candleid + 1, 1)
        adjintercmax = (df.High.iloc[xxall] - slope * xxall).max()
        adjintercmin = (df.Low.iloc[xxall] - slope * xxall).min()

        sample_df = df[candleid - optbackcandles:candleid + 1].copy()
        sample_df['high_line'] = sample_df.index * slope + adjintercmax
        sample_df['low_line'] = sample_df.index * slope + adjintercmin
        band = (sample_df['high_line'] - sample_df['low_line']).sum()
        price = (sample_df['High'] - sample_df['Low']).sum()
        price_density = price / band

        x = sample_df.index.to_numpy().reshape(-1, 1)
        y = sample_df['Close'].to_numpy()
        model = LinearRegression()
        try:
            model.fit(x, y)
        except ValueError:
            # print(f'({candleid}/{len(df)}) no fit')
            return None

        slopeols, intercols = model.coef_[0], model.intercept_

        channel_candleid_range = (slope * candleid + adjintercmax) - (slope * candleid + adjintercmin)
        inner_margin = channel_candleid_range * inner_safety_margin_ratio
        outer_margin = channel_candleid_range * outer_safety_margin_ratio
        innermarginintercmax = adjintercmax - inner_margin
        innermarginintercmin = adjintercmin + inner_margin
        outermarginintercmax = adjintercmax + outer_margin
        outermarginintercmin = adjintercmin - outer_margin
        candle_mid = ((slope * candleid + adjintercmax) + (slope * candleid + adjintercmin)) * 0.5
        midinterc = candle_mid - slope * candleid

        channel_df = df[candleid-optbackcandles:].copy()
        channel_df['max_line'] = channel_df.index * slope + adjintercmax
        channel_df['max_line_outer_margin'] = channel_df.index * slope + outermarginintercmax
        channel_df['max_line_inner_margin'] = channel_df.index * slope + innermarginintercmax
        channel_df['min_line'] = channel_df.index * slope + adjintercmin
        channel_df['min_line_outer_margin'] = channel_df.index * slope + outermarginintercmin
        channel_df['min_line_inner_margin'] = channel_df.index * slope + innermarginintercmin
        channel_df['mid_line'] = channel_df.index * slope + midinterc

        # print(f'({candleid}/{len(df)}) channel approved. {optbackcandles} candles back')
        channel_candle_id = candleid
        cap = 100.0
        trades = []
        channel_breached = False
        position = False
        while (not channel_breached) and candleid < len(df)-1:
            candleid += 1

            if direction == 'long':

                if position:
                    if channel_df.loc[candleid, 'High'] > channel_df.loc[candleid, 'mid_line']:
                        exit_price = channel_df.loc[candleid, 'mid_line']
                        exit_date = channel_df.loc[candleid, 'Date']
                        exit_candle_id = candleid
                        change = (exit_price/enter_price - 1)*100.0
                        cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                        trade_dict = {'symbol': ticker,
                                      'type': 'long',
                                      'enter_date': enter_date,
                                      'enter_price': enter_price,
                                      'exit_date': exit_date,
                                      'exit_price': exit_price,
                                      'win': exit_price > enter_price,
                                      'change%': change,
                                      'channel_price_density': price_density,
                                      'slope': slope,
                                      'slmax': slmaxopt,
                                      'slmin': slminopt,
                                      'slols': slopeols,
                                      'channel_candle_id': channel_candle_id,
                                      'channel_candles_back': optbackcandles,
                                      'enter_candle_id': enter_candle_id,
                                      'exit_candle_id': exit_candle_id}
                        # print(trade_dict)
                        trades.append(trade_dict)
                        position = False
                    elif channel_df.loc[candleid, 'Low'] < channel_df.loc[candleid, 'min_line_outer_margin']:
                        exit_price = channel_df.loc[candleid, 'min_line_outer_margin']
                        exit_date = channel_df.loc[candleid, 'Date']
                        exit_candle_id = candleid
                        change = (exit_price / enter_price - 1) * 100.0
                        cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                        trade_dict = {'symbol': ticker,
                                      'type': 'long',
                                      'enter_date': enter_date,
                                      'enter_price': enter_price,
                                      'exit_date': exit_date,
                                      'exit_price': exit_price,
                                      'win': exit_price > enter_price,
                                      'change%': change,
                                      'channel_price_density': price_density,
                                      'slope': slope,
                                      'slmax': slmaxopt,
                                      'slmin': slminopt,
                                      'slols': slopeols,
                                      'channel_candle_id': channel_candle_id,
                                      'channel_candles_back': optbackcandles,
                                      'enter_candle_id': enter_candle_id,
                                      'exit_candle_id': exit_candle_id}
                        # print(trade_dict)
                        trades.append(trade_dict)
                        position = False
                        channel_breached = True

                elif channel_df.loc[candleid, 'Low'] < channel_df.loc[candleid, 'min_line_outer_margin']:
                    # print(f'({candleid}/{len(df)}) Low trend-line was breached')
                    channel_breached = True
                elif channel_df.loc[candleid, 'High'] > channel_df.loc[candleid, 'max_line_outer_margin']:
                    # print(f'({candleid}/{len(df)}) High trend-line was breached')
                    channel_breached = True
                elif (channel_df.loc[candleid, 'Low'] < channel_df.loc[candleid, 'min_line_inner_margin']) and \
                        (channel_df.loc[candleid, 'Close'] > channel_df.loc[candleid, 'min_line_inner_margin']):
                    # print(f'({candleid}/{len(df)}) Entered {direction} position')
                    position = True
                    enter_price = channel_df.loc[candleid, 'min_line_inner_margin']
                    enter_date = channel_df.loc[candleid, 'Date']
                    enter_candle_id = candleid
                elif channel_df.shift(1).loc[candleid, 'Close'] < channel_df.shift(1).loc[candleid, 'min_line_inner_margin'] and \
                        channel_df.loc[candleid, 'High'] > channel_df.loc[candleid, 'min_line_inner_margin']:
                    # print(f'({candleid}/{len(df)}) Entered {direction} position')
                    position = True
                    enter_price = channel_df.loc[candleid, 'min_line_inner_margin']
                    enter_date = channel_df.loc[candleid, 'Date']
                    enter_candle_id = candleid

            elif direction == 'short':

                if position:
                    if channel_df.loc[candleid, 'Low'] < channel_df.loc[candleid, 'mid_line']:
                        # TODO: remove
                        low = channel_df.loc[candleid, 'Low']
                        mid = channel_df.loc[candleid, 'mid_line']
                        ###
                        exit_price = channel_df.loc[candleid, 'mid_line']
                        exit_date = channel_df.loc[candleid, 'Date']
                        exit_candle_id = candleid
                        change = (exit_price/enter_price - 1)*100.0*-1.0
                        cap = cap * (1.0 + ((exit_price - enter_price) / enter_price)*-1.0)
                        trade_dict = {'symbol': ticker,
                                      'type': 'short',
                                      'enter_date': enter_date,
                                      'enter_price': enter_price,
                                      'exit_date': exit_date,
                                      'exit_price': exit_price,
                                      'win': exit_price < enter_price,
                                      'change%': change,
                                      'channel_price_density': price_density,
                                      'slope': slope,
                                      'slmax': slmaxopt,
                                      'slmin': slminopt,
                                      'slols': slopeols,
                                      'channel_candle_id': channel_candle_id,
                                      'channel_candles_back': optbackcandles,
                                      'enter_candle_id': enter_candle_id,
                                      'exit_candle_id': exit_candle_id}
                        # print(trade_dict)
                        trades.append(trade_dict)
                        position = False
                    elif channel_df.loc[candleid, 'High'] > channel_df.loc[candleid, 'max_line_outer_margin']:
                        # TODO: remove
                        high = channel_df.loc[candleid, 'High']
                        mid = channel_df.loc[candleid, 'mid_line']
                        ###
                        exit_price = channel_df.loc[candleid, 'max_line_outer_margin']
                        exit_date = channel_df.loc[candleid, 'Date']
                        exit_candle_id = candleid
                        change = (exit_price / enter_price - 1) * 100.0 * -1.0
                        cap = cap * (1.0 + ((exit_price - enter_price) / enter_price)*-1.0)
                        trade_dict = {'symbol': ticker,
                                      'type': 'short',
                                      'enter_date': enter_date,
                                      'enter_price': enter_price,
                                      'exit_date': exit_date,
                                      'exit_price': exit_price,
                                      'win': exit_price < enter_price,
                                      'change%': change,
                                      'channel_price_density': price_density,
                                      'slope': slope,
                                      'slmax': slmaxopt,
                                      'slmin': slminopt,
                                      'slols': slopeols,
                                      'channel_candle_id': channel_candle_id,
                                      'channel_candles_back': optbackcandles,
                                      'enter_candle_id': enter_candle_id,
                                      'exit_candle_id': exit_candle_id}
                        # print(trade_dict)
                        trades.append(trade_dict)
                        position = False
                        channel_breached = True

                elif channel_df.loc[candleid, 'Low'] < channel_df.loc[candleid, 'min_line_outer_margin']:
                    # print(f'({candleid}/{len(df)}) Low trend-line was breached')
                    return None
                elif channel_df.loc[candleid, 'High'] > channel_df.loc[candleid, 'max_line_outer_margin']:
                    # print(f'({candleid}/{len(df)}) High trend-line was breached')
                    return None
                elif (channel_df.loc[candleid, 'High'] > channel_df.loc[candleid, 'max_line_inner_margin']) and \
                        (channel_df.loc[candleid, 'Close'] < channel_df.loc[candleid, 'max_line_inner_margin']):
                    # print(f'({candleid}/{len(df)}) Entered {direction} position')
                    position = True
                    enter_price = channel_df.loc[candleid, 'max_line_inner_margin']
                    enter_date = channel_df.loc[candleid, 'Date']
                    enter_candle_id = candleid
                elif channel_df.shift(1).loc[candleid, 'Close'] > channel_df.shift(1).loc[candleid, 'max_line_inner_margin'] and \
                        channel_df.loc[candleid, 'Low'] < channel_df.loc[candleid, 'max_line_inner_margin']:
                    # print(f'({candleid}/{len(df)}) Entered {direction} position')
                    position = True
                    enter_price = channel_df.loc[candleid, 'max_line_inner_margin']
                    enter_date = channel_df.loc[candleid, 'Date']
                    enter_candle_id = candleid

        return trades

    df_backup = pd.read_csv(download_stock_day(ticker)).reset_index()
    backcandles = 100
    brange = int(np.floor(backcandles * 0.9))  # should be less than backcandles
    df = df_backup.copy()
    # print(len(df))
    candleids = list(range(backcandles + brange - 1, len(df)))
    # candleids = list(range(15213, 15214))

    # detect_channel_and_trade(df, 15185)

    ticker_trades = []

    with pathos.multiprocessing.ProcessPool() as executor:
        results = executor.map(detect_channel_and_trade, repeat(df), candleids)

        for result in results:
            if result is not None:
                ticker_trades = ticker_trades + result

    return ticker_trades


if __name__ == '__main__':
    import os
    from datetime import datetime
    from utils.in_sample_tickers import *

    tickers = IN_SAMPLE_TICKERS

    for ticker in tickers:
        print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} {ticker}')
        trades = channel_mid_trading(ticker)
        if os.path.exists('channel_midline_trading_all_trades.csv'):
            trades_df = pd.read_csv('channel_midline_trading_all_trades.csv')
            trades_df = trades_df.loc[:, ~trades_df.columns.str.contains('^Unnamed')]
            all_trades = trades_df.to_dict('record')
            all_trades = all_trades + trades
            pd.DataFrame(all_trades).to_csv('channel_midline_trading_all_trades.csv')
        else:
            pd.DataFrame(trades).to_csv('channel_midline_trading_all_trades.csv')

