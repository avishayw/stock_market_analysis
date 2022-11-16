"""
Using the method for measuring movements (playground/measuring_movements_with_er.py):
1. Measure weekly movement using efficiency ratio of minimum 0.7.
2. If 3 weeks completed with the same movement, and using the movement's weekly prices - measure the weekly change
    by creating a straight line. Compare the weekly change to weekly ATR of period TBD (optimization parameter?).
3. Given the weekly change given by the movement implies clear trend (HOW TO MEASURE?), up or down, enter a position the
    same direction of the movement.
4. Exit the position once the movement is finished (the week's weekend in which the movement efficiency ratio becomes
    noisy, movement_end_idx.e. less than 0.7.
"""
from utils.download_stock_csvs import download_stock_day, download_stock_week
import pandas as pd
import os
from dateutil.relativedelta import relativedelta
import warnings
warnings.filterwarnings("ignore")


class NoConditionError(Exception):
    pass


class EfficiencyCalculationError(Exception):
    pass


def line(sample_df, source):
    y1 = sample_df.iloc[-1][source]
    y0 = sample_df.iloc[0][source]
    x0 = 0
    x1 = len(sample_df) - 1
    if x1-x0 == 0:
        return None
    m = (y1-y0)/(x1-x0)
    c = y1 - m*x1
    return m, c


def measure_er(sample_df, src='Close'):
    net_change = abs(sample_df.iloc[-1][src] - sample_df.iloc[0][src])
    sum_of_individual_changes = ((sample_df[src] - sample_df.shift(1)[src]).abs()).sum()
    if sum_of_individual_changes == 0:
        if net_change == 0:
            return 1.0
        else:
            raise EfficiencyCalculationError("Efficiency ratio: Sum of individual changes is zero but the net change is not.")
    return net_change / sum_of_individual_changes


