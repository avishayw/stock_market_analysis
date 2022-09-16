import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.paths import save_under_results_path
import json
from strategy_statistics.strategy_statistics import all_statistics_dict


def trading_simulator(df, trades_at_a_time=4, start_datetime=None, end_datetime=None):
    """
    Not quite simulating because there is no accounting for the share price and the number of shares
    """
    df = df.copy()
    df.sort_values(by=['enter_date'], inplace=True)
    df['enter_datetime'] = pd.to_datetime(df['enter_date'])
    df['exit_datetime'] = pd.to_datetime(df['exit_date'])

    if start_datetime:
        df = df.loc[df['enter_datetime'] >= start_datetime]
    if end_datetime:
        df = df.loc[df['exit_datetime'] <= end_datetime]

    i = 0
    active_trades = 0

    simulated_dict_list = []
    # simulated_df = pd.DataFrame(columns=(df.columns.tolist()))
    # print(simulated_df)
    exit_datetimes = []

    while i < len(df):
        if active_trades < trades_at_a_time:
            active_trades += 1
            # print(df.iloc[i])
            simulated_dict_list.append(df.iloc[i].to_dict())
            # simulated_df = pd.concat([simulated_df, df.iloc[i]], ignore_index=True, axis=1)
            # print(simulated_df)
            exit_datetimes.append(df.iloc[i]['exit_datetime'])
            exit_datetimes.sort(reverse=True)
        elif df.iloc[i]['enter_datetime'] > exit_datetimes[-1]:
            exit_datetimes.pop()
            exit_datetimes.append(df.iloc[i]['exit_datetime'])
            exit_datetimes.sort(reverse=True)
            simulated_dict_list.append(df.iloc[i].to_dict())
        i += 1

    simulated_df = pd.DataFrame(simulated_dict_list)

    return simulated_df


csv_path = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\ma_roc_and_efficiency_ratio_trading_10-09-2022-23-10-49_all_trades.csv"
df = pd.read_csv(csv_path)

final_datetime = datetime.now()

relative_day_jumps = [30, 60, 150, 200, 365, 730, 1460]

tradeing_periods = {}

for day_jump in relative_day_jumps:
    start_datetime = datetime(2006, 1, 1, 0, 0, 0)
    end_datetime = start_datetime + relativedelta(days=day_jump)
    tradeing_periods[day_jump] = {}
    while end_datetime < final_datetime:
        start_datetime_str = start_datetime.strftime('%d-%m-%Y')
        end_datetime_str = end_datetime.strftime('%d-%m-%Y')
        test_df = df.copy()
        clean_df = trading_simulator(test_df, start_datetime=start_datetime, end_datetime=end_datetime)

        if len(clean_df) <1:
            tradeing_periods[day_jump][f'{start_datetime_str}_to_{end_datetime_str}'] = 'empty'
        else:
            tradeing_periods[day_jump][f'{start_datetime_str}_to_{end_datetime_str}'] = all_statistics_dict(clean_df)

        with open(fr"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\ma_roc_er_splitted\trading_periods_stats.json", 'w') as f:
            json.dump(tradeing_periods, f, indent=4)

        clean_df.to_csv(fr"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\ma_roc_er_splitted\{start_datetime_str}_to_{end_datetime_str}.csv")
        start_datetime = start_datetime + relativedelta(days=day_jump)
        end_datetime = end_datetime + relativedelta(days=day_jump)

# commulative_change_list = (clean_df['change%']/100 + 1).tolist()
# print(len(commulative_change_list))
# commulative_change_list = list(filter((0.0).__ne__, commulative_change_list))
# print(len(commulative_change_list))
# commulative_change_series = pd.Series(commulative_change_list)
# print(commulative_change_series.prod())
