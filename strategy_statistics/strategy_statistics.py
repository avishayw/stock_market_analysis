import statistics
from scipy import stats
import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt
from utils.paths import save_under_results_path


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

    return {'mean_change': df['change%'].mean(),
            'stdev': np.std(df['change%'].tolist()),
            'cov': np.std(df['change%'].tolist())/df['change%'].mean(),
            'skew': stats.skew(df['change%'].tolist()),
            'kurtosis': stats.kurtosis(df['change%'].tolist()),
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
                     'coefficient of variance': statistics.stdev(days.tolist())/ float(days.mean()),
                     'skew': stats.skew(days.tolist()),
                     'kurtosis': stats.kurtosis(days.tolist())}
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


def histogram(items, save_png_path, cut_abnormal=True, draw_vertical=False):

    mean = np.mean(items)
    stdev = np.std(items)
    print(len(items))
    num_stdevs = 1
    if cut_abnormal:
        backup = items.copy()
        items = [x for x in backup if (x > (mean - stdev*num_stdevs)) and (x < (mean + stdev*num_stdevs))]
    print(len(items))
    bins = np.linspace(np.ceil(min(items)),
                       np.floor(max(items)),
                       100)

    mean = np.mean(items)
    median = np.median(items)
    stdev = np.std(items)
    tenth_percentile = np.percentile(items, 10)
    nintith_percentile = np.percentile(items, 90)
    skew = stats.skew(items)
    kurtosis = stats.kurtosis(items)

    occurrences, price_ranges = np.histogram(items, bins)

    plt.xlim([min(items), max(items)])
    plt.hist(items, bins=bins, alpha=0.5)
    if draw_vertical:
        plt.axvline(mean, color='r')
        plt.axvline(mean + stdev, color='k')
        plt.axvline(mean - stdev, color='k')
        plt.axvline(tenth_percentile, color='y')
        plt.axvline(nintith_percentile, color='y')
        plt.axvline(median, color='b')
    plt.text(min(items), max(occurrences), f'mean: {mean}\nmedian: {median}\nstdev: {stdev}\nskew: {skew}\nkurtosis: {kurtosis}')
    plt.savefig(save_png_path)


def win_rate_per_period(df, percentile_step):
    df['days'] = (pd.to_datetime(df['exit_date']) - pd.to_datetime(df['enter_date'])).dt.days
    days = df['days'].tolist()
    days_ranges = []
    for i in range(percentile_step, 100 + percentile_step, percentile_step):
        days_ranges.append((np.percentile(days, i-10), np.percentile(days, i)))

    win_rate_per_period = {}
    for day_range in days_ranges:
        print('range:', day_range)
        test_df = df.loc[(df['days'] >= day_range[0]) & (df['days'] <= day_range[1])].copy()
        print('total trades:', len(test_df))
        print('win rate:', len(test_df.loc[test_df['win']])/len(test_df))
        print('mean change:', test_df['change%'].mean())
        print('median change:', test_df['change%'].median())
        day_range_str = f'{day_range[0]}_to_{day_range[1]}_days'
        win_rate_per_period[day_range_str] = {'total trades': len(test_df),
                                          'win rate': len(test_df.loc[test_df['win']])/len(test_df),
                                          'mean change': test_df['change%'].mean(),
                                          'median change': test_df['change%'].median(),
                                          'stdev': np.std(test_df['change%'].tolist()),
                                          'skew': stats.skew(test_df['change%'].tolist()),
                                          'kurtosis': stats.kurtosis(test_df['change%'].tolist())}

    with open(save_under_results_path('ma_roc_er_trading_1h_timeframe_win_rate_per_trade_period.json'), 'w') as f:
        json.dump(win_rate_per_period, f, indent=4)


def stats_per_month(trades_csv_path):
    df = pd.read_csv(trades_csv_path)
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    stats_per_month_dict = {}
    months = list(set(list(pd.to_datetime(df['enter_date']).dt.strftime('%Y-%m').unique()) + list(pd.to_datetime(df['exit_date']).dt.strftime('%Y-%m').unique())))
    months = sorted(months)

    for month in months:
        stats_per_month_dict[month] = {}
        entries_df = df.loc[pd.to_datetime(df['enter_date']).dt.strftime('%Y-%m') == month].copy()
        if not entries_df.empty:
            total = len(entries_df)
            change_mean = entries_df['change%'].mean()
            change_median = np.median(entries_df['change%'].tolist())
            change_stdev = np.std(entries_df['change%'].tolist())
            trades_period_mean = np.mean((pd.to_datetime(entries_df['exit_date']) - pd.to_datetime(entries_df['enter_date'])).dt.days)
            trades_period_median = np.median((pd.to_datetime(entries_df['exit_date']) - pd.to_datetime(entries_df['enter_date'])).dt.days)
            trades_period_stdev = np.std((pd.to_datetime(entries_df['exit_date']) - pd.to_datetime(entries_df['enter_date'])).dt.days)
            win_rate = len(entries_df.loc[entries_df['win']])/len(entries_df)
            stats_per_month_dict[month]['entered_trades_stats'] = {'total_entries': total,
                                                                   'change_mean': change_mean,
                                                                   'change_median': change_median,
                                                                   'change_stdev': change_stdev,
                                                                   'trades_period_mean': trades_period_mean,
                                                                   'trades_period_median': trades_period_median,
                                                                   'trades_period_stdev': trades_period_stdev,
                                                                   'win_rate': win_rate}
        exits_df = df.loc[pd.to_datetime(df['exit_date']).dt.strftime('%Y-%m') == month].copy()
        if not exits_df.empty:
            total = len(exits_df)
            change_mean = exits_df['change%'].mean()
            change_median = np.median(exits_df['change%'].tolist())
            change_stdev = np.std(exits_df['change%'].tolist())
            trades_period_mean = np.mean(
                (pd.to_datetime(exits_df['exit_date']) - pd.to_datetime(exits_df['enter_date'])).dt.days)
            trades_period_median = np.median(
                (pd.to_datetime(exits_df['exit_date']) - pd.to_datetime(exits_df['enter_date'])).dt.days)
            trades_period_stdev = np.std(
                (pd.to_datetime(exits_df['exit_date']) - pd.to_datetime(exits_df['enter_date'])).dt.days)
            win_rate = len(exits_df.loc[exits_df['win']]) / len(exits_df)
            stats_per_month_dict[month]['exited_trades_stats'] = {'total_exits': total,
                                                                   'change_mean': change_mean,
                                                                   'change_median': change_median,
                                                                   'change_stdev': change_stdev,
                                                                   'trades_period_mean': trades_period_mean,
                                                                   'trades_period_median': trades_period_median,
                                                                   'trades_period_stdev': trades_period_stdev,
                                                                   'win_rate': win_rate}

    name = str(os.path.basename(trades_csv_path)).replace('csv','')
    with open(save_under_results_path(f'{name}_stats_per_month.json'), 'w') as f:
        json.dump(stats_per_month_dict, f, indent=4)


if __name__=="__main__":
    import json
    import pandas as pd
    import numpy as np
    from utils.paths import save_under_results_path
    import os
    import itertools

    trades_csv = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\AA_channel_midline_trading_trades_old_dropped_duplicates.csv"

    df = pd.read_csv(trades_csv)
    name = str(os.path.basename(trades_csv)).replace('.csv', '')

    with open(save_under_results_path(f'{name}_statistics.json'), 'w') as f:
        json.dump(all_statistics_dict(df), f, indent=4)
