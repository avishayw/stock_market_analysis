import pandas as pd
import statistics

trates_csv_path = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\ma_roc_and_efficiency_ratio_trading_10-09-2022-23-10-49_all_trades.csv"

df = pd.read_csv(trates_csv_path)

df.sort_values(by=['exit_date'], inplace=True)

most_consecutive_losses = 0
most_consecutive_wins = 0

consecutive_losses = 0
consecutive_wins = 0

consecutive_losses_list = []
consecutive_wins_list = []

for i in range(len(df)):
    if df.iloc[i]['win']:
        if consecutive_losses > 0:
            consecutive_wins = 1
            if consecutive_losses > most_consecutive_losses:
                most_consecutive_losses = consecutive_losses
            if consecutive_losses > 1:
                consecutive_losses_list.append(consecutive_losses)
            consecutive_losses = 0
        else:
            consecutive_wins += 1
    else:
        if consecutive_wins > 0:
            consecutive_losses = 1
            if consecutive_wins > most_consecutive_wins:
                most_consecutive_wins = consecutive_wins
            if consecutive_wins > 1:
                consecutive_wins_list.append(consecutive_wins)
            consecutive_wins = 0
        else:
            consecutive_losses += 1

print(f'most consecutive wins: {most_consecutive_wins}, most consecutive losses: {most_consecutive_losses}')
print(f'consecutive wins stats:\nmean: {statistics.mean(consecutive_wins_list)}\nmedian: {statistics.median(consecutive_wins_list)}\nstandard deviation: {statistics.stdev(consecutive_wins_list)}')
print(f'consecutive losses stats:\nmean: {statistics.mean(consecutive_losses_list)}\nmedian: {statistics.median(consecutive_losses_list)}\nstandard deviation: {statistics.stdev(consecutive_losses_list)}')