"""
Support and resistance levels:
1. Start from monthly prices levels.
2. Then find weekly levels, filtering by monthly levels.
3. Then find daily levels, filtering by weekly levels.

Alerts:
Monthly levels alerts:
1. Alert for the closest monthly resistance with difference of up to 10% from last daily price.
2. Alert for the closest monthly support with difference of up to 10% from last daily price.

Weekly levels alerts:
1. Alert for the closest weekly resistance with difference of up to 8% from last daily price.
2. Alert for the closest weekly support with difference of up to 8% from last daily price.

Daily levels alerts:
1. Alert for the closest daily resistance with difference of up to 5% from last daily price.
2. Alert for the closest daily support with difference of up to 5% from last daily price.
"""
from detectors.support_and_resistance import fractal_candlestick_pattern_method, window_shifting_method
from utils.download_stock_csvs import download_stock_day, download_stock_week, download_stock_month
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import warnings
warnings.filterwarnings("ignore")


def now():
    return datetime.now().astimezone(pytz.timezone('Asia/Jerusalem')).strftime('%Y-%m-%d %H:%M:%S')


def total_stock_levels(ticker):
    daily_df = pd.read_csv(download_stock_day(ticker))[-1008:]  # 4 years
    weekly_df = pd.read_csv(download_stock_week(ticker))[-223:]  # 4 years
    monthly_df = pd.read_csv(download_stock_month(ticker))[-65:]  # 4 years

    monthly_levels = fractal_candlestick_pattern_method(monthly_df, levels=window_shifting_method(monthly_df).copy())
    weekly_levels = fractal_candlestick_pattern_method(weekly_df, levels=window_shifting_method(weekly_df, levels=monthly_levels.copy()).copy())
    daily_levels = fractal_candlestick_pattern_method(daily_df, levels=window_shifting_method(daily_df, levels=weekly_levels.copy()).copy())

    # monthly_levels = [tup[1] for tup in monthly_levels]
    # weekly_levels = [tup[1] for tup in weekly_levels]
    # daily_levels = [tup[1] for tup in daily_levels]

    # weekly_levels = [level for level in weekly_levels if level not in monthly_levels]
    # daily_levels = [level for level in daily_levels if level not in weekly_levels and level not in monthly_levels]

    weekly_levels = [level for level in weekly_levels if level[1] not in [tup[1] for tup in monthly_levels]]
    daily_levels = [level for level in daily_levels if level[1] not in [tup[1] for tup in weekly_levels] and level[1] not in [tup[1] for tup in monthly_levels]]

    monthly_levels = [(str(monthly_df.loc[level[0], 'Date']).split(' ')[0], level[1]) for level in monthly_levels]
    weekly_levels = [(str(weekly_df.loc[level[0], 'Date']).split(' ')[0], level[1]) for level in weekly_levels]
    daily_levels = [(str(daily_df.loc[level[0], 'Date']).split(' ')[0], level[1]) for level in daily_levels]

    return monthly_levels, weekly_levels, daily_levels


def closest_levels(last_price, levels):
    closest_resistance = None
    closest_support = None
    # levels = np.array(levels)
    levels = np.array([tup[1] for tup in levels])
    difference_list = levels - last_price
    if len(np.where(difference_list > 0)[0]) > 0:
        closest_resistance = levels[np.where(difference_list == np.min(difference_list[np.where(difference_list > 0)]))][0]
    # closest_resistance_indices = np.where(difference_list == np.min(difference_list[np.where(difference_list > 0)]))
    # if len(closest_resistance_indices) != 0:
    #     closest_resistance = levels[closest_resistance_indices][0]
    if len(np.where(difference_list < 0)[0]) > 0:
        closest_support = levels[np.where(difference_list == np.max(difference_list[np.where(difference_list < 0)]))][0]
    # closest_support_indices = np.where(difference_list == np.max(difference_list[np.where(difference_list < 0)]))
    # if len(closest_support_indices) != 0:
    #     closest_support = levels[closest_support_indices][0]
    return closest_resistance, closest_support


