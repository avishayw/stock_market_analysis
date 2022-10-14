from google.cloud import storage
from google.oauth2 import service_account
from google_cloud_config import *
from pathlib import Path


def upload(file_path, bucket_file_path):
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)
    client = storage.Client(project='avish-analysis', credentials=credentials)
    bucket = client.get_bucket('avish-bucket')
    blob = bucket.blob(bucket_file_path)
    blob.upload_from_filename(file_path)


def download(bucket_file_path, save_to_path):
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)
    client = storage.Client(project='avish-analysis', credentials=credentials)
    bucket = client.get_bucket('avish-bucket')
    blob = bucket.blob(bucket_file_path)
    blob.download_to_filename(save_to_path)


def download_dir(bucket_dir_path, save_to_dir_path):
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)
    client = storage.Client(project='avish-analysis', credentials=credentials)
    bucket = client.get_bucket('avish-bucket')
    blobs = bucket.list_blobs(prefix=bucket_dir_path)  # Get list of files
    for blob in blobs:
        filename = blob.name.replace('/', '_')
        blob.download_to_filename(Path(save_to_dir_path, filename))  # Download


if __name__ == '__main__':
    bucket_path = 'ma_roc_er_optimization/'
    save_dir_path = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\ma_roc_er_long_optimization"
    download_dir(bucket_path, save_dir_path)

