"""
This file will contain some functions which will help with the training:
1. Choose random stock out of more than 8000
2. Choose random index
4. A space for adding indicators
5. Plot the data
6. Ability to add one day at a time in order to test price action
7. A log which will contain the trades, free text for the analysis, indicators used etc. Hopefully this log will show
more and more good estimations.
8. Backup everything
"""
from utils.stocks_by_exchange import *
from utils.download_stock_csvs import *
from plotting.candlestick_chart import multiple_windows_chart, add_markers_to_candlestick_chart, candlestick_chart_fig
from cloud_utils.bucket import upload
from utils.in_sample_tickers import *
import random
import pandas as pd
import numpy as np
import os
from datetime import datetime


def random_chart(plot=False):
    # tickers = NASDAQ_COMMON_STOCKS + NYSE_COMMON_STOCKS + AMEX_COMMON_STOCKS
    tickers = median_volume_above_1m_stocks
    ticker = random.choice(tickers)
    df = pd.read_csv(download_stock_day(ticker)).reset_index()
    length = len(df)
    idx = random.choice(list(range(int(np.floor(length*0.9)))))
    df = df[:idx].copy()

    df['Datetime'] = pd.to_datetime(df['Date'])
    weekly_df = pd.read_csv(download_stock_week(ticker)).reset_index()
    weekly_df['Datetime'] = pd.to_datetime(weekly_df['Date'])
    weekly_df = weekly_df.loc[weekly_df['Datetime'] < df.iloc[-1]['Datetime']]
    monthly_df = pd.read_csv(download_stock_month(ticker)).reset_index()
    monthly_df['Datetime'] = pd.to_datetime(monthly_df['Date'])
    monthly_df = monthly_df.loc[monthly_df['Datetime'] < df.iloc[-1]['Datetime']]

    df['Date_backup'] = df['Date']
    df['Date'] = pd.Series(list(range(len(df))))
    weekly_df['Date'] = pd.Series(list(range(len(weekly_df))))
    monthly_df['Date'] = pd.Series(list(range(len(monthly_df))))

    if os.path.exists('plot_IDs.csv'):
        plots_df = pd.read_csv('plot_IDs.csv')
        plots_df = plots_df[list(plots_df.columns)[1:]].copy()
        new_id = int(plots_df.iloc[-1]['ID']) + 1
        plot_dicts_list = plots_df.to_dict('records')
        plot_dicts_list.append({'ID': new_id, 'symbol': ticker, 'idx': idx, 'date': df.iloc[-1]['Date_backup']})
        pd.DataFrame(plot_dicts_list).to_csv('plot_IDs.csv')
    else:
        new_id = 0
        plot_dict = {'ID': [new_id], 'symbol': [ticker], 'idx': [idx], 'date': [df.iloc[-1]['Date_backup']]}
        pd.DataFrame(plot_dict).to_csv('plot_IDs.csv')

    day_fig = multiple_windows_chart(str(new_id), df, {(2, 'Volume'): ['Volume']})
    week_fig = multiple_windows_chart(str(new_id), weekly_df, {(2, 'Volume'): ['Volume']})
    month_fig = multiple_windows_chart(str(new_id), monthly_df, {(2, 'Volume'): ['Volume']})

    day_fig.write_html(f'plots/ID_{new_id}_day.html')
    week_fig.write_html(f'plots/ID_{new_id}_week.html')
    month_fig.write_html(f'plots/ID_{new_id}_month.html')

    if plot:
        day_fig.show()

    print(f'New ID: {new_id}')


def plot_extended_chart(plot_id, days_to_add):
    plots_df = pd.read_csv('plot_IDs.csv')
    plots_df = plots_df[list(plots_df.columns)[1:]].copy()
    plots_df = plots_df.loc[plots_df['ID'] == plot_id]
    ticker = plots_df.iloc[0]['symbol']
    idx = plots_df.iloc[0]['idx']
    df = pd.read_csv(download_stock_day(ticker)).reset_index()
    if (idx + days_to_add) < len(df):
        df = df[:idx + days_to_add]
    df['Date'] = pd.Series(list(range(len(df))))
    day_fig = multiple_windows_chart(str(plot_id), df, {(2, 'Volume'): ['Volume']})
    day_fig.show()


def load_df(plot_id):  # For calculations and technical indicators
    plots_df = pd.read_csv('plot_IDs.csv')
    plots_df = plots_df[list(plots_df.columns)[1:]].copy()
    plots_df = plots_df.loc[plots_df['ID'] == plot_id]
    ticker = plots_df.iloc[0]['symbol']
    idx = plots_df.iloc[0]['idx']
    df = pd.read_csv(download_stock_day(ticker)).reset_index()
    df = df[:idx].copy()
    df['Date'] = pd.Series(list(range(len(df))))

    return df


def plot_spy(plot_id, timeframe='day'):

    plots_df = pd.read_csv('plot_IDs.csv')
    plots_df = plots_df[list(plots_df.columns)[1:]].copy()
    plots_df = plots_df.loc[plots_df['ID'] == plot_id]
    date = datetime.strptime(plots_df.iloc[0]['date'], '%Y-%m-%d')
    if timeframe == 'day':
        df = pd.read_csv(download_stock_day('SPY')).reset_index()
    elif timeframe == 'week':
        df = pd.read_csv(download_stock_week('SPY')).reset_index()
    elif timeframe == 'month':
        df = pd.read_csv(download_stock_month('SPY')).reset_index()
    else:
        print('invalid timeframe')
        return None

    df['Datetime'] = pd.to_datetime(df['Date'])
    df = df.loc[df['Datetime'] <= date].copy()
    df['Date'] = pd.Series(list(range(len(df))))
    fig = multiple_windows_chart('SPY', df, {(2, 'Volume'): ['Volume']})
    fig.show()


if __name__ == '__main__':
    # random_chart(plot=True)
    # days = 1
    # while True:
    #     print(f'days: {days}')
    #     plot_extended_chart(8, days)
    #     input('Add day')
    #     days += 1
    plot_extended_chart(11, 0)