def trade_weekly_movement(ticker, er_th=0.7):

    # For this strategy I want the most updated dataframes for weekly_df and daily_df to be synchronized (date wise)
    daily_df_path = download_stock_day(ticker)
    weekly_df_path = download_stock_week(ticker)
    os.remove(daily_df_path)
    os.remove(weekly_df_path)

    weekly_df = pd.read_csv(download_stock_week(ticker)).reset_index()
    daily_df = pd.read_csv(download_stock_day(ticker)).reset_index()
    # TODO: remove print
    print(weekly_df.head())
    print(weekly_df.tail())
    print(daily_df.head())
    print(daily_df.tail())

    weekly_df['Date'] = weekly_df['Date'].map(lambda x: str(x).split(' ')[0])
    weekly_df['Datetime'] = pd.to_datetime(weekly_df['Date'])

    daily_df['Date'] = daily_df['Date'].map(lambda x: str(x).split(' ')[0])
    daily_df['Datetime'] = pd.to_datetime(daily_df['Date'])

    movement_id = 0
    movement_start_idx = 0
    movement_end_idx = movement_start_idx + 3
    source = 'Close'
    long_position = False
    short_position = False
    trades = []

    while movement_end_idx < len(weekly_df):
        movement_df = weekly_df[movement_start_idx:movement_end_idx].copy()
        movement_efficiency_ratio = measure_er(movement_df, source)
        if movement_efficiency_ratio < er_th:
            # TODO: Question: what do you do if the efficiency ratio is below ratio but the movement is in the direction
            #  of the trend? REQUIRES THINKING
            if long_position or short_position:
                # TODO: check the dates thing again
                # weekend_date = movement_df.iloc[-1]['Datetime']
                week_date = movement_df.iloc[-1]['Datetime']
                weekend_date = week_date + relativedelta(days=(4 - week_date.weekday()))
                if weekend_date == weekly_df.iloc[-1]['Datetime']:  # Final week
                    break
                exit_series = daily_df.loc[daily_df['Datetime'] > weekend_date].iloc[0].copy()
                exit_price = exit_series['Open']
                exit_date = exit_series['Date']
                if long_position:
                    change = (exit_price/enter_price - 1)*100.0
                    trade_dict = {'symbol': ticker,
                                  'type': 'long',
                                  'enter_date': enter_date,
                                  'enter_price': enter_price,
                                  'exit_date': exit_date,
                                  'exit_price': exit_price,
                                  'win': exit_price > enter_price,
                                  'change%': change,
                                  'movement_id': movement_id,
                                  'movement_slope': slope,
                                  'movement_intercept': intercept}
                    print(trade_dict)
                    trades.append(trade_dict)
                    long_position = False
                elif short_position:
                    change = (exit_price / enter_price - 1) * -100.0
                    trade_dict = {'symbol': ticker,
                                  'type': 'short',
                                  'enter_date': enter_date,
                                  'enter_price': enter_price,
                                  'exit_date': exit_date,
                                  'exit_price': exit_price,
                                  'win': exit_price < enter_price,
                                  'change%': change,
                                  'movement_id': movement_id,
                                  'movement_slope': slope,
                                  'movement_intercept': intercept}
                    print(trade_dict)
                    trades.append(trade_dict)
                    short_position = False
            movement_id += 1
            movement_start_idx = movement_end_idx - 1
            # Changed
            movement_end_idx = movement_start_idx + 3
            # movement_end_idx = movement_start_idx + 2
        elif movement_efficiency_ratio >= er_th:
            if long_position or short_position:
                updated_slope, updated_intercept = line(movement_df, source)
                weekly_df.loc[movement_end_idx - 1, 'movement_id'] = movement_id
                weekly_df.loc[movement_end_idx - 1, 'movement_current_er'] = movement_efficiency_ratio
                weekly_df.loc[movement_end_idx - 1, 'movement_slope'] = slope
                weekly_df.loc[movement_end_idx - 1, 'movement_intercept'] = intercept
                weekly_df.loc[movement_end_idx - 1, 'movement_price'] = slope * (movement_end_idx - movement_start_idx - 1) + intercept
                weekly_df.loc[movement_end_idx - 1, 'movement_updated_slope'] = updated_slope
                weekly_df.loc[movement_end_idx - 1, 'movement_updated_intercept'] = updated_intercept
                weekly_df.loc[movement_end_idx - 1, 'movement_updated_price'] = updated_slope * (
                            movement_end_idx - movement_start_idx - 1) + updated_intercept
                movement_end_idx += 1
                continue
            else:
                slope, intercept = line(movement_df, source)
                for idx in range(movement_start_idx, movement_end_idx):
                    weekly_df.loc[idx, 'movement_id'] = movement_id
                    weekly_df.loc[idx, 'movement_current_er'] = movement_efficiency_ratio
                    weekly_df.loc[idx, 'movement_slope'] = slope
                    weekly_df.loc[idx, 'movement_intercept'] = intercept
                    weekly_df.loc[idx, 'movement_price'] = slope*(idx-movement_start_idx) + intercept
                # TODO: check the dates thing again
                # weekend_date = movement_df.iloc[-1]['Datetime']
                week_date = movement_df.iloc[-1]['Datetime']
                weekend_date = week_date + relativedelta(days=(4 - week_date.weekday()))
                entrance_series = daily_df.loc[daily_df['Datetime'] > weekend_date].iloc[0].copy()
                enter_price = entrance_series['Open']
                enter_date = entrance_series['Date']
                if slope > 0:
                    long_position = True
                elif slope < 0:
                    short_position = True
                movement_end_idx += 1
        else:
            raise NoConditionError("None of the conditions met")

    return trades, weekly_df


