from utils.download_stock_csvs import download_stock_day
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import statistics
import time


def reverse_pattern_enter_and_exit(ticker, entrance_df, exit_dfs):

    if len(exit_dfs) != 1:
        exit_df = pd.concat(list(exit_dfs), ignore_index=True)
        exit_df.sort_values(by=['entrance_date'])
    else:
        exit_df = list(exit_dfs)[0]

    if len(entrance_df) == 0 or entrance_df.empty:
        return None

    trades = []

    for day in range(len(entrance_df)):
        entrance_price = entrance_df.iloc[day]["entrance_price"]
        # Skip zeros
        if entrance_price == 0.0:
            continue
        entrance_date = str(entrance_df.iloc[day]["entrance_date"])
        relevant_exit_df = exit_df.loc[exit_df["entrance_date"] > entrance_date]

        if not (len(relevant_exit_df)==0 or relevant_exit_df.empty):
            relevant_exit_df = relevant_exit_df.iloc[0]
            exit_price = relevant_exit_df["entrance_price"]
            exit_date = relevant_exit_df["entrance_date"]
            change_abs = exit_price - entrance_price
            trade_time_in_days = (datetime.strptime(exit_date[:10], "%Y-%m-%d") - datetime.strptime(entrance_date[:10], "%Y-%m-%d")).days
            if not entrance_price == 0.0:
                change_percentage = ((exit_price - entrance_price)/entrance_price)*100.0
            else:
                change_percentage = None
        else:
            last_date_df = pd.read_csv(download_stock_day(ticker)).iloc[-1]
            exit_price = last_date_df["Close"]
            exit_date = last_date_df["Date"]
            change_abs = exit_price - entrance_price
            trade_time_in_days = (datetime.strptime(exit_date[:10], "%Y-%m-%d") - datetime.strptime(entrance_date[:10], "%Y-%m-%d")).days
            if not entrance_price == 0.0:
                change_percentage = ((exit_price - entrance_price)/entrance_price)*100.0
            else:
                change_percentage = None

        trades.append({"entrance_date": entrance_date[:10], "entrace_price": entrance_price,
                       "exit_date": exit_date[:10], "exit_price": exit_price, "trade_time_in_days": trade_time_in_days,
                       "win": (change_abs > 0), "change": change_abs,
                       "change_%": change_percentage})

    return trades


if __name__=="__main__":
    from locators.reverse_pattern_locators_day import doji_long, doji_short, evening_star, dark_cloud_cove
    from utils.get_all_stocks import get_all_snp_stocks
    from os.path import dirname, abspath, exists
    from pathlib import Path
    from dateutil.relativedelta import relativedelta

    project_path = dirname(dirname(abspath(__file__)))
    tickers = get_all_snp_stocks()
    total_results_df = pd.DataFrame([{"Stock": None, "entrance_date": None, "entrace_price": None, "exit_date": None, "exit_price": None, "trade_time_in_days": None, "win": None, "change": None, "change_%": None}])

    for ticker in tickers:
        print(f"{ticker}")
        path = download_stock_day(ticker)
        if not path:
            continue
        stock_df = pd.read_csv(download_stock_day(ticker))
        stock_df["datetime"] = pd.to_datetime(stock_df["Date"])
        stock_df = stock_df.loc[stock_df["datetime"] > datetime.utcnow() - relativedelta(years=4)]
        stock_df.drop(columns=['datetime'])
        entrance_df = doji_long(stock_df)
        exit_dfs = [evening_star(stock_df),
                    dark_cloud_cove(stock_df)]
        if entrance_df is None:
            continue
        result_df = pd.DataFrame(reverse_pattern_enter_and_exit(ticker, entrance_df, exit_dfs))
        if result_df is not None:
            result_df["Stock"] = ticker
            total_results_df = pd.concat([total_results_df, result_df], ignore_index=True)
            total_results_df.to_csv(Path(project_path, "results/entrace_doji_long_evening_star_or_dark_cloud_cove.csv"))


    # # exit_dfs = [doji_short(pd.read_csv(download_stock(stock))),
    # #             evening_star(pd.read_csv(download_stock(stock))),
    # #             dark_cloud_cove(pd.read_csv(download_stock(stock)))]
    #
    #
    #
    # # pd.set_option('display.max_columns', None)
    # pd.DataFrame(reverse_pattern_enter_and_exit(ticker, entrance_df, exit_dfs)).to_csv("results.csv")
