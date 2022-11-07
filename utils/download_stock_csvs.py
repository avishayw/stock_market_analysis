import os.path

from utils.get_stock_history_df import get_stock_daily_max_history_df, get_stock_minute_history_of_day, get_stock_weekly_max_history_df, get_stock_monthly_max_history_df, get_stock_minute_max_history_df
from utils.get_all_stocks import get_all_snp_stocks
from os.path import dirname, abspath, exists
from pathlib import Path


def download_stock_day(ticker):
    project_path = dirname(dirname(abspath(__file__)))
    if not os.path.exists(Path(project_path, f"stocks_max_daily_history")):
        os.mkdir(Path(project_path, f"stocks_max_daily_history"))
    csv_path = Path(project_path, f"stocks_max_daily_history/{ticker}.csv")
    if not exists(csv_path):
        stock_df = get_stock_daily_max_history_df(ticker)
        if len(stock_df) < 2:
            return None
        stock_df.to_csv(csv_path)
    return csv_path


def download_stock_week(ticker):
    project_path = dirname(dirname(abspath(__file__)))
    if not os.path.exists(Path(project_path, f"stocks_max_weekly_history")):
        os.mkdir(Path(project_path, f"stocks_max_weekly_history"))
    csv_path = Path(project_path, f"stocks_max_weekly_history/{ticker}.csv")
    if not exists(csv_path):
        stock_df = get_stock_weekly_max_history_df(ticker)
        if len(stock_df) < 2:
            return None
        stock_df.to_csv(csv_path)
    return csv_path


def download_stock_month(ticker):
    project_path = dirname(dirname(abspath(__file__)))
    if not os.path.exists(Path(project_path, f"stocks_max_monthly_history")):
        os.mkdir(Path(project_path, f"stocks_max_monthly_history"))
    csv_path = Path(project_path, f"stocks_max_monthly_history/{ticker}.csv")
    if not exists(csv_path):
        stock_df = get_stock_monthly_max_history_df(ticker)
        if len(stock_df) < 2:
            return None
        stock_df.to_csv(csv_path)
    return csv_path


def download_stock_minute_data(ticker):
    project_path = dirname(dirname(abspath(__file__)))
    csv_path = Path(project_path, f"stocks_max_daily_history/{ticker}_minute.csv")
    if not exists(csv_path):
        stock_df = get_stock_minute_max_history_df(ticker)
        if len(stock_df) < 2:
            return None
        stock_df.to_csv(csv_path)
    return csv_path


if __name__=="__main__":
    import pandas as pd

    ticker = '^VIX'
    df = pd.read_csv(download_stock_day(ticker))
    print(df.head())
    print(df.tail())

