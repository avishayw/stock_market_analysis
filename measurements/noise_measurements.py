import pandas as pd
import numpy as np


def efficiency_ratio(df, src, period, inplace=True, threshold=None):

    net_change = (df[src] - df.shift(period)[src]).abs()
    change = (df[src] - df.shift(1)[src]).abs()
    sum_of_individual_changes = change.rolling(period).sum()
    er = net_change/sum_of_individual_changes
    if inplace:
        df[f'{src}ER{period}'] = er
        if threshold:
            er_th = np.where(er > threshold, True, False)
            df[f'{src}ER{period}>{threshold}'] = er_th
            return df
        return df
    else:
        if threshold:
            return pd.Series(np.where(er > threshold, True, False))
        else:
            return er


def price_density(df, period, inplace=True, threshold=None):
    highest_high = df['High'].rolling(period).max()
    lowest_low = df['Low'].rolling(period).min()
    box_range = highest_high - lowest_low
    day_range = df['High'] - df['Low']
    sum_of_individual_changes = day_range.rolling(period).sum()
    # density = sum_of_individual_changes/box_range
    density = box_range/sum_of_individual_changes
    if inplace:
        df[f'PriceDensity{period}'] = density
        if threshold:
            density_th = np.where(density > threshold, True, False)
            df[f'PriceDensity{period}>{threshold}'] = density_th
            return df
        return df
    else:
        if threshold:
            return pd.Series(np.where(density > threshold, True, False))
        else:
            return density


def fractal_dimension(df, period, inplace=True, threshold=None):
    dx2 = (1/period)**2
    highest_high = df['High'].rolling(period).max()
    lowest_low = df['Low'].rolling(period).min()
    box_range = highest_high - lowest_low


