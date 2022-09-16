import glob
import pandas as pd
import os
from pathlib import Path


def parquet_to_csv(file_path):
    dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    df = pd.read_parquet(file_path)
    df.to_csv(Path(dir, file_name.replace('parquet', 'csv')))


def dir_of_parquest_to_csv(dir_path, delete_parquet=False):
    files = glob.glob(dir_path + '/*.parquet')
    for file in files:
        parquet_to_csv(file)
        if delete_parquet:
            os.remove(file)


if __name__=="__main__":

    path = r"C:\Users\Avishay Wasse\Documents\MEGAsync Downloads\Minute_Equities_All\minute\A.tar\A\AAPL.parquet"
    parquet_to_csv(path)

