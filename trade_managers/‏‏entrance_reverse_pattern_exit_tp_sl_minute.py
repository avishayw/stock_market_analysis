from detectors.reverse_pattern_locators_day import doji_long
from utils.download_stock_csvs import download_stock_day
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import statistics
import time


def exit_tp_sl(ticker, entrance_df, tp_percentage, sl_percentage):
    # TODO: edit so it will suit minute interval
    df = pd.read_csv(download_stock_day(ticker))

    start = time.time()

    if len(entrance_df) == 0 or entrance_df.empty:
        return None

    worst_case_losses = 0
    worst_case_profits = 0
    best_case_losses = 0
    best_case_profits = 0
    dates = {}

    total_trade_time_list = []
    for day in range(len(entrance_df)):
        price = entrance_df.iloc[day]["entrance_price"]
        # Skip zeros
        if price == 0.0:
            continue
        entrance_date = str(entrance_df.iloc[day]["entrance_date"])[:10]
        trade_days_counter = 0
        while True:
            date_df = pd.DataFrame()
            sanity = 1
            while date_df.empty:
                date = entrance_df.iloc[day]["entrance_date"] + timedelta(days=trade_days_counter)
                date_df = df.loc[df["Date"] == date]
                trade_days_counter += 1
                sanity += 1
                if sanity == 7:
                    break
            if sanity == 7:
                break
            high = date_df.iloc[0]["High"]
            low = date_df.iloc[0]["Low"]
            price_range = np.arange(low, high, 0.1)
            price_range_loss = ((price_range - price) / price) * 100 <= sl_percentage * -1.0
            price_range_profit = ((price_range - price) / price) * 100 >= tp_percentage
            if True in price_range_loss and True in price_range_profit:
                worst_case_losses += 1
                best_case_profits += 1
                dates[entrance_date] = False
                break
            elif True in price_range_loss:
                worst_case_losses += 1
                best_case_losses += 1
                dates[entrance_date] = False
                break
            elif True in price_range_profit:
                worst_case_profits += 1
                best_case_profits += 1
                dates[entrance_date] = True
                break
            else:
                trade_days_counter += 1
        total_trade_time_list.append(trade_days_counter)

    summary = {"Best case profits ratio": float(best_case_profits) / float(len(entrance_df)),
               "Worst case profits ratio": float(worst_case_profits) / float(len(entrance_df)),
               "Best case losses ratio": float(best_case_losses) / float(len(entrance_df)),
               "Worst case losses ratio": float(worst_case_losses) / float(len(entrance_df)),
               "Max. trade period in days": max(total_trade_time_list),
               "Min. trade period in days": min(total_trade_time_list),
               "Avg. trade period in days": statistics.mean(total_trade_time_list),
               "Median trade period in days": statistics.median(total_trade_time_list),
               "Total exploration time": time.time() - start}

    return summary, dates
