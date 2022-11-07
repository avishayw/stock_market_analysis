import pandas as pd
import numpy as np
from utils.download_stock_csvs import download_stock_day
from indicators.momentum_indicators import rsi
from measurements.noise_measurements import efficiency_ratio
from datetime import datetime


def trailing_rsi_trading(ticker,
                         df,
                         rsi_period=50,
                         change_period=10,
                         spy_rsi_th=30,
                         spy_rsi_diff_th=5,
                         spy_rsi_er_th=0.6,
                         stock_index_rsi_ratio=1):

    spy = pd.read_csv(download_stock_day('SPY')).reset_index()
    spy['Date'] = spy['Date'].map(lambda x: str(x).split(' ')[0])
    spy['Datetime'] = pd.to_datetime(spy['Date'])
    spy = rsi(spy, rsi_period)
    spy[f'{change_period}DayDiff'] = spy[f'RSI{rsi_period}'] - spy.shift(change_period)[f'RSI{rsi_period}']
    spy[f'{change_period}DayEfficiencyRatio'] = efficiency_ratio(spy, f'RSI{rsi_period}', change_period, inplace=False)

    df['Date'] = df['Date'].map(lambda x: str(x).split(' ')[0])
    df['Datetime'] = pd.to_datetime(df['Date'])
    df = rsi(df, rsi_period)

    i = 0
    long_position = False
    enter_price = None
    enter_date = None
    cap = 100.0

    trades = []

    while i < len(df):
        date_spy = spy.loc[spy['Datetime'] == df.iloc[i]['Datetime']]
        if date_spy.empty:
            i += 1
            continue
        if long_position:
            if df.iloc[i]['Close'] >= enter_price*1.1:
                exit_price = df.shift(-1).iloc[i]['Open']
                if np.isnan(exit_price):
                    break
                exit_date = df.shift(-1).iloc[i]['Date']
                if np.isnan(exit_price):
                    long_position = False
                    continue
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                period_df = pd.DataFrame.copy(df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                                    (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))])
                period_df.reset_index(inplace=True)
                period_max = period_df['High'].max()
                max_date = period_df.iloc[period_df['High'].idxmax()]['Datetime'].strftime('%Y-%m-%d')
                period_min = period_df['Low'].min()
                min_date = period_df.iloc[period_df['Low'].idxmin()]['Datetime'].strftime('%Y-%m-%d')
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100,
                              'period_max': period_max,
                              'period_max_date': max_date,
                              'period_min': period_min,
                              'period_min_date': min_date}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif date_spy.iloc[0][f'{change_period}DayDiff'] >= spy_rsi_diff_th and \
                date_spy.iloc[0][f'{change_period}DayEfficiencyRatio'] >= spy_rsi_er_th and \
                date_spy.iloc[0][f'RSI{rsi_period}'] >= spy_rsi_th and \
                df.iloc[i][f'RSI{rsi_period}'] <= date_spy.iloc[0][f'RSI{rsi_period}']*stock_index_rsi_ratio:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            print(enter_date)
            starting_rsi = df.iloc[i][f'RSI{rsi_period}']
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


if __name__ == '__main__':
    from utils.get_all_stocks import get_all_snp_stocks
    from utils.paths import save_under_results_path
    import random

    tickers = get_all_snp_stocks()
    ticker = random.choice(tickers)
    ticker = 'ORCL'
    df = pd.read_csv(download_stock_day(ticker))[-1008:]

    trades, final_cap = trailing_rsi_trading(ticker, df)
    pd.DataFrame(trades).to_csv(save_under_results_path(f'{ticker}_trailing_rsi_trading.csv'))
