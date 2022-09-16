import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.download_stock_csvs import download_stock_day
import json
import glob
import os
from pathlib import Path


def df_with_day_gaps(df, reference_df):
    """
    :return: True for valid dataframes
    """
    df['datetime'] = pd.to_datetime(df['datetime'])
    reference_df['datetime'] = pd.to_datetime(reference_df['Date'])

    unique_day_dates = df['datetime'].dt.strftime('%Y-%m-%d').unique()
    unique_day_dates_reference = reference_df['datetime'].dt.strftime('%Y-%m-%d').unique()

    unique_day_datetimes_series = pd.Series([datetime.strptime(x, '%Y-%m-%d') for x in unique_day_dates])
    unique_day_datetimes_series_reference = pd.Series(
        [datetime.strptime(x, '%Y-%m-%d') for x in unique_day_dates_reference])

    start_datetime = unique_day_datetimes_series.iloc[0]
    start_datetime_reference = unique_day_datetimes_series_reference.iloc[0]

    if start_datetime != start_datetime_reference:
        if start_datetime < start_datetime_reference:
            unique_day_datetimes_series = unique_day_datetimes_series.loc[
                unique_day_datetimes_series >= start_datetime_reference]
        else:
            unique_day_datetimes_series_reference = unique_day_datetimes_series_reference.loc[
                unique_day_datetimes_series_reference >= start_datetime]

    # Comparing
    loops = min(len(unique_day_datetimes_series), len(unique_day_datetimes_series_reference))

    for i in range(loops):
        if unique_day_datetimes_series.iloc[i] != unique_day_datetimes_series_reference.iloc[i]:
            # print('missing dates')
            # print('df', unique_day_datetimes_series.iloc[i])
            # print('reference', unique_day_datetimes_series_reference.iloc[i])
            return True
    return False


def short_df(df, rows_th=2016):
    """
    :return: True for dataframes of length > rows_th (Default: 2016 (~8 Years))
    """
    if len(df) < rows_th:
        return True
    return False


def df_with_incomplete_minute_data(df, hr_th=3.5):
    """
    For each trading day, this function will check if there are at least 6hr (Default) between the first and last
    minute data
    :return: True for complete dataframes
    """
    df['datetime'] = pd.to_datetime(df['datetime'])
    unique_day_dates = df['datetime'].dt.strftime('%Y-%m-%d').unique()
    for date in unique_day_dates:
        lower_datetime_limit = datetime.strptime(date, '%Y-%m-%d')
        upper_datetime_limit = lower_datetime_limit + relativedelta(days=1)
        sample_df = df.loc[(df['datetime'] > lower_datetime_limit) & (df['datetime'] < upper_datetime_limit)].copy()
        first_date_row = sample_df.iloc[0]['datetime']
        last_date_row = sample_df.iloc[-1]['datetime']
        total_hours = (last_date_row - first_date_row).total_seconds()/3600.0
        if total_hours < hr_th:
            return True
    return False


def delisted_stock(ticker):
    try:
        test_df = pd.read_csv(download_stock_day(ticker))
    except ValueError:
        return True
    return False


def filter_dfs(parquets_dir):

    now = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")

    all_parquets = glob.glob(parquets_dir + '/*.parquet')

    parquets_dict = {'short_dfs': [],
                     'missing_dates_dfs': [],
                     'incomplete_minute_data_dfs': [],
                     'index_error_dfs': [],
                     'valid_dfs': [],
                     'delisted_dfs': []}

    reference_df = pd.read_csv(download_stock_day('AAPL'))

    for parquet in all_parquets:
        ticker = str(os.path.basename(parquet)).replace('.parquet', '')
        df = pd.read_parquet(parquet)
        try:
            if short_df(df):
                parquets_dict['short_dfs'].append(ticker)
                print(ticker, 'short_df')
            elif df_with_incomplete_minute_data(df):
                parquets_dict['incomplete_minute_data_dfs'].append(ticker)
                print(ticker, 'incomplete minute data')
            elif df_with_day_gaps(df, reference_df):
                parquets_dict['missing_dates_dfs'].append(ticker)
                print(ticker, 'missing_dates')
            else:
                parquets_dict['valid_dfs'].append(ticker)
                print(ticker, 'valid')
        except IndexError:
            parquets_dict['index_error_dfs'].append(ticker)
            print(ticker, 'IndexError')
        if delisted_stock(ticker):
            parquets_dict['delisted_dfs'].append(ticker)
            print(ticker, 'delisted df')
        with open(f'parquets_dict_{now}.json', 'w') as f:
            json.dump(parquets_dict, f, indent=4)

    return parquets_dict


def minute_data_to_day(df):

    new_df_dict = {'Date': [], 'Open': [], 'High': [], 'Low': [], 'Close': [], 'Volume': []}

    unique_dates = df['datetime'].dt.strftime('%Y-%m-%d').unique().tolist()

    try:
        for date in unique_dates:
            lower_date_limit = datetime.strptime(date,'%Y-%m-%d')
            upper_date_limit = lower_date_limit + relativedelta(days=1)
            work_df = df.loc[(df['datetime'] > lower_date_limit) & (df['datetime'] < upper_date_limit)].copy()
            new_df_dict['Date'].append(date)
            new_df_dict['Open'].append(work_df.iloc[0]['open'])
            new_df_dict['Close'].append(work_df.iloc[-1]['close'])
            new_df_dict['High'].append(work_df['high'].max())
            new_df_dict['Low'].append(work_df['low'].min())
            new_df_dict['Volume'].append(work_df['volume'].sum())
    except IndexError:
        return None

    return pd.DataFrame(new_df_dict)


def convert_all_minute_parquets_to_day_csv(minute_data_dir, destination_dir, tickers_list=None):

    parquet_files = glob.glob(minute_data_dir + '/*.parquet')
    for parquet_file in parquet_files:
        ticker = str(os.path.basename(parquet_file)).replace('.parquet', '')
        if tickers_list is not None:
            if ticker not in tickers_list:
                continue
        df = pd.read_parquet(parquet_file)
        day_df = minute_data_to_day(df)
        if day_df is not None:
            day_df.to_csv(Path(destination_dir, f'{ticker}.csv'))


# result_dict = filter_dfs(r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\stocks_minute_history")
# print(result_dict['valid_dfs'])

# json_path = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\utils\parquets_dict_11-09-2022-18-33-06.json"
#
# with open(json_path, 'r') as f:
#     parquet_dict = json.load(f)
#
# delisted_dict = {}
# delisted_stocks = parquet_dict['delisted_dfs']
#
# for df_type in parquet_dict.keys():
#     if df_type == 'delisted_dfs':
#         continue
#     delisted_dict[f'delisted_dfs+{df_type}'] = [x for x in parquet_dict[df_type] if x in delisted_stocks]
#
# pd.Series(delisted_dict['delisted_dfs+incomplete_minute_data_dfs']).to_csv('delisted_stocks_incomplete_minute_data.csv')

minute_data_dir = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\stocks_minute_history"
destination_dir = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\stocks_minute_history\minute_to_day_conversion"
tickers_list = pd.read_csv(r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\utils\delisted_stocks_incomplete_minute_data.csv").to_numpy()


convert_all_minute_parquets_to_day_csv(minute_data_dir, destination_dir, tickers_list=tickers_list)

