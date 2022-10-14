"""
Calculating the trendlines using detectors/trendlines/both_trendlines function.
If price opened above the upper trend-line - buy immediately & sell at the next candle open.
If price opened below the lower trend-line - short immediately & cover at the next candle open.

One thing/parameter to consider: For how long the trend-line should be used?
Or, maybe filter trendlines according to % from current (Closing) price
"""
import numpy as np
import pandas as pd
from detectors.trendlines import upper_trendline
from utils.download_stock_csvs import download_stock_day
from indicators.my_indicators import my_rsi


def open_breached_upper_trendline_trading(ticker, backcandles=100, max_candles_after=50, line_candle_max_ratio=np.inf):

    df = pd.read_csv(download_stock_day(ticker)).reset_index()
    i = backcandles + int(np.floor(backcandles*0.9))

    upper_trendline_detected = False
    upper_trendline_breached_by_high = 0
    upper_trendline_breached_by_close = 0
    upper_counter = 0
    long = False

    trades = []
    cap = 100.0
    while i < (len(df) - max_candles_after):
        if long:
            exit_price = df.iloc[i]['Open']
            exit_date = df.iloc[i]['Date']
            change = (exit_price/enter_price - 1)*100.0
            all_candles_change = (df.iloc[i]['Open']/df.shift(backcandlesopt+upper_counter).iloc[i]['Close'] - 1)*100.0
            period_df = df[i-backcandlesopt-upper_counter:i-1].copy()
            period_df['trendline'] = period_df.index*slmax+intercmax
            avg_distance_pct = ((period_df['trendline']/period_df['High'] - 1)*100.0).mean()
            max_distance_pct = ((period_df['trendline']/period_df['High'] - 1)*100.0).max()
            cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
            trade_dict = {'symbol': ticker,
                          'type': 'long',
                          'enter_date': enter_date,
                          'enter_price': enter_price,
                          'exit_date': exit_date,
                          'exit_price': exit_price,
                          'win': exit_price > enter_price,
                          'change%': change,
                          'slope': slmax,
                          'backcandles': backcandlesopt,
                          'trenline_detected_candle_%': detected_candle_trendline_pct,
                          'candles_after': upper_counter,
                          'close_breached_before': upper_trendline_breached_by_close,
                          'high_breached_before': upper_trendline_breached_by_high,
                          'open%trendline': pct_above_trenline,
                          'backcandkes_change%': backcandles_change,
                          'all_candles_change%': all_candles_change,
                          'avg_distance%': avg_distance_pct,
                          'max_distance%': max_distance_pct}
            print(trade_dict)
            trades.append(trade_dict)
            long = False
            upper_trendline_detected = False
            upper_trendline_breached_by_close = 0
            upper_trendline_breached_by_high = 0
            upper_counter = 0
        elif upper_trendline_detected:
            upper_counter += 1
            if (slmax*i+intercmax) < df.iloc[i]['Close'] and not (slmax*i+intercmax) < df.iloc[i]['Open']:
                upper_trendline_breached_by_close += 1
                upper_trendline_breached_by_high += 1
            elif (slmax*i+intercmax) < df.iloc[i]['High'] and not (slmax*i+intercmax) < df.iloc[i]['Open']:
                upper_trendline_breached_by_high += 1
            if (slmax*i+intercmax) < df.iloc[i]['Open']:
                long = True
                enter_price = df.iloc[i]['Open']
                enter_date = df.iloc[i]['Date']
                pct_above_trenline = (df.iloc[i]['Open']/(slmax*i+intercmax) - 1)*100.0
            elif upper_counter >= max_candles_after:
                upper_trendline_detected = False
                upper_trendline_breached_by_close = 0
                upper_trendline_breached_by_high = 0
                upper_counter = 0
        else:
            slmax, intercmax, backcandlesopt = upper_trendline(df, i, backcandles=backcandles)
            if slmax is not None:
                if (slmax*i+intercmax)/(df.iloc[i]['High']) < line_candle_max_ratio and (slmax*i+intercmax) > df.iloc[i]['High']:
                    upper_trendline_detected = True
                    backcandles_change = (df.iloc[i]['Close']/df.shift(backcandlesopt).iloc[i]['Close'] - 1)*100.0
                    detected_candle_trendline_pct = ((slmax * i + intercmax)/df.iloc[i]['High'] - 1) * 100.0
        i += 1

    print(ticker, cap, len(trades))
    return trades, cap


