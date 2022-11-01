from plotting.renko_chart import construct_renko_values_fixed_atr, construct_renko_values_fixed_pct, construct_renko_values_fixed_point
from trade_managers._signal_trading_manager import signal_trading_manager_long
import pandas as pd
import numpy as np
from datetime import datetime


def renko_buy_above_sma_sell_below_sma(ticker, df, sma_period=10, print_trades=True):
    df['Datetime'] = pd.to_datetime(df['Date'])

    # renko_df = construct_renko_values_fixed_atr(df)
    renko_df = construct_renko_values_fixed_pct(df, pct=3.0)
    renko_df['SMA'] = renko_df['renko_close'].rolling(sma_period).mean()

    i = 0
    long_position = False
    enter_price = None
    enter_date = None
    cap = 100.0

    trades = []

    while i < len(df):
        current_date = df.iloc[i]['Date']
        renko_df_date = renko_df.loc[renko_df['Date'] == current_date].copy()
        if renko_df_date.empty:
            pass
        elif long_position:
            if renko_df_date.iloc[0]['renko_high'] < renko_df_date.iloc[0]['SMA']:
                exit_price = df.shift(-1).iloc[i]['Open']
                if np.isnan(exit_price):
                    break
                exit_date = df.shift(-1).iloc[i]['Datetime']
                if np.isnan(exit_price):
                    long_position = False
                    continue
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                # period_df = pd.DataFrame.copy(df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                #                                      (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))])
                period_df = pd.DataFrame.copy(df.loc[(df['Datetime'] >= enter_date) &
                                                     (df['Datetime'] <= exit_date)])
                period_df.reset_index(inplace=True)
                period_max = period_df['High'].max()
                max_date = period_df.iloc[period_df['High'].idxmax()]['Datetime'].strftime('%Y-%m-%d')
                period_min = period_df['Low'].min()
                min_date = period_df.iloc[period_df['Low'].idxmin()]['Datetime'].strftime('%Y-%m-%d')
                enter_date = enter_date.strftime('%Y-%m-%d')
                exit_date = exit_date.strftime('%Y-%m-%d')
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
                if print_trades:
                    print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif renko_df_date.iloc[0]['renko_low'] > renko_df_date.iloc[0]['SMA']:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Datetime']
            long_position = True

        i += 1

    if print_trades:
        print(ticker, cap)
    return trades, cap


if __name__ == '__main__':
    from utils.download_stock_csvs import download_stock_day

    ticker = 'KO'
    df = pd.read_csv(download_stock_day(ticker)).reset_index()[-1008:]
    trades, final_cap = renko_buy_above_sma_sell_below_sma(ticker, df)