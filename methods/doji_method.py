from stock import Stock
from datetime import datetime, timedelta
import time
import numpy as np
import statistics
import pandas as pd

def doji_method(ticker, sl_percentage, tp_percentage):
    """
    This function will return the **method success rate** with the given stock history, STOP-LOSS percentage,
    TAKE-PROFIT percentage and the maximum amount of days for the trade

    Doji Method:

    1. Check for down trend, i.e. high & low prices of day x-1 are lower then the correspondent high & low prices
    of day x-2. If passed - we have a down trend
    2. Check for buyers-sellers balance i.e. open & close prices of day x are of max. difference of 0.5%. If passed
    - we have Doji paradigm."
    3. Check for up trend, i.e. high & low prices of day x+2 are higher then the correspondent high & low prices
    of day x+1. If passed - we have an up trend"
    4. Check if there has been a positive change of 5% within 10 days period after the paradigm was identified.
    If so the paradigm succeeded.

    :param ticker: str - Symbol/ticker of the stock
    :param sl_percentage: float - POSITIVE percentage. Example: 5.0
    :param tp_percentage: float - POSITIVE percentage. Example: 10.0
    :return: dict - Best case profits ratio, Worst case profits ratio, Best case losses ratio, Worst case losses ratio,
    Max. trade period in days, Min. trade period in days, Avg. trade period in days, Median trade period in days,
    Total exploration time
    """
    start = time.time()

    stock = Stock(ticker)
    df = stock.max_daily_history()

    df["down_trend"] = np.where((df["High"].shift(1) < df["High"].shift(2)) & (df["Low"].shift(1) < df["Low"].shift(2)),
                                True, False)
    df["even_power"] = np.where((df.down_trend == True) & (((df["Open"] - df["Open"] * 0.005)) < df.Close) & (
                ((df["Open"] + df["Open"] * 0.005)) > df.Close), True, False)
    df["doji"] = np.where((df.down_trend == True) & (df.even_power == True), True, False)
    df["up_trend"] = np.where(
        (df["High"].shift(-1) < df["High"].shift(-2)) & (df["Low"].shift(-1) < df["Low"].shift(-2)), True, False)
    df["up_trend_after_doji"] = np.where((df.doji == True) & (df.up_trend == True), True, False)
    df["entrance_date"] = df["Date"].shift(-3)
    df["entrance_price"] = df["Open"].shift(-3)

    df = pd.DataFrame.copy(df[3:-3])

    entrance_df = df.loc[df["up_trend_after_doji"] == True][["entrance_date", "entrance_price"]].reset_index()

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
            price_range_loss = ((price_range - price) / price) * 100 <= sl_percentage*-1.0
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

    summary = {"Best case profits ratio": float(best_case_profits)/float(len(entrance_df)),
               "Worst case profits ratio": float(worst_case_profits) / float(len(entrance_df)),
               "Best case losses ratio": float(best_case_losses) / float(len(entrance_df)),
               "Worst case losses ratio": float(worst_case_losses) / float(len(entrance_df)),
               "Max. trade period in days": max(total_trade_time_list),
               "Min. trade period in days": min(total_trade_time_list),
               "Avg. trade period in days": statistics.mean(total_trade_time_list),
               "Median trade period in days": statistics.median(total_trade_time_list),
               "Total exploration time": time.time() - start}

    return summary, dates


