from utils.get_stock_daily_max_history_df import get_stock_daily_max_history_df
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
            stock_df.to_csv(Path(project_path, f"stocks_max_daily_history/{ticker}.csv"))
            downloaded_csvs += 1
    print(f"Done. Downloaded {downloaded_csvs} stock CSVs.")


def download_stock(ticker):
    project_path = dirname(dirname(abspath(__file__)))
    if not exists(Path(project_path, f"stocks_max_daily_history/{ticker}.csv")):
        stock_df = get_stock_daily_max_history_df(ticker)
        stock_df.to_csv(Path(project_path, f"stocks_max_daily_history/{ticker}.csv"))
    return Path(project_path, f"stocks_max_daily_history/{ticker}.csv")


if __name__=="__main__":

    download_stock('FB')