if __name__ == "__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, \
        get_all_dow_jones_industrial_stocks, get_all_nyse_composite_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    from indicators.momentum_indicators import rate_of_change, simple_moving_average
    from trade_managers._signal_trading_manager import signal_trading_manager_long, signal_trading_manager_short
    import pandas as pd
    import numpy as np
    from datetime import datetime
    import json
    import time
    import yfinance as yf
    import json

    sma1_period = 5
    sma2_period = 20
    sma1_uptrend_roc_period = 5
    sma2_uptrend_roc_period = 5
    sma1_uptrend_roc_th = 3.0
    sma2_uptrend_roc_th = 2.0
    sma1_uptrend_er_th = 0.5
    sma2_uptrend_er_th = 0.5
    sma1_downtrend_roc_period = 5
    sma1_downtrend_roc_th = -3.0
    sma1_downtrend_er_th = 0.2

    dataframe_length = 60

    strategy_name = f'ma_roc_and_efficiency_ratio_trading'
    strategy_parameters = {'sma1_period' : sma1_period,
                           'sma2_period' : sma2_period,
                           'sma1_uptrend_roc_period' : sma1_uptrend_roc_period,
                           'sma2_uptrend_roc_period' : sma2_uptrend_roc_period,
                           'sma1_uptrend_roc_th' : sma1_uptrend_roc_th,
                           'sma2_uptrend_roc_th' : sma2_uptrend_roc_th,
                           'sma1_uptrend_er_th' : sma1_uptrend_er_th,
                           'sma2_uptrend_er_th' : sma2_uptrend_er_th,
                           'sma1_downtrend_roc_period' : sma1_downtrend_roc_period,
                           'sma1_downtrend_roc_th' : sma1_downtrend_roc_th,
                           'sma1_downtrend_er_th' : sma1_downtrend_er_th,
                           'dataframe_length': dataframe_length}

    run_time = datetime.now().strftime('%d-%m-%Y-%H-%M-%S')

    with open(save_under_results_path(f'{strategy_name}_{run_time}.json'), 'w') as f:
        json.dump(strategy_parameters, f, indent=4)

    tickers = list(set(get_all_snp_stocks() + get_all_nasdaq_100_stocks() + get_all_dow_jones_industrial_stocks() + ['SPY'] + get_all_nyse_composite_stocks()))

    all_trades = []
    ticker_returns = []
    # incomplete_trades = []

    for ticker in tickers:
        try:
            # df = pd.read_csv(download_stock_day(ticker)).reset_index()
            df = yf.Ticker(ticker).history(period='max', interval='1d')
            if len(df) > dataframe_length:
                df = df[-dataframe_length:].reset_index()
            else:
                df = df.reset_index()
        except ValueError:
            continue

        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        df = simple_moving_average(df, sma1_period)
        df = simple_moving_average(df, sma2_period)
        df[f'SMA{sma1_period}ROC{sma1_uptrend_roc_period}'] = ((df[f'SMA{sma1_period}'] - df.shift(sma1_uptrend_roc_period)[
            f'SMA{sma1_period}']) /
                                                               df.shift(sma1_uptrend_roc_period)[
                                                                   f'SMA{sma1_period}']) * 100.0
        df[f'SMA{sma1_period}ROC{sma1_downtrend_roc_period}'] = ((df[f'SMA{sma1_period}'] -
                                                                  df.shift(sma1_downtrend_roc_period)[
                                                                      f'SMA{sma1_period}']) /
                                                                 df.shift(sma1_downtrend_roc_period)[
                                                                     f'SMA{sma1_period}']) * 100.0
        df[f'SMA{sma2_period}ROC{sma2_uptrend_roc_period}'] = ((df[f'SMA{sma2_period}'] - df.shift(sma2_uptrend_roc_period)[
            f'SMA{sma2_period}']) /
                                                               df.shift(sma2_uptrend_roc_period)[
                                                                   f'SMA{sma2_period}']) * 100.0
        df[f'SMA{sma1_period}ER'] = efficiency_ratio(df, f'SMA{sma1_period}', sma1_period, inplace=False)
        df[f'SMA{sma2_period}ER'] = efficiency_ratio(df, f'SMA{sma2_period}', sma2_period, inplace=False)

        df['sell_signal'] = np.where((df[f'SMA{sma1_period}ROC{sma1_uptrend_roc_period}'] > sma1_uptrend_roc_th) &
                                    (df[f'SMA{sma2_period}ROC{sma2_uptrend_roc_period}'] > sma2_uptrend_roc_th) &
                                    (df[f'SMA{sma1_period}ER'] > sma1_uptrend_er_th) &
                                    (df[f'SMA{sma2_period}ER'] > sma2_uptrend_er_th), True, False)
        df['buy_signal'] = np.where((df[f'SMA{sma1_period}ROC{sma1_downtrend_roc_period}'] < sma1_downtrend_roc_th) &
                                     (df[f'SMA{sma1_period}ER'] > sma1_downtrend_er_th), True, False)

        # df['datetime'] = pd.to_datetime(df['Date'])
        # copy_df = df.loc[df['buy_signal']].copy()
        # if not copy_df.empty:
        #     if copy_df.loc[copy_df['sell_signal']].empty:
        #         print(ticker, 'buy but no sell')
        #         incomplete_trades.append({'ticker': ticker,
        #                                      'signal_price_at_close': float(copy_df.iloc[0]['Close']),
        #                                      'date': copy_df.iloc[0]['Date'],
        #                                      'last_price': float(df.iloc[-1]['Close'])
        #                                      })
        #
        #     pd.DataFrame(incomplete_trades).to_csv(save_under_results_path('incomplete_trades_last_60_days.csv'))
        #     # with open(save_under_results_path('incomplete_trades.json'), 'w') as f:
            #     json.dump(incomplete_trades, f, indent=4)

        # trades, final_cap = signal_trading_manager_long(ticker, df)
        #
        # all_trades = all_trades + trades
        # ticker_returns.append(
        #     {'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0})
        # pd.DataFrame(all_trades).to_csv(
        #     save_under_results_path(f'{strategy_name}_{run_time}_all_trades.csv'))
        # pd.DataFrame(ticker_returns).to_csv(
        #     save_under_results_path(f'{strategy_name}_{run_time}_ticker_returns.csv'))
