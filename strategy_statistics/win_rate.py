import pandas as pd
import statistics


def win_rate(csv_path):
    df = pd.read_csv(csv_path)
    return len(df.loc[df['win']])/len(df)


def avg_change(csv_path):
    df = pd.read_csv(csv_path)
    win_avg_change = df.loc[df['win']]['change%'].mean()
    loss_avg_change = df.loc[df['win'] == False]['change%'].mean()
    return df['change%'].mean(), win_avg_change, loss_avg_change


# csv_path = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\ma_roc_and_efficiency_ratio_trading_10-09-2022-23-10-49_all_trades.csv"
#
# print(win_rate(csv_path))
# print(avg_change(csv_path))

if __name__=="__main__":
    import glob


