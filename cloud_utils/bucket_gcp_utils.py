from google.cloud import storage
from google.oauth2 import service_account
from cloud_utils.google_cloud_config import *
from pathlib import Path


def get_bucket(bucket: str, timeout: int = None):
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)
    client = storage.Client(project='avish-analysis', credentials=credentials)
    if timeout is None:
        return client.get_bucket(bucket)
    else:
        return client.get_bucket(bucket, timeout=timeout)


def upload_to_bucket(file_path, bucket_file_path):
    bucket = get_bucket('avish-bucket')
    blob = bucket.blob(bucket_file_path)
    blob.upload_from_filename(file_path)


def download_from_bucket(bucket_file_path, save_to_path):
    bucket = get_bucket('avish-bucket')
    blob = bucket.blob(bucket_file_path)
    blob.download_to_filename(save_to_path)
    return save_to_path


def download_dir_from_bucket(bucket_dir_path, save_to_dir_path):
    bucket = get_bucket('avish-bucket')
    blobs = bucket.list_blobs(prefix=bucket_dir_path)  # Get list of files
    downloaded_files = []
    for blob in blobs:
        filename = blob.name.replace('/', '_')
        download_path = Path(save_to_dir_path, filename)
        blob.download_to_filename(download_path)  # Download
        downloaded_files.append(download_path)
    return downloaded_files


def file_exist_in_bucket(bucket_file_path):
    bucket = get_bucket('avish-bucket')
    blob = bucket.blob(bucket_file_path)
    return blob.exists()


def list_files_in_dir(bucket_dir_path, max_depth=None):
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


def delete_file_from_bucket(bucket_file_path):
    bucket = get_bucket('avish-bucket')
    blob = bucket.blob(bucket_file_path)
    blob.delete()


if __name__ == '__main__':
    import time

    download_from_bucket('download_daily_minute.py', 'download_daily_minute.py')
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

