"""
Given that the cumulative change (close-to-close) of a stock is greater than x after y days, what's the probability
that the cumulative change will be greater than z (z>x) after w days?
"""
import numpy as np
from utils.get_all_stocks import in_sample_tickers
from utils.download_stock_csvs import download_stock_day
import pandas as pd
import json
import os
import concurrent.futures
import time


def cumulative_change_continuation(df, x, y, z, w):
    df['change'] = (1+(df['Close'] - df.shift(1)['Close'])/df.shift(1)['Close'])
    precondition_met_count = len(df.loc[df['change'].rolling(y).apply(np.prod, raw=True) >= x])
    condition_met_count = len(df.loc[(df['change'].rolling(y).apply(np.prod, raw=True) >= x) &
                                     (df.shift(-w)['change'].rolling(w).apply(np.prod, raw=True) >= z)])

    return precondition_met_count, condition_met_count


def count_condition(ticker, params):
    x = params[0]
    y = params[1]
    z = params[2]
    w = params[3]
    df = pd.read_csv(download_stock_day(ticker))
    preconditions, conditions = cumulative_change_continuation(df, x, y, z, w)
    if preconditions > 0:
        print(ticker, conditions/preconditions)
    return preconditions, conditions, (x, y, z, w)


if __name__=='__main__':
    import concurrent.futures
    import itertools
    import numpy as np

    t0 = time.time()

    tickers = in_sample_tickers()

    x_list = list(np.arange(1.03, 1.30, 0.02))
    y_list = list(np.arange(2, 252, 2))
    z_list = list(np.arange(1.03, 1.30, 0.02))
    w_list = list(np.arange(2, 252, 2))

    combinations = itertools.product(*[x_list, y_list, z_list, w_list])

    for combination in combinations:
        x = combination[0]
        y = combination[1]
        z = combination[2]
        w = combination[3]

        total_precondition_met_count = 0
        total_condition_met_count = 0

        with concurrent.futures.ProcessPoolExecutor() as process_executor:
            results = process_executor.map(count_condition, tickers, combinations)

            for result in results:
                total_precondition_met_count += result[0]
                total_condition_met_count += result[1]
                x = result[2][0]
                y = result[2][1]
                z = result[2][2]
                w = result[2][3]

                if total_precondition_met_count == 0:
                    results_dict = {f'{x}_{y}_{z}_{w}': None}
                else:
                    results_dict = {f'{x}_{y}_{z}_{w}': (total_condition_met_count / total_precondition_met_count,
                                                         float(total_precondition_met_count),
                                                         float(total_condition_met_count))}

                results_json_path = 'cumulative_change_continuation.json'

                if not os.path.exists(results_json_path):
                    with open(results_json_path, 'w') as f:
                        json.dump(results_dict, f, indent=4)
                else:
                    with open(results_json_path, 'r') as f:
                        old_dict = json.load(f)
                    old_dict.update(results_dict)
                    with open(results_json_path, 'w') as f:
                        json.dump(old_dict, f, indent=4)

    print(time.time() - t0)



