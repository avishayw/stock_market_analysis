from google.cloud import storage
from google.oauth2 import service_account
from cloud_utils.google_cloud_config import *
from pathlib import Path
from google.api_core.exceptions import ServiceUnavailable
import time
from datetime import datetime
import pytz


def now():
    return datetime.now().astimezone(pytz.timezone('Asia/Jerusalem')).strptime('%Y-%m-%d %H:%M:%S')


def get_bucket(bucket: str, timeout: int = None):
    while True:
        try:
            credentials = service_account.Credentials.from_service_account_info(credentials_dict)
            client = storage.Client(project='avish-analysis', credentials=credentials)
            if timeout is None:
                return client.get_bucket(bucket)
            else:
                return client.get_bucket(bucket, timeout=timeout)
        except ServiceUnavailable as e:
            print(e)
            print(f'{now()} Encountered error with google services. Retry in 10 seconds...')
            time.sleep(10)


def upload_to_bucket(file_path, bucket_file_path):
    exception = True
    while exception:
        try:
            bucket = get_bucket('avish-bucket')
            blob = bucket.blob(bucket_file_path)
            blob.upload_from_filename(file_path)
            exception = False
        except ServiceUnavailable as e:
            print(e)
            print(f'{now()} Encountered error with google services. Retry in 10 seconds...')
            time.sleep(10)


def download_from_bucket(bucket_file_path, save_to_path):
    while True:
        try:
            bucket = get_bucket('avish-bucket')
            blob = bucket.blob(bucket_file_path)
            blob.download_to_filename(save_to_path)
            return save_to_path
        except ServiceUnavailable as e:
            print(e)
            print(f'{now()} Encountered error with google services. Retry in 10 seconds...')
            time.sleep(10)


def download_dir_from_bucket(bucket_dir_path, save_to_dir_path):
    while True:
        try:
            bucket = get_bucket('avish-bucket')
            blobs = bucket.list_blobs(prefix=bucket_dir_path)  # Get list of files
            downloaded_files = []
            for blob in blobs:
                filename = blob.name.replace('/', '_')
                download_path = Path(save_to_dir_path, filename)
                blob.download_to_filename(download_path)  # Download
                downloaded_files.append(download_path)
            return downloaded_files
        except ServiceUnavailable as e:
            print(e)
            print(f'{now()} Encountered error with google services. Retry in 10 seconds...')
            time.sleep(10)


def file_exist_in_bucket(bucket_file_path):
    while True:
        try:
            bucket = get_bucket('avish-bucket')
            blob = bucket.blob(bucket_file_path)
            return blob.exists()
        except ServiceUnavailable as e:
            print(e)
            print(f'{now()} Encountered error with google services. Retry in 10 seconds...')
            time.sleep(10)


def list_files_in_dir(bucket_dir_path, max_depth=None):
    while True:
        try:
            bucket = get_bucket('avish-bucket')
            blobs = bucket.list_blobs(prefix=bucket_dir_path)  # Get list of files
            files = []
            if max_depth is None:
                for blob in blobs:
                    filename = blob.name.replace('/', '_')
                    files.append(filename)
            else:
                for blob in blobs:
                    filename = '_'.join(blob.name.split('/')[0:1+max_depth])
                    files.append(filename)
                files = list(set(files))
            return files
        except ServiceUnavailable as e:
            print(e)
            print(f'{now()} Encountered error with google services. Retry in 10 seconds...')
            time.sleep(10)


def delete_file_from_bucket(bucket_file_path):
    exception = True
    while exception:
        try:
            bucket = get_bucket('avish-bucket')
            blob = bucket.blob(bucket_file_path)
            blob.delete()
            exception = False
        except ServiceUnavailable as e:
            print(e)
            print(f'{now()} Encountered error with google services. Retry in 10 seconds...')
            time.sleep(10)


if __name__ == '__main__':
    import time

    print(file_exist_in_bucket('channel_trading'))
    # download_from_bucket('minute_data_downloader.py', 'minute_data_downloader.py')
    # print(file_exist_in_bucket('minute_stocks/TGLS/TGLS_01-11-2022.parquet'))
    # exit()
    # durations = []
    # i = 0
    # while i < 3:
    #     t0 = time.perf_counter()
    #     print(list_files_in_dir('minute_stocks', max_depth=1))
    #     duration = time.perf_counter() - t0
    #     print(duration)
    #     durations.append(duration)
    #     i += 1
    #
    # print(durations)