def generate_alerts(ticker,
                    monthly_alert=True,
                    weekly_alert=True,
                    daily_alert=False,
                    monthly_diff_th=5.0,
                    weekly_diff_th=5.0,
                    daily_diff_th=5.0):

    try:
        last_price = pd.read_csv(download_stock_day(ticker)).iloc[-1]['Close']
    except ValueError:
        return []
    monthly_levels, weekly_levels, daily_levels = total_stock_levels(ticker)

    def date():
        return datetime.now().astimezone(pytz.timezone('Asia/Jerusalem')).strftime('%Y-%m-%d')

    alerts = []
    # monthly alerts
    if monthly_levels and monthly_alert:
        monthly_resistance, monthly_support = closest_levels(last_price, monthly_levels)
        if monthly_resistance is not None:
            monthly_resistance_diff = (monthly_resistance/last_price - 1)*100.0
            if monthly_resistance_diff <= monthly_diff_th:
                level_date = [level[0] for level in monthly_levels if level[1] == monthly_resistance][0]
                alert_dict = {'date': date(),
                              'symbol': ticker,
                              'timeframe': 'monthly',
                              'level_type': 'R',
                              'level_date': level_date,
                              'price_level_diff': monthly_resistance_diff,
                              'alert': f'Stock is {round(monthly_resistance_diff, 2)}% from closest monthly resistance. Last price: {last_price}. Resistance: {monthly_resistance}'}
                print(f'{now()}: {alert_dict}')
                alerts.append(alert_dict)
        if monthly_support is not None:
            monthly_support_diff = (monthly_support/last_price - 1)*-100.0
            if monthly_support_diff <= monthly_diff_th:
                level_date = [level[0] for level in monthly_levels if level[1] == monthly_support][0]
                alert_dict = {'date': date(),
                              'symbol': ticker,
                              'timeframe': 'monthly',
                              'level_type': 'S',
                              'level_date': level_date,
                              'price_level_diff': monthly_support_diff,
                              'alert': f'Stock is {round(monthly_support_diff, 2)}% from closest monthly support. Last price: {last_price}. Support: {monthly_support}'}
                print(f'{now()}: {alert_dict}')
                alerts.append(alert_dict)

    # weekly alerts
    if weekly_levels and weekly_alert:
        weekly_resistance, weekly_support = closest_levels(last_price, weekly_levels)
        if weekly_resistance is not None:
            weekly_resistance_diff = (weekly_resistance / last_price - 1) * 100.0
            if weekly_resistance_diff <= weekly_diff_th:
                level_date = [level[0] for level in weekly_levels if level[1] == weekly_resistance][0]
                alert_dict = {'date': date(),
                              'symbol': ticker,
                              'timeframe': 'weekly',
                              'level_type': 'R',
                              'level_date': level_date,
                              'price_level_diff': weekly_resistance_diff,
                              'alert': f'Stock is {round(weekly_resistance_diff, 2)}% from closest weekly resistance. Last price: {last_price}. Resistance: {weekly_resistance}'}
                print(f'{now()}: {alert_dict}')
                alerts.append(alert_dict)
        if weekly_support is not None:
            weekly_support_diff = (weekly_support / last_price - 1) * -100.0
            if weekly_support_diff <= weekly_diff_th:
                level_date = [level[0] for level in weekly_levels if level[1] == weekly_support][0]
                alert_dict = {'date': datetime.now().strftime('%Y-%m-%d'),
                              'symbol': ticker,
                              'timeframe': 'weekly',
                              'level_type': 'S',
                              'level_date': level_date,
                              'price_level_diff': weekly_support_diff,
                              'alert': f'Stock is {round(weekly_support_diff, 2)}% from closest weekly support. Last price: {last_price}. Support: {weekly_support}'}
                print(f'{now()}: {alert_dict}')
                alerts.append(alert_dict)

    # daily alerts
    if daily_levels and daily_alert:
        daily_resistance, daily_support = closest_levels(last_price, daily_levels)
        if daily_resistance is not None:
            daily_resistance_diff = (daily_resistance / last_price - 1) * 100.0
            if daily_resistance_diff <= daily_diff_th:
                level_date = [level[0] for level in daily_levels if level[1] == daily_resistance][0]
                alert_dict = {'date': datetime.now().strftime('%Y-%m-%d'),
                              'symbol': ticker,
                              'timeframe': 'daily',
                              'level_type': 'R',
                              'level_date': level_date,
                              'price_level_diff': daily_resistance_diff,
                              'alert': f'Stock is {round(daily_resistance_diff, 2)}% from closest daily resistance. Last price: {last_price}. Resistance: {daily_resistance}'}
                print(f'{now()}: {alert_dict}')
                alerts.append(alert_dict)
        if daily_support is not None:
            daily_support_diff = (daily_support / last_price - 1) * -100.0
            if daily_support_diff <= daily_diff_th:
                level_date = [level[0] for level in daily_levels if level[1] == daily_support][0]
                alert_dict = {'date': datetime.now().strftime('%Y-%m-%d'),
                              'symbol': ticker,
                              'timeframe': 'daily',
                              'level_type': 'S',
                              'level_date': level_date,
                              'price_level_diff': daily_support_diff,
                              'alert': f'Stock is {round(daily_support_diff, 2)}% from closest daily support. Last price: {last_price}. Support: {daily_support}'}
                print(f'{now()}: {alert_dict}')
                alerts.append(alert_dict)

    return alerts


