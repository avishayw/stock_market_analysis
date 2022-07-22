from utils.get_stock_history_df import get_stock_daily_max_history_df, get_stock_minute_history_of_day
from utils.get_all_snp_companies import get_all_snp_companies
from os.path import dirname, abspath, exists
from pathlib import Path



def download_all_snp_stocks():
    project_path = dirname(dirname(abspath(__file__)))
    snp_stocks = get_all_snp_companies()
    downloaded_csvs = 0
    for ticker in snp_stocks:
        if not exists(Path(project_path, f"stocks_max_daily_history/{ticker}.csv")):
            stock_df = get_stock_daily_max_history_df(ticker)
            if len(stock_df) < 2:
                continue
            stock_df.to_csv(Path(project_path, f"stocks_max_daily_history/{ticker}.csv"))
            downloaded_csvs += 1
    print(f"Done. Downloaded {downloaded_csvs} stock CSVs.")


def download_stock(ticker):
    project_path = dirname(dirname(abspath(__file__)))
    csv_path = Path(project_path, f"stocks_max_daily_history/{ticker}.csv")
    if not exists(csv_path):
        stock_df = get_stock_daily_max_history_df(ticker)
        if len(stock_df) < 2:
            return None
        stock_df.to_csv(csv_path)
    return csv_path


def download_stock_minute_data(ticker,date):
    project_path = dirname(dirname(abspath(__file__)))
    csv_path = Path(project_path, f"stocks_max_daily_history/{ticker}_minute_{date}.csv")
    if not exists(csv_path):
        stock_df = get_stock_minute_history_of_day(ticker, date)
        if len(stock_df) < 2:
            return None
        stock_df.to_csv(csv_path)
    return csv_path


if __name__=="__main__":
    import pandas as pd

    stocks = get_all_snp_companies()

    for stock in stocks:
        path = download_stock(stock)
        print(path)
        if not path:
            continue
        df = pd.read_csv(path)
        zeros = df.loc[df["Open"]==0.0]
        if not zeros.empty:
            zeros.to_csv(f"zeros_{stock}.csv")

