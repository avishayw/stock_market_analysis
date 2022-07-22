from utils.download_stock_csvs import download_stock
import pandas as pd
from datetime import datetime


def enter_reverse_pattern_exit_indicator(ticker, entrance_df, indicator):

    if len(entrance_df) == 0 or entrance_df.empty:
        return None

    stock_csv_path = download_stock(ticker)
    stock_df = pd.read_csv(stock_csv_path)
    stock_df = indicator(stock_df)
    sell_df = stock_df.loc[stock_df["Sell"] == True]

    trades = []

    for day in range(len(entrance_df)):
        entrance_price = entrance_df.iloc[day]["entrance_price"]
        # Skip zeros
        if entrance_price == 0.0:
            continue
        entrance_date = str(entrance_df.iloc[day]["entrance_date"])
        relevant_exit_df = sell_df.loc[sell_df["Date"] > entrance_date]

        if not (len(relevant_exit_df)==0 or relevant_exit_df.empty):
            relevant_exit_df = relevant_exit_df.iloc[0]
            exit_price = relevant_exit_df["Open"]
            exit_date = relevant_exit_df["Date"]
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


if __name__ == "__main__":
    from locators.reverse_pattern_locators_day import doji_long, doji_short, evening_star, dark_cloud_cove
    from indicators.momentum_indicators import awesome_oscillator
    from utils.get_all_snp_companies import get_all_snp_companies
    from os.path import dirname, abspath, exists
    from pathlib import Path
    from dateutil.relativedelta import relativedelta

    project_path = dirname(dirname(abspath(__file__)))
    tickers = get_all_snp_companies()
    total_results_df = pd.DataFrame([{"Stock": None, "entrance_date": None, "entrace_price": None, "exit_date": None, "exit_price": None, "trade_time_in_days": None, "win": None, "change": None, "change_%": None}])

    def date_to_datetime(row):
        return datetime.strptime(row["datetime"], "%Y-%m-%d")

    for ticker in tickers:
        print(f"{ticker}")
        path = download_stock(ticker)
        if not path:
            continue
        stock_df = pd.read_csv(download_stock(ticker))
        stock_df["datetime"] = pd.to_datetime(stock_df["Date"])
        stock_df = stock_df.loc[stock_df["datetime"] > datetime.utcnow() - relativedelta(years=1)]
        stock_df.drop(columns=['datetime'])
        entrance_df = doji_long(stock_df)
        if entrance_df is None:
            continue
        result_df = pd.DataFrame(enter_reverse_pattern_exit_indicator(ticker, entrance_df, awesome_oscillator))
        if result_df is not None:
            result_df["Stock"] = ticker
            total_results_df = pd.concat([total_results_df, result_df], ignore_index=True)
            total_results_df.to_csv(Path(project_path, "results/entrace_doji_long_exit_awesome_oscillator_sell_signal.csv"))