if __name__ == '__main__':
    from utils.get_all_stocks import get_all_snp_stocks
    from cloud_utils.bucket_gcp_utils import download_from_bucket, upload_to_bucket, file_exist_in_bucket
    from cloud_utils.google_cloud_config import save_credentials_to_file
    import gspread
    import gspread_dataframe as gd
    import pathos
    import time

    bucket_filename = 'support_and_resistance_alerts.parquet'
    last_date = ''
    run_now = input("Run now? (y/n) ")
    while True:
        today = datetime.now().astimezone(pytz.timezone('Asia/Jerusalem'))
        if (today.strftime('%Y-%m-%d') != last_date and today.weekday() in [list(range(0,5))] and today.hour == 8) or run_now == 'y':
            last_date = today.strftime('%Y-%m-%d')
            run_now = None

            print(f'{now()} Starting...')
            t0 = time.perf_counter()
            tickers = get_all_snp_stocks()
            new_alerts = []

            with pathos.multiprocessing.ProcessPool() as executor:
                tickers_alerts = executor.map(generate_alerts, tickers)
                for ticker_alerts in tickers_alerts:
                    new_alerts = new_alerts + ticker_alerts

            # for ticker in tickers:
            #     new_alerts = new_alerts + generate_alerts(ticker)

            new_alerts_df = pd.DataFrame(new_alerts)

            if file_exist_in_bucket(bucket_filename):
                old_alerts_df = pd.read_parquet(download_from_bucket(bucket_filename, bucket_filename))
                total_alerts_df = pd.concat([new_alerts_df, old_alerts_df])
            else:
                total_alerts_df = new_alerts_df

            total_alerts_df.sort_values(by=['Date', 'price_level_diff'], ascending=[False, True], inplace=True)
            print(f'{now()} Finished generating alerts. Total of {len(new_alerts_df)} alerts generated.')
            print(f'{now()} Uploading backup file to bucket...')
            total_alerts_df.to_parquet(bucket_filename)
            upload_to_bucket(bucket_filename, bucket_filename)

            print(f'{now()} Uploading to Google Spreadsheets...')
            sa = gspread.service_account(filename=save_credentials_to_file("service_account.json"))
            sheet = sa.open("TechnicalAlerts")
            work_sheet = sheet.worksheet("support_and_resistance_alerts")
            work_sheet.clear()
            gd.set_with_dataframe(work_sheet, total_alerts_df)
            print(f'{now()} S/R Alerts Generator finished successfully. Took {time.perf_counter() - t0} seconds.')
