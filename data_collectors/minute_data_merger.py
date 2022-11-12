from cloud_utils.bucket_gcp_utils import download_dir_from_bucket, list_files_in_dir, upload_to_bucket, file_exist_in_bucket, download_from_bucket, delete_file_from_bucket
from utils.paths import project_path, save_under_project_path
import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


next_date = datetime.now() - relativedelta(hours=1)
while True:
    today = datetime.now()
    if today >= next_date:
        next_date = datetime.now() + relativedelta(weeks=2)
        print(f'{now()} Starting')
        if not os.path.exists(save_under_project_path('stock_minute_data/')):
            os.mkdir(save_under_project_path('stock_minute_data/'))
        if not os.path.exists(save_under_project_path('stock_minute_merged_data/')):
            os.mkdir(save_under_project_path('stock_minute_merged_data/'))

        if file_exist_in_bucket('stock_merged_minute_data/'):
            print(f'{now()} Listing merged dataframes in bucket...')
            merged_dataframes_bucket_paths = list_files_in_dir('stock_merged_minute_data/')

        # for file in merged_dataframes_bucket_paths:

        print(f'{now()} Listing tickers directories of split files in bucket...')
        ticker_dirs = list_files_in_dir('minute_stocks/', max_depth=1)
        print(ticker_dirs)

        for ticker_dir in ticker_dirs:
            ticker = ticker_dir.split("_")[-1]
            print(f'{now()} Listing {ticker} split files in bucket...')
            ticker_minute_files = list_files_in_dir('/'.join(['_'.join(ticker_dir.split('_')[:2])] + [ticker_dir.split('_')[-1]]))
            if len(ticker_minute_files) == 0:
                print(f'{now()} No split dataframes of {ticker}.')
                continue
            else:
                print(f'{now()} Found {len(ticker_minute_files)} split files of {ticker}.')
            ticker_minute_files_to_delete = ['/'.join(['minute_stocks', ticker] + ['_'.join(f.split('_')[-2:])]) for f in
                                   ticker_minute_files]
            if not os.path.exists(save_under_project_path(f'stock_minute_data/{ticker}/')):
                os.mkdir(save_under_project_path(f'stock_minute_data/{ticker}/'))
            print(f'{now()} Downloading {ticker} split files from bucket...')
            ticker_minute_files = download_dir_from_bucket('/'.join(['_'.join(ticker_dir.split('_')[:2])] + [ticker_dir.split('_')[-1]]), save_under_project_path(f'stock_minute_data/{ticker}/'))
            print(f'{now()} Checking for {ticker} existing merged file in bucket...')
            if file_exist_in_bucket(f'stock_merged_minute_data/{ticker}.parquet'):
                print(f'{now()} Found existing merged file of {ticker}. Downloading...')
                ticker_minute_files.append(download_from_bucket(f'stock_merged_minute_data/{ticker}.parquet', f'stock_minute_data/{ticker}/'))
            else:
                print(f'{now()} No merged file of {ticker}.')

            ticker_dataframes = []
            for file in ticker_minute_files:
                ticker_dataframes.append(pd.read_parquet(file).reset_index())

            print(f'{now()} Merging {ticker} dataframes...')
            merged_df = pd.concat(ticker_dataframes)
            merged_df.drop_duplicates(subset=['Datetime'], inplace=True)
            merged_df.sort_values(by='Datetime', ascending=True, inplace=True)
            merged_file_path = save_under_project_path(f'stock_minute_merged_data/{ticker}_minute_data_merged.csv')
            merged_df.to_parquet(merged_file_path)
            print(f'{now()} Uploading {ticker} merged dataframe to bucket...')
            upload_to_bucket(merged_file_path, f'stock_merged_minute_data/{ticker}.parquet')
            print(f'{now()} Finished merging and uploading {ticker} dataframes successfully.')

            print(f'{now()} Deleting {ticker} split files from bucket...')
            for file in ticker_minute_files_to_delete:
                delete_file_from_bucket(file)
            print(f'{now()} Deleted {ticker} split files from bucket successfully.')

