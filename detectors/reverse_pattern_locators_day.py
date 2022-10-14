import numpy as np
import pandas as pd


# LONG
def doji_long(df):
    # TODO: update description and conditions for this method
    # TODO: before each step - explain what you're doing
    df["down_trend_2_days_before"] = np.where((df["High"].shift(1) < df["High"].shift(2)) & (df["Low"].shift(1) < df["Low"].shift(2)),
                                True, False)
    df["even_power_today"] = np.where(((df["Open"] - df["Open"] * 0.005) < df.Close) & (
            (df["Open"] + df["Open"] * 0.005) > df.Close), True, False)
    df["doji"] = np.where((df.down_trend_2_days_before == True) & (df.even_power_today == True), True, False)
    df["1_day_after_higher"] = np.where(
        (df.doji == True) & (df.shift(-1)["Low"] < df["High"]*1.005) &(df["High"]*1.005 < df.shift(-1)["High"]), True, False)
    df["entrance_date"] = df["Date"].shift(-1)
    df["entrance_price"] = df["High"]*1.005

    df = pd.DataFrame.copy(df[3:-1])

    entrance_df = df.loc[df["1_day_after_higher"] == True][["entrance_date", "entrance_price"]].reset_index()

    if len(entrance_df) == 0 or entrance_df.empty:
        return None
    else:
        return entrance_df


def dragonfly_doji(df):
    # TODO: finish this shit
    """
    Conditions for doji old:
    # TODO: update conditions
    1. The 'High' & 'Low' prices of 1st candle are correspondingly higher than the 2nd's candle
    2. The ratio between the 'Open' & 'Close' prices of the 3rd candle is 0.5% or lower
    3. 3rd day:
        a. If 'Close' < 'Open': The difference between the 'Low' price and the 'Close' price is greater than the
        difference between the 'High' price and the 'Close' prices times *long_tail_ratio* (TBD) AND the difference between the 'High' price and the 'Close' price is greater than the difference between the 'High'
    price and the 'Close' prices times *long_tail_ratio*
        b. If 'Open' < 'Close': The difference between the 'Low' price and the 'Open' price is greater than the difference between the 'High'
    price and the 'Open' prices times *long_tail_ratio* (TBD)
    4. The price range at the 4th candle includes (3rd day 'High')*1.005

    Given these conditions were met - Enter a trade at the 4th candle, buy at (3rd day 'High')*1.005

    :param df: stock price dataframe
    :return: pd.DataFrame contains the datetimes to enter a trade and their prices OR None if the paradigm wasn't
    found at all
    """
    up_tail_down_tail_ratio = 0.55

    df["down_trend_2_days_before"] = np.where((df["High"].shift(1) < df["High"].shift(2)) & (df["Low"].shift(1) < df["Low"].shift(2)),
                                True, False)
    df["even_power_today"] = np.where(((df["Open"] - df["Open"] * 0.005) < df.Close) & (
            (df["Open"] + df["Open"] * 0.005) > df.Close), True, False)
    # TODO: fix calculation. it's wrong now
    df["short_tail_up_long_tail_down"] = np.where(((df["Open"] < df["Close"]) & (((df["High"]-df["Close"])/(df["Open"]-df["Low"]) < up_tail_down_tail_ratio))) | ((df["Close"] < df["Open"]) & (((df["High"]-df["Open"])/(df["Close"]-df["Low"]) < up_tail_down_tail_ratio))), True, False)
    df["lower_low_than_day_before"] = np.where(df["Low"] < df["Low"].shift(1), True, False)
    df["dragonfly_doji"] = np.where(df.down_trend_2_days_before & df.even_power_today & df.lower_low_than_day_before &
                                    df.short_tail_up_long_tail_down, True, False)
    df["1_day_after_higher"] = np.where(
        (df.dragonfly_doji == True) & (df.shift(-1)["Low"] < df["High"]*1.005) & (df["High"]*1.005 < df.shift(-1)["High"]), True, False)
    df["entrance_date"] = df["Date"].shift(-1)
    df["entrance_price"] = df["High"]*1.005

    df = pd.DataFrame.copy(df[3:-1])

    entrance_df = df.loc[df["1_day_after_higher"] == True][["entrance_date", "entrance_price"]].reset_index()

    if len(entrance_df) == 0 or entrance_df.empty:
        return None
    else:
        return entrance_df


def doji_old(df):
    """
    Conditions for doji old:

    1. The 'High' & 'Low' prices of 1st candle are correspondingly higher than the 2nd's candle
    2. The ratio between the 'Open' & 'Close' prices of the 3rd candle is 0.5% or lower
    3. The 'High' & 'Low' prices of 4th candle are correspondingly lower than the 5th's candle

    Given these conditions were met - Enter a trade at the 6th candle

    :param df: stock price dataframe
    :return: pd.DataFrame contains the datetimes to enter a trade and their prices OR None if the paradigm wasn't
    found at all
    """
    df["down_trend_2_days_before"] = np.where((df["High"].shift(1) < df["High"].shift(2)) & (df["Low"].shift(1) < df["Low"].shift(2)),
                                True, False)
    df["even_power_today"] = np.where(((df["Open"] - df["Open"] * 0.005) < df.Close) & (
            (df["Open"] + df["Open"] * 0.005) > df.Close), True, False)
    df["doji"] = np.where((df.down_trend_2_days_before == True) & (df.even_power_today == True), True, False)
    df["up_trend_2_days_after"] = np.where(
        (df["High"].shift(-1) < df["High"].shift(-2)) & (df["Low"].shift(-1) < df["Low"].shift(-2)), True, False)
    df["up_trend_after_doji"] = np.where((df.doji == True) & (df.up_trend_2_days_after == True), True, False)
    df["entrance_date"] = df["Date"].shift(-3)
    df["entrance_price"] = df["Open"].shift(-3)

    df = pd.DataFrame.copy(df[3:-3])

    entrance_df = df.loc[df["up_trend_after_doji"] == True][["entrance_date", "entrance_price"]].reset_index()

    if len(entrance_df) == 0 or entrance_df.empty:
        return None
    else:
        return entrance_df


