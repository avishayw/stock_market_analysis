import statistics
import pandas as pd


def most_consecutive(df):

    df = df.copy()

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
                consecutive_losses_list.append(consecutive_losses)
                consecutive_losses = 0
            else:
                consecutive_wins += 1
        else:
            if consecutive_wins > 0:
                consecutive_losses = 1
                if consecutive_wins > most_consecutive_wins:
                    most_consecutive_wins = consecutive_wins
                consecutive_wins_list.append(consecutive_wins)
                consecutive_wins = 0
            else:
                consecutive_losses += 1

    try:
        consecutive_dict = {'wins': {'max_consecutive': most_consecutive_wins,
                                     'mean': statistics.mean(consecutive_wins_list),
                                     'median': statistics.median(consecutive_wins_list),
                                     'stdev': statistics.stdev(consecutive_wins_list),
                                     'coefficient of variance': statistics.stdev(consecutive_wins_list)/statistics.mean(consecutive_wins_list)},
                            'losses': {'max_consecutive': most_consecutive_losses,
                                       'mean': statistics.mean(consecutive_losses_list),
                                       'median': statistics.median(consecutive_losses_list),
                                       'stdev': statistics.stdev(consecutive_losses_list),
                                       'coefficient of variance': statistics.stdev(
                                           consecutive_losses_list) / statistics.mean(consecutive_losses_list)}
                            }
    except statistics.StatisticsError:
        return None

    return consecutive_dict


def win_rate(df):
    return len(df.loc[df['win']])/len(df)


def avg_change(df):

    return {'total_avg_change': df['change%'].mean(),
                'win_avg_change': df.loc[df['win']]['change%'].mean(),
                'loss_avg_change': df.loc[df['win'] == False]['change%'].mean()}


def trade_days(df):
    df = df.copy()
    days = (df['exit_datetime'] - df['enter_datetime']).dt.days
    try:
        days_dict = {'max': float(days.max()),
                     'min': float(days.min()),
                     'mean': float(days.mean()),
                     'median': statistics.median(days.tolist()),
                     'stdev': statistics.stdev(days.tolist()),
                     'coefficient of variance': statistics.stdev(days.tolist())/ float(days.mean())}
    except statistics.StatisticsError:
        return None
    return days_dict


def all_statistics_dict(df):

    df['enter_datetime'] = pd.to_datetime(df['enter_date'])
    df['exit_datetime'] = pd.to_datetime(df['exit_date'])

    return {'cosecutive_dict': most_consecutive(df),
            'avgerage_change': avg_change(df),
            'total_trades': len(df),
            'win_rate': win_rate(df),
            'days_stats': trade_days(df)}


if __name__=="__main__":
    import json
    import pandas as pd
    from utils.paths import save_under_results_path

    # v1 = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\ma_roc_and_efficiency_ratio_trading_13-09-2022-16-45-59_all_trades.csv"
    v2 = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\ma_roc_and_efficiency_ratio_trading_14-09-2022-12-08-53_all_trades.csv"

    with open(save_under_results_path('delisted_stocks_statistics.json'), 'w') as f:
        json.dump(all_statistics_dict(pd.read_csv(v2)), f, indent=4)

    # with open(save_under_results_path('v1_statistics.json'), 'w') as f:
    #     json.dump(all_statistics_dict(pd.read_csv(v1)), f, indent=4)

