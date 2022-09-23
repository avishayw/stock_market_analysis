"""
Given that the cumulative change (close-to-close) of a stock is greater than x after y days, what's the probability
that the cumulative change will be greater than z (z>x) after w days?
"""
import numpy as np


def cumulative_change_continuation(df, x, y, z, w):
    df['change'] = (1+(df['Close'] - df.shift(1)['Close'])/df.shift(1)['Close'])
    precondition_met_count = len(df.loc[df['change'].rolling(y).apply(np.prod, raw=True) >= x])
    condition_met_count = len(df.loc[(df['change'].rolling(y).apply(np.prod, raw=True) >= x) &
                                     (df.shift(-w)['change'].rolling(w).apply(np.prod, raw=True) >= z)])

    return precondition_met_count, condition_met_count


from utils.get_all_stocks import in_sample_tickers
from utils.download_stock_csvs import download_stock_day
import pandas as pd
import json
import os


x = 1.15
y = 5
z = 1.5
w = 10

tickers = in_sample_tickers()
total_precondition_met_count = 0
total_condition_met_count = 0

for ticker in tickers:
    df = pd.read_csv(download_stock_day(ticker))
    preconditions, conditions = cumulative_change_continuation(df, x, y, z, w)
    if preconditions > 0:
        print(ticker, conditions/preconditions)
    total_precondition_met_count += preconditions
    total_condition_met_count += conditions

if total_precondition_met_count == 0:
    results_dict = {f'{x}_{y}_{z}_{w}': None}
else:
    results_dict = {f'{x}_{y}_{z}_{w}': (total_condition_met_count/total_precondition_met_count,
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