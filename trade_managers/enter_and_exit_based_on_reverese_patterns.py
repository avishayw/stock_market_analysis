from utils.download_stock_csvs import download_stock
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
            last_date_df = pd.read_csv(download_stock(ticker)).iloc[-1]
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
    from locators.reverse_pattern_locators import doji_long, doji_short, evening_star, dark_cloud_cove
    from utils.get_all_snp_companies import get_all_snp_companies

    tickers = get_all_snp_companies()
    print()
    for ticker in tickers:
        cap = 5000
        entrance_df = doji_long(pd.read_csv(download_stock(ticker)))
        exit_dfs = [evening_star(pd.read_csv(download_stock(ticker))),
                    dark_cloud_cove(pd.read_csv(download_stock(ticker)))]
        result_df = pd.DataFrame(reverse_pattern_enter_and_exit(ticker, entrance_df, exit_dfs))
        if result_df:
            changes = result_df["change_%"].to_list()
            for change in changes:
                cap = cap*(1 + (change/100.0))
            print(f"Stock: {ticker}\nFinal cap: {cap}")
            result_df.to_csv(f"{ticker}_results.csv")


    # # exit_dfs = [doji_short(pd.read_csv(download_stock(stock))),
    # #             evening_star(pd.read_csv(download_stock(stock))),
    # #             dark_cloud_cove(pd.read_csv(download_stock(stock)))]
    #
    #
    #
    # # pd.set_option('display.max_columns', None)
    # pd.DataFrame(reverse_pattern_enter_and_exit(ticker, entrance_df, exit_dfs)).to_csv("results.csv")