if __name__=="__main__":

    stocks = ['AAPL', 'FB']

    total_summary = {"Best case profits ratio": [],
               "Worst case profits ratio": [],
               "Best case losses ratio": [],
               "Worst case losses ratio": [],
               "Max. trade period in days": [],
               "Min. trade period in days": [],
               "Avg. trade period in days": [],
               "Median trade period in days": [],
               "Total exploration time": []}

    sl = 5.0
    tp = 10.0

    for stock in stocks:
        result = doji_method(stock, sl, tp)
        for key in total_summary.keys():
            total_summary[key].append(result[key])

    print(total_summary)
    # import time
    # import numpy as np
    # import pandas as pd
    # from datetime import datetime,timedelta
    # import statistics

    # start = time.time()
    # pd.set_option('display.max_columns', None)
    # ticker = 'FB'
    # stock = Stock(ticker)
    # df = stock.max_daily_history()
    #
    #
    # df["down_trend"] = np.where((df["High"].shift(1) < df["High"].shift(2)) & (df["Low"].shift(1) < df["Low"].shift(2)), True, False)
    # df["even_power"] = np.where((df.down_trend == True) & (((df["Open"] - df["Open"]*0.005)) < df.Close) & (((df["Open"] + df["Open"]*0.005)) > df.Close), True, False)
    # df["doji"] = np.where((df.down_trend == True) & (df.even_power == True), True, False)
    # df["up_trend"] =  np.where((df["High"].shift(-1) < df["High"].shift(-2)) & (df["Low"].shift(-1) < df["Low"].shift(-2)), True, False)
    # df["up_trend_after_doji"] = np.where((df.doji == True) & (df.up_trend == True), True, False)
    # df["entrace_date"] = df["Date"].shift(3)
    # df["entrace_price"] = df["Open"].shift(3)
    #
    # entrance_df = df.loc[df["up_trend_after_doji"] == True][["Date", "Open"]].reset_index()
    #
    # worst_case_losses = 0
    # worst_case_profits = 0
    # best_case_losses = 0
    # best_case_profits = 0
    #
    # total_trade_time_list = []
    # for day in range(len(entrance_df)):
    #     price = entrance_df.iloc[day]["Open"]
    #     trade_days_counter = 1
    #     i = 0
    #     while True:
    #         date_df = pd.DataFrame()
    #         while date_df.empty:
    #             date = entrance_df.iloc[day]["Date"] + timedelta(days=i)
    #             date_df = df.loc[df["Date"] == date]
    #             i += 1
    #         high = date_df.iloc[0]["High"]
    #         low = date_df.iloc[0]["Low"]
    #         price_range = np.arange(low, high, 0.1)
    #         price_range_loss = ((price_range-price)/price)*100 <= -5.0
    #         price_range_profit = ((price_range - price) / price) * 100 >= 10.0
    #         if True in price_range_loss and True in price_range_profit:
    #             worst_case_losses += 1
    #             best_case_profits += 1
    #             break
    #         elif True in price_range_loss:
    #             worst_case_losses += 1
    #             best_case_losses += 1
    #             break
    #         elif True in price_range_profit:
    #             worst_case_profits += 1
    #             best_case_profits += 1
    #             break
    #         else:
    #             trade_days_counter += 1
    #     total_trade_time_list.append(trade_days_counter)
    #
    #
    # print(f"Best case profits ratio: {float(best_case_profits)/float(len(entrance_df))}")
    # print(f"Worst case profits ratio: {float(worst_case_profits) / float(len(entrance_df))}")
    # print(f"Best case losses ratio: {float(best_case_losses) / float(len(entrance_df))}")
    # print(f"Worst case losses ratio: {float(worst_case_losses) / float(len(entrance_df))}")
    # print(f"Max. trade period in days: {max(total_trade_time_list)}")
    # print(f"Min. trade period in days: {min(total_trade_time_list)}")
    # print(f"Avg. trade period in days: {statistics.mean(total_trade_time_list)}")
    # print(f"Median trade period in days: {statistics.median(total_trade_time_list)}")
    # print(f"Total exploration time: {time.time() - start}")
    # # print(float(none)/float(len(entrance_df)))






# create new columns derived from existing columns
# https://pandas.pydata.org/docs/getting_started/intro_tutorials/05_add_columns.html

# Shift column in pandas
# https://stackoverflow.com/questions/20095673/shift-column-in-pandas-dataframe-up-by-one