def open_breached_upper_trendline_trading_v2(ticker, backcandles=100, max_candles_after=50, line_candle_max_ratio=1.2):

    df = pd.read_csv(download_stock_day(ticker)).reset_index()
    i = backcandles + int(np.floor(backcandles*0.9))

    upper_trendline_detected = False
    upper_trendline_breached_by_high = 0
    upper_trendline_breached_by_close = 0
    upper_counter = 0
    long = False

    trades = []
    cap = 100.0
    while i < (len(df) - max_candles_after):
        if long:
            exit_price = df.iloc[i]['Open']
            exit_date = df.iloc[i]['Date']
            change = (exit_price/enter_price - 1)*100.0
            all_candles_change = (df.iloc[i]['Open']/df.shift(backcandlesopt+upper_counter).iloc[i]['Close'] - 1)*100.0
            period_df = df[i-backcandlesopt-upper_counter:i-1].copy()
            period_df['trendline'] = period_df.index*slmax+intercmax
            avg_distance_pct = ((period_df['trendline']/period_df['High'] - 1)*100.0).mean()
            max_distance_pct = ((period_df['trendline']/period_df['High'] - 1)*100.0).max()
            cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
            trade_dict = {'symbol': ticker,
                          'type': 'long',
                          'enter_date': enter_date,
                          'enter_price': enter_price,
                          'exit_date': exit_date,
                          'exit_price': exit_price,
                          'win': exit_price > enter_price,
                          'change%': change,
                          'slope': slmax,
                          'backcandles': backcandlesopt,
                          'candles_after': upper_counter,
                          'close_breached_before': upper_trendline_breached_by_close,
                          'high_breached_before': upper_trendline_breached_by_high,
                          'open%trendline': pct_above_trenline,
                          'backcandkes_change%': backcandles_change,
                          'all_candles_change%': all_candles_change,
                          'avg_distance%': avg_distance_pct,
                          'max_distance%': max_distance_pct}
            print(trade_dict)
            trades.append(trade_dict)
            long = False
            upper_trendline_detected = False
            upper_trendline_breached_by_close = 0
            upper_trendline_breached_by_high = 0
            upper_counter = 0
        elif upper_trendline_detected:
            upper_counter += 1
            if (slmax*i+intercmax) < df.iloc[i]['Close'] and not (slmax*i+intercmax) < df.iloc[i]['Open']:
                upper_trendline_breached_by_close += 1
                upper_trendline_breached_by_high += 1
            elif (slmax*i+intercmax) < df.iloc[i]['High'] and not (slmax*i+intercmax) < df.iloc[i]['Open']:
                upper_trendline_breached_by_high += 1
            if (slmax*i+intercmax) < df.iloc[i]['Open']:
                long = True
                enter_price = df.iloc[i]['Open']
                enter_date = df.iloc[i]['Date']
                pct_above_trenline = (df.iloc[i]['Open']/(slmax*i+intercmax) - 1)*100.0
            elif upper_counter >= max_candles_after:
                upper_trendline_detected = False
                upper_trendline_breached_by_close = 0
                upper_trendline_breached_by_high = 0
                upper_counter = 0
        else:
            slmax, intercmax, backcandlesopt = upper_trendline(df, i, backcandles=backcandles)
            if slmax is not None:
                if (slmax*i+intercmax)/(df.iloc[i]['High']) < line_candle_max_ratio:
                    upper_trendline_detected = True
                    backcandles_change = (df.iloc[i]['Close']/df.shift(backcandlesopt).iloc[i]['Close'] - 1)*100.0
        i += 1

    print(ticker, cap, len(trades))
    return trades, cap


if __name__ == '__main__':
    from utils.in_sample_tickers import *
    from utils.paths import save_under_results_path
    import random
    import pathos

    # ticker = random.choice(IN_SAMPLE_TICKERS)
    # ticker = 'ADBE'
    # ticker = 'VRSN'

    # trades, final_cap = open_breached_upper_trendline_trading(ticker, line_candle_max_ratio=np.inf)
    # pd.DataFrame(trades).to_csv(save_under_results_path(f'open_breached_upper_trendline_trading_{ticker}_results.csv'))

    # tickers = IN_SAMPLE_TICKERS
    # all_trades = []
    # with pathos.multiprocessing.ProcessPool() as executor:
    #     results = executor.map(open_breached_upper_trendline_trading, tickers)
    #
    #     for result in results:
    #         all_trades = all_trades + result[0]
    #
    # pd.DataFrame(all_trades).to_csv(save_under_results_path(f'open_breached_upper_trendline_trading_max_candles_after_50_all_trades.csv'))
