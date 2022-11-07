from cloud_utils.bucket_gcp_utils import download_dir_from_bucket, list_files_in_dir, upload_to_bucket
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
        print(f'{now()} Downloading parquet files from bucket...')
        all_minute_files = download_dir_from_bucket('minute_stocks/', save_under_project_path('stock_minute_data/'))
        print(f'{now()} Loading dataframes...')
        ticker_dataframes = {}
        for file in all_minute_files:
            ticker = file.split('_')[-2]
            if ticker not in ticker_dataframes.keys():
                ticker_dataframes[ticker] = [pd.read_parquet(file).reset_index()]
            else:
                ticker_dataframes[ticker].append(pd.read_parquet(file).reset_index())

        for ticker in ticker_dataframes.keys():
            print(f'{now()} Merging {ticker} dataframes...')
            merged_df = pd.concat(ticker_dataframes[ticker])
            merged_df.drop_duplicates(subset=['Datetime'], inplace=True)
            merged_df.sort_values(by='Datetime', ascending=True, inplace=True)

            merged_file_path = save_under_project_path(f'stock_minute_merged_data/{ticker}_minute_data_merged.csv')
            merged_df.to_parquet(merged_file_path)
            print(f'{now()} Uploading {ticker} merged dataframe to bucket...')
            upload_to_bucket(merged_file_path, f'stock_merged_minute_data/{ticker}.parquet')

        print(f'{now()} Finished merging dataframes successfully. Next run: {next_date.strftime("%Y-%m-%d %H:%M:%S")}')
