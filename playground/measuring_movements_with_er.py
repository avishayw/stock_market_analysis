from measurements.noise_measurements import efficiency_ratio
from utils.download_stock_csvs import download_stock_day, download_stock_week, download_stock_month
from plotting.candlestick_chart import multiple_windows_chart
from utils.paths import save_under_results_path
import pandas as pd
import numpy as np

"""
Spotting movements algorithmically by connecting candles which answer some efficiency ratio threshold
"""


class NoConditionError(Exception):
    pass


class EfficiencyCalculationError(Exception):
    pass


class TimeframeError(Exception):
    pass


def measure_er(sample_df, src='Close'):
    net_change = abs(sample_df.iloc[-1][src] - sample_df.iloc[0][src])
    sum_of_individual_changes = ((sample_df[src] - sample_df.shift(1)[src]).abs()).sum()
    if sum_of_individual_changes == 0:
        if net_change == 0:
            return 1.0
        else:
            raise EfficiencyCalculationError("Efficiency ratio: Sum of individual changes is zero but the net change is not.")
    return net_change / sum_of_individual_changes


ticker = 'APH'
timeframe = 'd'
if timeframe == 'd':
    df = pd.read_csv(download_stock_day(ticker)).reset_index()[-252:]
elif timeframe == 'w':
    df = pd.read_csv(download_stock_week(ticker)).reset_index()[-52:]
elif timeframe == 'm':
    df = pd.read_csv(download_stock_week(ticker)).reset_index()[-12:]
else:
    raise TimeframeError("Invalid timeframe. Set to 'd', 'w' or 'm'")

df['close_change%'] = (df['Close']/df.shift(1)['Close'] - 1)*100.0
df['high_change%'] = (df['High']/df.shift(1)['High'] - 1)*100.0
df['low_change%'] = (df['Low']/df.shift(1)['Low'] - 1)*100.0
df['Median'] = (df['High'] + df['Low'])/2

df_start_idx = df.index[0]
# i = 2
i = 2
movement_id = 0
current_idx = 0
er_threshold = 0.8
max_movement_period = 10
source = 'High'
while i < len(df):
    sample_df = df[current_idx:i].copy()
    er = measure_er(sample_df, source)
    if er >= er_threshold:
        movement_er = er
        i += 1
    elif er < er_threshold:
        for j in range(current_idx, i - 1):
            df.loc[df_start_idx + j, 'movement_id'] = movement_id
            df.loc[df_start_idx + j, 'movement_er'] = movement_er
        current_idx = i - 1
        movement_id += 1
        # i = current_idx + 2
        i = current_idx + 2
    elif i - current_idx >= max_movement_period:
        current_idx += 1
        i = current_idx + 1
    else:
        raise NoConditionError("None of the conditions met")

print(movement_id)

movements = df['movement_id'].dropna().unique().tolist()
for movement in movements:
    movement_df = df.loc[df['movement_id'] == movement].copy()
    movement_roc = (movement_df.iloc[-1][source]/movement_df.iloc[0][source] - 1)*100.0
    df.loc[movement_df.index[-1], 'movement_roc'] = movement_roc
    y1 = movement_df.iloc[-1][source]
    y0 = movement_df.iloc[0][source]
    x0 = 0
    x1 = len(movement_df) - 1
    m = (y1-y0)/(x1-x0)
    c = y1 - m*x1
    print(movement, m, c, len(movement_df))
    for i in range(len(movement_df)):
        df.loc[movement_df.index[0] + i, f'{source.lower()}_noise_removed'] = m*i + c

df.to_csv(save_under_results_path(f'{ticker}_movements_source_{source.lower()}_er_{str(er_threshold).replace(".", "_")}_timeframe_{timeframe}.csv'))

chart_dict = {(1, 'Close Noise Removed'): [f'{source.lower()}_noise_removed', source],
              (2, 'Movement ID'): ['movement_id'],
              (3, 'Movement ER'): ['movement_er']}
fig = multiple_windows_chart(ticker, df, chart_dict)

# Remove non-trading dates
df['Date'] = df['Date'].map(lambda x: str(x).split(' ')[0])
df['Datetime'] = pd.to_datetime(df['Date'])
dt_all = pd.date_range(start=df.loc[df.index[0], 'Date'], end=df.loc[df.index[-1], 'Date'], freq='D')
dt_all_py = [d.to_pydatetime() for d in dt_all]
dt_obs_py = [d.to_pydatetime() for d in df['Datetime']]
dt_breaks = [d for d in dt_all_py if d not in dt_obs_py]
print(dt_breaks)
print(len(dt_all), len(dt_breaks))
fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

fig.show()