def trade_weekly_movement_v2(ticker, er_th=0.7):
    """
    In this version I want to enter a position once a movement with sufficient efficiency ratio is detected, but exit
    only if a new movement is detected with a slope in the opposite direction of the trade.
    """

    # For this strategy I want the most updated dataframes for weekly_df and daily_df to be synchronized (date wise)
    daily_df_path = download_stock_day(ticker)
    weekly_df_path = download_stock_week(ticker)
    os.remove(daily_df_path)
    os.remove(weekly_df_path)

    weekly_df = pd.read_csv(download_stock_week(ticker)).reset_index()
    daily_df = pd.read_csv(download_stock_day(ticker)).reset_index()
    # TODO: remove print
    print(weekly_df.head())
    print(weekly_df.tail())
    print(daily_df.head())
    print(daily_df.tail())

    weekly_df['Date'] = weekly_df['Date'].map(lambda x: str(x).split(' ')[0])
    weekly_df['Datetime'] = pd.to_datetime(weekly_df['Date'])

    daily_df['Date'] = daily_df['Date'].map(lambda x: str(x).split(' ')[0])
    daily_df['Datetime'] = pd.to_datetime(daily_df['Date'])

    movement_id = 0
    movement_start_idx = 0
    movement_end_idx = movement_start_idx + 3
    source = 'Close'
    long_position = False
    short_position = False
    trades = []

    while movement_end_idx < len(weekly_df):
        movement_df = weekly_df[movement_start_idx:movement_end_idx].copy()
        movement_efficiency_ratio = measure_er(movement_df, source)
        if movement_efficiency_ratio < er_th:
            # TODO: Question: what do you do if the efficiency ratio is below ratio but the movement is in the direction
            #  of the trend? REQUIRES THINKING
            # if long_position or short_position:
            #     # TODO: check the dates thing again
            #     # weekend_date = movement_df.iloc[-1]['Datetime']
            #     week_date = movement_df.iloc[-1]['Datetime']
            #     weekend_date = week_date + relativedelta(days=(4 - week_date.weekday()))
            #     if weekend_date == weekly_df.iloc[-1]['Datetime']:  # Final week
            #         break
            #     exit_series = daily_df.loc[daily_df['Datetime'] > weekend_date].iloc[0].copy()
            #     exit_price = exit_series['Open']
            #     exit_date = exit_series['Date']
            #     if long_position:
            #         change = (exit_price/enter_price - 1)*100.0
            #         trade_dict = {'symbol': ticker,
            #                       'type': 'long',
            #                       'enter_date': enter_date,
            #                       'enter_price': enter_price,
            #                       'exit_date': exit_date,
            #                       'exit_price': exit_price,
            #                       'win': exit_price > enter_price,
            #                       'change%': change,
            #                       'movement_id': movement_id,
            #                       'movement_slope': slope,
            #                       'movement_intercept': intercept}
            #         print(trade_dict)
            #         trades.append(trade_dict)
            #         long_position = False
            #     elif short_position:
            #         change = (exit_price / enter_price - 1) * -100.0
            #         trade_dict = {'symbol': ticker,
            #                       'type': 'short',
            #                       'enter_date': enter_date,
            #                       'enter_price': enter_price,
            #                       'exit_date': exit_date,
            #                       'exit_price': exit_price,
            #                       'win': exit_price < enter_price,
            #                       'change%': change,
            #                       'movement_id': movement_id,
            #                       'movement_slope': slope,
            #                       'movement_intercept': intercept}
            #         print(trade_dict)
            #         trades.append(trade_dict)
            #         short_position = False
            movement_id += 1
            movement_start_idx = movement_end_idx - 1
            # Changed
            movement_end_idx = movement_start_idx + 3
            # movement_end_idx = movement_start_idx + 2
        elif movement_efficiency_ratio >= er_th:
            if long_position or short_position:
                updated_slope, updated_intercept = line(movement_df, source)
                if (updated_slope > 0 > slope) or (updated_slope < 0 < slope):
                    week_date = movement_df.iloc[-1]['Datetime']
                    weekend_date = week_date + relativedelta(days=(4 - week_date.weekday()))
                    if weekend_date == weekly_df.iloc[-1]['Datetime']:  # Final week
                        break
                    exit_series = daily_df.loc[daily_df['Datetime'] > weekend_date].iloc[0].copy()
                    exit_price = exit_series['Open']
                    exit_date = exit_series['Date']
                    if long_position:
                        change = (exit_price/enter_price - 1)*100.0
                        trade_dict = {'symbol': ticker,
                                      'type': 'long',
                                      'enter_date': enter_date,
                                      'enter_price': enter_price,
                                      'exit_date': exit_date,
                                      'exit_price': exit_price,
                                      'win': exit_price > enter_price,
                                      'change%': change,
                                      'movement_id': movement_id,
                                      'movement_initial_slope': slope,
                                      'movement_initial_intercept': intercept,
                                      'movement_updated_slope': updated_slope,
                                      'movement_updated_intercept': updated_intercept}
                        print(trade_dict)
                        trades.append(trade_dict)
                        long_position = False
                    elif short_position:
                        change = (exit_price / enter_price - 1) * -100.0
                        trade_dict = {'symbol': ticker,
                                      'type': 'short',
                                      'enter_date': enter_date,
                                      'enter_price': enter_price,
                                      'exit_date': exit_date,
                                      'exit_price': exit_price,
                                      'win': exit_price < enter_price,
                                      'change%': change,
                                      'movement_id': movement_id,
                                      'movement_initial_slope': slope,
                                      'movement_initial_intercept': intercept,
                                      'movement_updated_slope': updated_slope,
                                      'movement_updated_intercept': updated_intercept}
                        print(trade_dict)
                        trades.append(trade_dict)
                        short_position = False
                else:
                    weekly_df.loc[movement_end_idx - 1, 'movement_id'] = movement_id
                    weekly_df.loc[movement_end_idx - 1, 'movement_current_er'] = movement_efficiency_ratio
                    weekly_df.loc[movement_end_idx - 1, 'movement_slope'] = slope
                    weekly_df.loc[movement_end_idx - 1, 'movement_intercept'] = intercept
                    weekly_df.loc[movement_end_idx - 1, 'movement_price'] = slope * (movement_end_idx - movement_start_idx - 1) + intercept
                    weekly_df.loc[movement_end_idx - 1, 'movement_updated_slope'] = updated_slope
                    weekly_df.loc[movement_end_idx - 1, 'movement_updated_intercept'] = updated_intercept
                    weekly_df.loc[movement_end_idx - 1, 'movement_updated_price'] = updated_slope * (
                                movement_end_idx - movement_start_idx - 1) + updated_intercept
                    movement_end_idx += 1
                    continue
            else:
                slope, intercept = line(movement_df, source)
                for idx in range(movement_start_idx, movement_end_idx):
                    weekly_df.loc[idx, 'movement_id'] = movement_id
                    weekly_df.loc[idx, 'movement_current_er'] = movement_efficiency_ratio
                    weekly_df.loc[idx, 'movement_slope'] = slope
                    weekly_df.loc[idx, 'movement_intercept'] = intercept
                    weekly_df.loc[idx, 'movement_price'] = slope*(idx-movement_start_idx) + intercept
                # TODO: check the dates thing again
                # weekend_date = movement_df.iloc[-1]['Datetime']
                week_date = movement_df.iloc[-1]['Datetime']
                weekend_date = week_date + relativedelta(days=(4 - week_date.weekday()))
                entrance_series = daily_df.loc[daily_df['Datetime'] > weekend_date].iloc[0].copy()
                enter_price = entrance_series['Open']
                enter_date = entrance_series['Date']
                if slope > 0:
                    long_position = True
                elif slope < 0:
                    short_position = True
                movement_end_idx += 1
        else:
            raise NoConditionError("None of the conditions met")

    return trades, weekly_df


if __name__ == '__main__':
    from utils.paths import save_under_results_path
    from utils.in_sample_tickers import IN_SAMPLE_TICKERS

    ticker = 'META'
    efficiency_ratio_threshold = 0.7
    trades, df = trade_weekly_movement_v2(ticker, er_th=efficiency_ratio_threshold)
    df.to_csv(save_under_results_path(f'{ticker}_movement_df_er_th_{efficiency_ratio_threshold}_v2.csv'))
    pd.DataFrame(trades).to_csv(save_under_results_path(f'weekly_noise_reduced_trend_trading_v2_er_th_{efficiency_ratio_threshold}_{ticker}_trades.csv'))