# SHORT
def doji_short(df):
    # TODO: update description and conditions for this method
    # TODO: before each step - explain what you're doing
    df["up_trend_2_days_before"] = np.where((df["High"].shift(1) > df["High"].shift(2)) & (df["Low"].shift(1) > df["Low"].shift(2)),
                                True, False)
    df["even_power_today"] = np.where(((df["Open"] - df["Open"] * 0.005) < df.Close) & (
            (df["Open"] + df["Open"] * 0.005) > df.Close), True, False)
    df["doji"] = np.where((df.up_trend_2_days_before == True) & (df.even_power_today == True), True, False)
    df["1_day_after_lower"] = np.where(
        (df.doji == True) & (df.shift(-1)["Low"] < df["Low"]*0.995) &(df["Low"]*0.995 < df.shift(-1)["High"]), True, False)
    df["entrance_date"] = df["Date"].shift(-1)
    df["entrance_price"] = df["Low"]*0.995

    df = pd.DataFrame.copy(df[3:-1])

    entrance_df = df.loc[df["1_day_after_lower"] == True][["entrance_date", "entrance_price"]].reset_index()

    if len(entrance_df) == 0 or entrance_df.empty:
        return None
    else:
        return entrance_df


def dark_cloud_cove(df):
    # TODO: update description and conditions for this method
    # TODO: before each step - explain what you're doing

    df["up_trend_1_days_before"] = np.where((df["High"] > df["High"].shift(1)) & (df["Low"] > df["Low"].shift(1)),
                                True, False)
    df["buyers_strong_today"] = np.where(df.shift(1)["Close"] > df.shift(1)["Open"], True, False)
    df["dark_cloud_cove"] = np.where((df.up_trend_1_days_before == True) & (df.buyers_strong_today == True) & (df.shift(-1)["Open"] > df.shift(-1)["Close"]), True, False)
    df["1_day_after_lower_than_75%_1_day_before"] = np.where(
        (df.dark_cloud_cove == True) & (df.shift(-1)["Low"] < ((df["Close"]-df["Open"])/4.0 +
                                                               df["Open"])) &
        (((df["Close"]-df["Open"])/4.0 + df["Open"]) < df.shift(-1)["High"]) &
        (df["Close"] < df.shift(-1)["Open"]), True, False)
    df["entrance_date"] = df["Date"].shift(-1)
    df["entrance_price"] = ((df["Close"]-df["Open"])/4.0 + df["Open"])

    df = pd.DataFrame.copy(df[3:-1])

    entrance_df = df.loc[df["1_day_after_lower_than_75%_1_day_before"] == True][["entrance_date", "entrance_price"]].reset_index()

    if len(entrance_df) == 0 or entrance_df.empty:
        return None
    else:
        return entrance_df


def evening_star(df):
    # TODO: update description and conditions for this method
    # TODO: before each step - explain what you're doing

    df["up_trend_2_days_before"] = np.where((df["High"].shift(1) > df["High"].shift(2)) & (df["Low"].shift(1) > df["Low"].shift(2)),
                                True, False)
    df["buyers_strong_1_day_before"] = np.where(df.shift(1)["Close"] > df.shift(1)["Open"], True, False)
    df["short_range_today"] = np.where(((df["Open"] > df["Close"]) & (df["Close"] > df.shift(1)["Close"])) | ((df["Close"] > df["Open"]) & (df["Open"] > df.shift(1)["Close"])), True, False)
    df["evening_star"] = np.where((df.up_trend_2_days_before == True) & (df.buyers_strong_1_day_before == True) & (df.short_range_today == True), True, False)
    df["1_day_after_lower_than_half_1_day_before"] = np.where(
        (df.evening_star == True) & (df.shift(-1)["Low"] < ((df.shift(1)["Close"]-df.shift(1)["Open"])/2.0 + df.shift(1)["Open"])) &(((df.shift(1)["Close"]-df.shift(1)["Open"])/2.0 + df.shift(1)["Open"]) < df.shift(-1)["High"]), True, False)
    df["entrance_date"] = df["Date"].shift(-1)
    df["entrance_price"] = ((df.shift(1)["Close"]-df.shift(1)["Open"])/2.0 + df.shift(1)["Open"])

    df = pd.DataFrame.copy(df[3:-1])

    entrance_df = df.loc[df["1_day_after_lower_than_half_1_day_before"] == True][["entrance_date", "entrance_price"]].reset_index()

    if len(entrance_df) == 0 or entrance_df.empty:
        return None
    else:
        return entrance_df


if __name__=="__main__":
    from os.path import dirname, abspath
    from pathlib import Path

    project_path = dirname(dirname(abspath(__file__)))
    stock_csv_path = Path(project_path, "stocks_max_daily_history/FB.csv")
    stock_df = pd.read_csv(stock_csv_path)
    pd.set_option('display.max_columns', None)
    print(evening_star(stock_df))
