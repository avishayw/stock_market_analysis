from utils.stocks_by_exchange import *
from cloud_utils.bucket_gcp_utils import upload_to_bucket
import yfinance as yf
import os
import pytz


def now():
    return datetime.now().astimezone(pytz.timezone('Asia/Jerusalem')).strftime('%Y-%m-%d %H:%M:%S')


def download_minute_daily_and_upload_to_bucket(today_str):

    tickers = NASDAQ_COMMON_STOCKS + NYSE_COMMON_STOCKS + AMEX_COMMON_STOCKS
    
    for i, ticker in enumerate(tickers):
        try:
            df = yf.Ticker(ticker).history(period='5d', interval='1m')
            if df.empty:
                continue
            file_path = f'{ticker}_{today_str}.parquet'
            df.to_parquet(file_path)
            upload_to_bucket(file_path, f'minute_stocks/{ticker}/{file_path}')
            os.remove(file_path)
            print(f'{now()} Uploaded {ticker} dataframe to bucket ({i+1}/{len(tickers)}).')
        except ValueError:
            continue
    print(f'{now()} Finished downloading stocks dataframes.')


if __name__=="__main__":
    from datetime import datetime
    import time

    run_now = input('Run now? (y/n) ')
    while True:
        today = datetime.now().astimezone(pytz.timezone('Asia/Jerusalem'))

        if today.weekday() is not (0 or 7) and today.hour == 0 or run_now == 'y':
            today_str = today.strftime('%d-%m-%Y')
            download_minute_daily_and_upload_to_bucket(today_str)
            print(f'{now()}: Sleeping 24 hours.')
            time.sleep(86400)
