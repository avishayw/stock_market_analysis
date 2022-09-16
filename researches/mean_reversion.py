from indicators.momentum_indicators import simple_moving_average
from indicators.trend_indicators import exponential_moving_average
import math


def distance_from_sma(df, period):

    df = simple_moving_average(df, period)
    df.dropna(inplace=True)
    df[f'distance_from_SMA{period}'] = (df['Open'] + df['Close'] + df['High'] + df['Low'])/4 - df[f'SMA{period}']
    max_distance = df[f"distance_from_SMA{period}"].max()
    min_distance = df[f"distance_from_SMA{period}"].min()
    mean_distance = df[f"distance_from_SMA{period}"].mean()
    if not (math.isnan(max_distance) or math.isnan(min_distance) or math.isnan(mean_distance)):
        if mean_distance < 100.0:
            print(f'max distance from SMA{period}: {max_distance}')
            print(f'min distance from SMA{period}: {min_distance}')
            print(f'mean distance from SMA{period}: {mean_distance}')
            return mean_distance
    else:
        return None


if __name__ == "__main__":
    from utils.get_all_stocks import get_all_nasdaq_100_stocks, \
        get_all_nyse_composite_stocks, \
        get_all_dow_jones_industrial_stocks, get_all_snp_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import statistics

    # excluded_tickers = ['TCC', 'SMA', 'MCP']

    tickers = list(set(get_all_dow_jones_industrial_stocks() +
                       get_all_nyse_composite_stocks() +
                       get_all_nasdaq_100_stocks() +
                       get_all_snp_stocks()))

    # tickers = [x for x in tickers if x not in excluded_tickers]

    distances = []

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        print(ticker)
        result = distance_from_sma(df, 50)
        # distances = distances + distance_from_sma(df, 200)
        if result is not None:
            distances.append(result)
        if len(distances) > 1:
            try:
                print(f'\nmax: {max(distances)}\n'
                      f'min: {min(distances)}\n'
                      f'mean: {statistics.mean(distances)}\n'
                      f'median: {statistics.median(distances)}\n\n')
            except [statistics.StatisticsError, ValueError]:
                continue
