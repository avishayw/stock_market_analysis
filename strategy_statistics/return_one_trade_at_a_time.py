import pandas as pd
from datetime import datetime

trades_csv_path = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\ma_roc_and_efficiency_ratio_trading_09-09-2022-02-07-05_all_trades.csv"
df = pd.read_csv(trades_csv_path)
df['enter_datetime'] = pd.to_datetime(df['enter_date'])
df['exit_datetime'] = pd.to_datetime(df['exit_date'])

df.sort_values(by=['enter_date'], inplace=True)

current_trade_exit_datetime = df.iloc[0]['exit_datetime']
commulative_change = 1 + (df.iloc[0]['change%']/100.0)
commulative_change_for_reference = 1 + (df.iloc[0]['change%']/100.0)
total_trades = 1

for i in range(1,len(df)):
    commulative_change_for_reference = commulative_change_for_reference*(1 + (df.iloc[i]['change%']/100.0))
    if df.iloc[i]['enter_datetime'] > current_trade_exit_datetime:
        commulative_change = commulative_change*(1 + (df.iloc[i]['change%']/100.0))
        current_trade_exit_datetime = df.iloc[i]['exit_datetime']
        total_trades += 1

start_cap = 100.0
print(commulative_change, start_cap*commulative_change, total_trades/len(df))
print(commulative_change_for_reference, start_cap*commulative_change_for_reference)