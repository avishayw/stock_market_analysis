from utils.download_stock_csvs import download_stock, download_stock_minute_data
import pandas as pd
from datetime import datetime


def enter_reverse_pattern_exit_indicator(ticker, entrance_df, indicator, date):
    # TODO: edit so it will suit minute interval
    if len(entrance_df) == 0 or entrance_df.empty:
        return None

    stock_csv_path = download_stock_minute_data(ticker, date)
    stock_df = pd.read_csv(stock_csv_path)
    stock_df = indicator(stock_df)
    sell_df = stock_df.loc[stock_df["Sell"] == True]
    # TODO: remove debug
    pd.set_option('display.max_columns', None)
    print(sell_df)

    trades = []

    for day in range(len(entrance_df)):
        entrance_price = entrance_df.iloc[day]["entrance_price"]
        # Skip zeros
        if entrance_price == 0.0:
            continue
        entrance_time = str(entrance_df.iloc[day]["entrance_time"])
        relevant_exit_df = sell_df.loc[sell_df["Datetime"] > entrance_time]

        if not (len(relevant_exit_df)==0 or relevant_exit_df.empty):
            relevant_exit_df = relevant_exit_df.iloc[0]
            exit_price = relevant_exit_df["Open"]
            exit_time = relevant_exit_df["Datetime"]
            change_abs = exit_price - entrance_price
            trade_time_in_minutes = ((datetime.strptime(exit_time[:19], "%Y-%m-%d %H:%M:%S") - datetime.strptime(entrance_time[:19], "%Y-%m-%d %H:%M:%S")).total_seconds()) / 60
            if not entrance_price == 0.0:
                change_percentage = ((exit_price - entrance_price)/entrance_price)*100.0
            else:
                change_percentage = None
        else:
            last_date_df = pd.read_csv(download_stock(ticker)).iloc[-1]
            exit_price = last_date_df["Close"]
            exit_time = last_date_df["Date"]
            change_abs = exit_price - entrance_price
            trade_time_in_minutes = ((datetime.strptime(exit_time[:19], "%Y-%m-%d %H:%M:%S") - datetime.strptime(entrance_time[:19], "%Y-%m-%d %H:%M:%S")).total_seconds()) / 60
            if not entrance_price == 0.0:
                change_percentage = ((exit_price - entrance_price)/entrance_price)*100.0
            else:
                change_percentage = None

        trades.append({"entrance_time": entrance_time[:10], "entrace_price": entrance_price,
                       "exit_date": exit_time[:10], "exit_price": exit_price, "trade_time_in_minutes": trade_time_in_minutes,
                       "win": (change_abs > 0), "change": change_abs,
                       "change_%": change_percentage})

    return trades


if __name__ == "__main__":
    from locators.reverse_pattern_locators_minute import doji_long, doji_short, evening_star, dark_cloud_cove
    from indicators.momentum_indicators import awesome_oscillator
    from utils.get_all_snp_companies import get_all_snp_companies
    from utils.download_stock_csvs import download_stock_minute_data
    from os.path import dirname, abspath, exists
    from pathlib import Path
    from dateutil.relativedelta import relativedelta

    project_path = dirname(dirname(abspath(__file__)))

    stocks = get_all_snp_companies()
    today = datetime.utcnow()
    trade_date = datetime.utcnow() - relativedelta(months=1)

    while trade_date != today:
        for ticker in stocks:
            date = trade_date.strftime("%Y-%m-%d")
            path = download_stock_minute_data(ticker, date)
            if not path:
                print("path is None")
                continue

            stock_df = pd.read_csv(path)
            entrance_df = doji_long(stock_df)

            if entrance_df is None:
                print("entrace_df is None")
                continue

            # TODO: remove debug
            pd.set_option('display.max_columns', None)
            print(entrance_df)

            trades = enter_reverse_pattern_exit_indicator(ticker, entrance_df, awesome_oscillator, date)

            df = pd.DataFrame(trades)
            df.to_csv(Path(project_path, f"results/{ticker}_minute_enter_doji_exit_AO_{date}.csv"))

        trade_date = trade_date + relativedelta(days=1)

    # project_path = dirname(dirname(abspath(__file__)))
    # tickers = get_all_snp_companies()
    # total_results_df = pd.DataFrame([{"Stock": None, "entrance_time": None, "entrace_price": None, "exit_date": None, "exit_price": None, "trade_time_in_days": None, "win": None, "change": None, "change_%": None}])
    #
    # def date_to_datetime(row):
    #     return datetime.strptime(row["datetime"], "%Y-%m-%d")
    #
    # for ticker in tickers:
    #     print(f"{ticker}")
    #     path = download_stock(ticker)
    #     if not path:
    #         continue
    #     stock_df = pd.read_csv(download_stock(ticker))
    #     stock_df["datetime"] = pd.to_datetime(stock_df["Date"])
    #     stock_df = stock_df.loc[stock_df["datetime"] > datetime.utcnow() - relativedelta(years=1)]
    #     stock_df.drop(columns=['datetime'])
    #     entrance_df = doji_long(stock_df)
    #     if entrance_df is None:
    #         continue
    #     result_df = pd.DataFrame(enter_reverse_pattern_exit_indicator(ticker, entrance_df, awesome_oscillator_indicator))
    #     if result_df is not None:
    #         result_df["Stock"] = ticker
    #         total_results_df = pd.concat([total_results_df, result_df], ignore_index=True)
    #         total_results_df.to_csv(Path(project_path, "results/entrace_doji_long_exit_awesome_oscillator_sell_signal.csv"))
