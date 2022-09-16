import gzip
import shutil
import tarfile
import glob
import os
from pathlib import Path

import pandas as pd

from utils.parquet_to_csv import dir_of_parquest_to_csv


def extract_tar_from_gzip(gzip_path):
    gzip_file_name = os.path.basename(gzip_path)
    gzip_file_dir = os.path.dirname(gzip_path)
    tar_file_name = gzip_file_name.replace('.gz', '')
    tar_path = Path(gzip_file_dir, tar_file_name)
    with gzip.open(gzip_path, 'rb') as f_in:
        with open(tar_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def extract_tar(tar_gz_path, save_dir):
    tar_file = tarfile.open(tar_gz_path)
    tar_file.extractall(save_dir)
    tar_file.close()


gz_dir_path = r"C:\Users\Avishay Wasse\Documents\MEGAsync Downloads\Minute_Equities_All\minute"
gz_files_list = glob.glob(gz_dir_path + '/*.gz')
# gz_files_list.remove(r'C:\Users\Avishay Wasse\Documents\MEGAsync Downloads\Minute_Equities_All\minute\A.tar.gz')
# print(gz_files_list)

save_dir = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\stocks_minute_history"

for file in gz_files_list:
    print(file)
    # new_dir = os.path.basename(file).replace('.tar.gz', '')
    # full_new_dir_path = Path(save_dir, new_dir).__str__()
    extract_tar(file, save_dir)
    # parquest_files = glob.glob(full_new_dir_path + '/*.parquet')
    # for parquet in parquest_files:
    #     file_name = os.path.basename(parquet)
    #     df = pd.read_parquet(parquet)
    #     df.to_csv(Path(save_dir, file_name.replace('parquet', 'csv')))
    # os.remove(full_new_dir_path)
