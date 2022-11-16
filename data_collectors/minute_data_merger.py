from cloud_utils.bucket_gcp_utils import download_dir_from_bucket, list_files_in_dir, upload_to_bucket, file_exist_in_bucket, download_from_bucket, delete_file_from_bucket
from utils.paths import project_path, save_under_project_path
import os
import shutil
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
import time


def now():
    return datetime.now().astimezone(pytz.timezone('Asia/Jerusalem')).strftime('%Y-%m-%d %H:%M:%S')


local_split_files_dir_path = save_under_project_path('stock_minute_data/')
local_merged_files_dir_path = save_under_project_path('stock_minute_merged_data/')
if not os.path.exists(local_split_files_dir_path):
    print(f'{now()} Creating local directory for split files...')
    os.mkdir(local_split_files_dir_path)
if not os.path.exists(local_merged_files_dir_path):
    print(f'{now()} Creating local directory for merged files...')
    os.mkdir(local_merged_files_dir_path)

run_now = input("Run now? (y/n) ")
next_date = datetime.now().astimezone(pytz.timezone('Asia/Jerusalem')) - relativedelta(hours=1)
while True:
    today = datetime.now().astimezone(pytz.timezone('Asia/Jerusalem'))
    if (today >= next_date and today.weekday() in [0, 6]) or run_now:
        t0 = time.perf_counter()
        next_date = today + relativedelta(weeks=1)
        run_now = None
        print(f'{now()} Starting')

        # for stats
        total_split_files = 0
        total_new_merged_files = 0

        print(f'{now()} Listing tickers directories of split files in bucket...')
        ticker_dirs = list_files_in_dir('minute_stocks/', max_depth=1)  # format: 'minute_stocks_'<ticker>'
        print(f'{now()} Total of {len(ticker_dirs)} ticker directories found in bucket.')

        for i, ticker_dir in enumerate(ticker_dirs):
            ticker = ticker_dir.split("_")[-1]  # 'minute_stocks_<ticker>' > ['minute', 'stocks', '<ticker>'] > '<ticker>'
            ticker_in_order_str = f'{ticker} ({i+1}/{len(ticker_dirs)})'
            print(f'{now()} Listing {ticker_in_order_str} split files in bucket...')
            bucket_minute_dir_path = '_'.join(ticker_dir.split('_')[:2])
            bucket_full_ticker_minute_dir_path = f'{bucket_minute_dir_path}/{ticker}/'
            ticker_minute_files = list_files_in_dir(bucket_full_ticker_minute_dir_path)
            if len(ticker_minute_files) == 0:
                print(f'{now()} No split files of {ticker_in_order_str}.')
                continue
            else:
                print(f'{now()} Found {len(ticker_minute_files)} split files of {ticker_in_order_str}.')
                total_split_files += len(ticker_minute_files)

            print(f'{now()} Fixing bucket file paths in order to delete later...')
            ticker_minute_files_bucket_real_paths = []
            for file in ticker_minute_files:
                filename = file.split('_')[-1]  # 'minute_stocks_<ticker>_<ticker>_<date_str>.parquet' > '<date_str>.parquet'
                bucket_file_path = f'{ticker}_{filename}'
                bucket_full_file_path = f'{bucket_full_ticker_minute_dir_path}{bucket_file_path}'
                ticker_minute_files_bucket_real_paths.append(bucket_full_file_path)

            local_ticker_split_files_dir_path = save_under_project_path(f'stock_minute_data/{ticker}/')
            if not os.path.exists(local_ticker_split_files_dir_path):
                print(f'{now()} Creating a local directory for {ticker_in_order_str} split files...')
                os.mkdir(local_ticker_split_files_dir_path)

            print(f'{now()} Downloading {ticker_in_order_str} split files from bucket...')
            ticker_minute_files = download_dir_from_bucket(bucket_full_ticker_minute_dir_path, local_ticker_split_files_dir_path)
            print(f'{now()} Checking for {ticker_in_order_str} existing merged file in bucket...')
            if file_exist_in_bucket(f'stock_merged_minute_data/{ticker}.parquet'):
                print(f'{now()} Found existing merged file of {ticker_in_order_str}. Downloading...')
                ticker_minute_files.append(download_from_bucket(f'stock_merged_minute_data/{ticker}.parquet', local_ticker_split_files_dir_path))
            else:
                print(f'{now()} No merged file of {ticker_in_order_str}.')

            print(f'{now()} Loading {ticker_in_order_str} dataframes from files...')
            ticker_dataframes = []
            for file in ticker_minute_files:
                ticker_dataframes.append(pd.read_parquet(file).reset_index())

            print(f'{now()} Merging {ticker_in_order_str} dataframes...')
            merged_df = pd.concat(ticker_dataframes)
            initial_df_length = len(merged_df)
            print(f'{now()} Removing duplicate lines...')
            merged_df.drop_duplicates(subset=['Datetime'], inplace=True)
            final_df_length = len(merged_df)
            print(f'{now()} {initial_df_length-final_df_length} lines removed from dataframe.')
            print(f'{now()} Sorting dataframe by date...')
            merged_df.sort_values(by='Datetime', ascending=True, inplace=True)
            local_merged_file_path = save_under_project_path(f'stock_minute_merged_data/{ticker}_minute_data_merged.parquet')
            merged_df.to_parquet(local_merged_file_path)
            print(f'{now()} Uploading {ticker_in_order_str} merged dataframe to bucket...')
            upload_to_bucket(local_merged_file_path, f'stock_merged_minute_data/{ticker}.parquet')
            print(f'{now()} Finished merging and uploading {ticker_in_order_str} dataframes successfully.')
            total_new_merged_files += 1

            print(f'{now()} Deleting {ticker_in_order_str} local files...')
            try:
                shutil.rmtree(local_ticker_split_files_dir_path)
                shutil.rmtree(local_merged_file_path)
            except PermissionError as e:
                print(e)
                print(f"{now()} Couldn't remove local files. Access is denied.")

            print(f'{now()} Deleting {ticker_in_order_str} split files from bucket...')
            for file in ticker_minute_files_bucket_real_paths:
                delete_file_from_bucket(file)
            print(f'{now()} Done for {ticker_in_order_str}.')

        run_duration_in_hr = round((time.perf_counter() - t0)/3600, 2)
        print(f'{now()} Minute Data Merger finished successfully. Took {run_duration_in_hr} hours to complete. Total split files loaded: {total_split_files}. Total new merged files: {total_new_merged_files}.')
        print(f'{now()} Sleeping for one week. Next run: {next_date.strftime("%Y-%m-%d %H:%M:%S")}')
