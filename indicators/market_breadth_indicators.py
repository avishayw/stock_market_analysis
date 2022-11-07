import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.download_stock_csvs import download_stock_day
import pathos
from indicators.momentum_indicators import rsi


def above_sma(tickers, sma_period, date_str, print_debug=False):

    def ticker_is_above_sma(ticker):
        if print_debug:
            print(f'Checking on {ticker}...')
        try:
            df = pd.read_csv(download_stock_day(ticker)).reset_index()
            df['Date'] = df['Date'].map(lambda x: str(x).split(' ')[0])
            df['Datetime'] = pd.to_datetime(df['Date'])
            df = df.loc[df['Datetime'] <= date].copy()
            if len(df) < sma_period+1 or df.iloc[-1]['Datetime'] < date_validation:
                if print_debug:
                    print(f'{ticker} dataframe is invalid')
                return None
            else:
                df['SMA'] = df['Close'].rolling(sma_period).mean()
                if df.iloc[-1]['Close'] > df.iloc[-1]['SMA']:
                    if print_debug:
                        print(f'{ticker} above SMA')
                    return True
                else:
                    if print_debug:
                        print(f'{ticker} below SMA')
                    return False
        except ValueError:
            if print_debug:
                print(f'No dataframe for {ticker}')
            pass

    date = datetime.strptime(date_str, '%Y-%m-%d')
    date_validation = date - relativedelta(days=5)
    total_valid_tickers = 0
    tickers_above_sma = 0

    with pathos.multiprocessing.ProcessPool() as executor:
        results = executor.map(ticker_is_above_sma, tickers)

        for result in results:
            if result is not None:
                total_valid_tickers += 1
                if result:
                    tickers_above_sma +=1

    if total_valid_tickers > 0:
        return tickers_above_sma/total_valid_tickers
    else:
        return None


def rsi_above_threshold(tickers, rsi_period, rsi_th, date_str, print_debug=False):

    def ticker_rsi_is_above_55(ticker):
        if print_debug:
            print(f'Checking on {ticker}...')
        try:
            df = pd.read_csv(download_stock_day(ticker)).reset_index()
            df['Date'] = df['Date'].map(lambda x: str(x).split(' ')[0])
            df['Datetime'] = pd.to_datetime(df['Date'])
            df = df.loc[df['Datetime'] <= date].copy()
            if len(df) < rsi_period+1 or df.iloc[-1]['Datetime'] < date_validation:
                if print_debug:
                    print(f'{ticker} dataframe is invalid')
                return None
            else:
                df = rsi(df, rsi_period)
                if df.iloc[-1][f'RSI{rsi_period}'] > rsi_th:
                    if print_debug:
                        print(f'{ticker} RSI above {rsi_th}')
                    return True
                else:
                    if print_debug:
                        print(f'{ticker} RSI below {rsi_th}')
                    return False
        except ValueError:
            if print_debug:
                print(f'No dataframe for {ticker}')
            pass

    date = datetime.strptime(date_str, '%Y-%m-%d')
    date_validation = date - relativedelta(days=5)
    total_valid_tickers = 0
    tickers_rsi_above_th = 0

    with pathos.multiprocessing.ProcessPool() as executor:
        results = executor.map(ticker_rsi_is_above_55, tickers)

        for result in results:
            if result is not None:
                total_valid_tickers += 1
                if result:
                    tickers_rsi_above_th +=1

    if total_valid_tickers > 0:
        return tickers_rsi_above_th/total_valid_tickers
    else:
        return None


def periodic_high_low_zone(tickers, period, date_str, zone_ratio=0.2, print_debug=False):

    def ticker_in_high_zone(ticker):
        if print_debug:
            print(f'Checking on {ticker}...')
        try:
            df = pd.read_csv(download_stock_day(ticker)).reset_index()
            df['Date'] = df['Date'].map(lambda x: str(x).split(' ')[0])
            df['Datetime'] = pd.to_datetime(df['Date'])
            df = df.loc[df['Datetime'] <= date].copy()
            if len(df) < period+1 or df.iloc[-1]['Datetime'] < date_validation:
                if print_debug:
                    print(f'{ticker} dataframe is invalid')
                return None
            else:
                df['period_high'] = df['High'].rolling(period).max()
                df['period_low'] = df['Low'].rolling(period).min()
                if df.iloc[-1]['Close'] > df.iloc[-1]['period_high']*(1-zone_ratio):
                    if print_debug:
                        print(f'{ticker} in periodic high zone')
                    return True
                elif df.iloc[-1]['Close'] < df.iloc[-1]['period_low']*(1+zone_ratio):
                    if print_debug:
                        print(f'{ticker} in periodic low zone')
                    return False
                else:
                    if print_debug:
                        print(f'{ticker} outside of both high and low zones')
                    return None
        except ValueError:
            if print_debug:
                print(f'No dataframe for {ticker}')
            pass

    date = datetime.strptime(date_str, '%Y-%m-%d')
    date_validation = date - relativedelta(days=5)
    total_tickers_in_zone = 0
    tickers_in_high_zone = 0

    with pathos.multiprocessing.ProcessPool() as executor:
        results = executor.map(ticker_in_high_zone, tickers)

        for result in results:
            if result is not None:
                total_tickers_in_zone += 1
                if result:
                    tickers_in_high_zone += 1

    if total_tickers_in_zone > 0:
        return tickers_in_high_zone/total_tickers_in_zone
    else:
        return None


if __name__ == '__main__':
    from utils.get_all_stocks import get_all_snp_stocks
    from plotting.candlestick_chart import multiple_windows_chart
    from utils.paths import save_under_results_path

    tickers = get_all_snp_stocks()
    spy = pd.read_csv(download_stock_day('SPY')).reset_index()[-756:]
    # TODO: remove test
    spy.to_csv(save_under_results_path('spy.csv'))
    start_idx = spy.index[0]

    for i in range(len(spy)):
        spy_date = str(spy.iloc[i]['Date']).split(' ')[0]
        spy.loc[start_idx + i, 'pct_stocks_above_sma'] = above_sma(tickers, 50, spy_date)
        spy.loc[start_idx + i, 'pct_stocks_above_rsi_th'] = rsi_above_threshold(tickers, 50, 55, spy_date)
        spy.loc[start_idx + i, 'pct_stocks_in_high_zone'] = periodic_high_low_zone(tickers, 50, spy_date)

    spy.to_csv(save_under_results_path('spy_market_breadth.csv'))

    chart_dict = {(2, 'Market Breadth'): ['pct_stocks_above_sma', 'pct_stocks_above_rsi_th', 'pct_stocks_in_high_zone']}
    fig = multiple_windows_chart('SPY', spy, chart_dict)
    fig.show()

    # above_sma_pct = above_sma(tickers, 50, '2021-12-27')
    # above_rsi_th_pct = rsi_above_threshold(tickers, 50, 55, '2021-12-27')
    # in_high_zone = periodic_high_low_zone(tickers, 50, '2022-11-03', print_debug=True)
    # print(above_sma_pct, above_rsi_th_pct, in_high_zone)
    # print('avg', (above_sma_pct + above_rsi_th_pct + in_high_zone)/3)
