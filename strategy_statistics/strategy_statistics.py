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

    trades_csv = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\ma_roc_er_trading_v4_in_sample_tickers_1h_timeframe.csv"

    # stats_per_month(trades_csv)
    # exit()
    name = str(os.path.basename(trades_csv).replace('.csv', ''))
    df = pd.read_csv(trades_csv)

    # with open(save_under_results_path(f'{name}_statistics.json'), 'w') as f:
    #     json.dump(all_statistics_dict(df), f, indent=4)
    # df.replace([np.inf, -np.inf], np.nan, inplace=True)
    # df.dropna(inplace=True)

    # # win rate per vix
    # periods = [20, 50, 200]
    # # columns = ['vix_sma20_roc5', 'vix_sma50_roc5', 'vix_sma200_roc5', 'vix_sma20_er', 'vix_sma50_er',
    # #            'vix_sma200_er', 'vix_close_sma20_ratio', 'vix_close_sma50_ratio', 'vix_close_sma200_ratio']
    #
    # for period in periods:
    #     columns = [f'vix_sma{period}_roc5', f'vix_close_sma{period}_ratio']
    #     value_ranges_dict = {}
    #     for column in columns:
    #         values = df[column]
    #         value_ranges_dict[column] = []
    #         for i in range(5, 105, 5):
    #             range_start = np.percentile(values, i - 5)
    #             range_end = np.percentile(values, i)
    #             if not np.isnan(range_end):
    #                 value_ranges_dict[column].append((range_start, range_end))
    #             else:
    #                 value_ranges_dict[column].append((range_start, np.max(values)))
    #
    #     values_to_combine = [value_ranges_dict[x] for x in value_ranges_dict.keys()]
    #     combinations = list(itertools.product(*values_to_combine))
    #     print(len(combinations))
    #     win_rate_per_column = {}
    #     for combination in combinations:
    #         test_df = df.copy()
    #         value_range_str = ''
    #         for i, range_tuple in enumerate(combination):
    #             value_range_str = value_range_str + f'_{columns[i]}_{range_tuple[0]}_to{range_tuple[1]}'
    #             test_df = test_df.loc[(test_df[columns[i]] >= range_tuple[0]) & (test_df[columns[i]] < range_tuple[1])].copy()
    #         if test_df.empty:
    #             print(combination)
    #             continue
    #         test_df['days'] = (pd.to_datetime(test_df['exit_date']) - pd.to_datetime(test_df['enter_date'])).dt.days
    #         print('total trades:', len(test_df))
    #         print('win rate:', len(test_df.loc[test_df['win']]) / len(test_df))
    #         print('mean change:', test_df['change%'].mean())
    #         print('median change:', test_df['change%'].median())
    #         win_rate_per_column[value_range_str] = {'total trades': len(test_df),
    #                                                 'sample error %': 100/np.sqrt(len(test_df)),
    #                                                 'dates': list(test_df['enter_date'].unique()),
    #                                                 'stocks': list(test_df['symbol'].unique()),
    #                                                     'mean days': float(test_df['days'].mean()),
    #                                               'win rate': float(len(test_df.loc[test_df['win']]) / len(test_df)),
    #                                               'mean change': float(test_df['change%'].mean()),
    #                                               'median change': float(test_df['change%'].median()),
    #                                               'stdev': float(np.std(test_df['change%'].tolist())),
    #                                               'skew': float(stats.skew(test_df['change%'].tolist())),
    #                                               'kurtosis': float(stats.kurtosis(test_df['change%'].tolist()))}
    #
    #     with open(save_under_results_path(f'{name}_win_rate_per_{period}.json'), 'w') as f:
    #         json.dump(win_rate_per_column, f, indent=4)

    for period in [20, 50, 200]:
        print(period)
        json_path = fr"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\ma_roc_er_trading_v4_in_sample_tickers_1h_timeframe_win_rate_per_vix_close_sma{period}_ratio.json"
        with open(json_path, 'r') as f:
            stats_dict = json.load(f)

        profitable_combinations = []
        for combination in stats_dict.keys():
            # sample_error = stats_dict[combination]['sample error %']
            mean = stats_dict[combination]['mean change']
            stdev = stats_dict[combination]['stdev']
            median = stats_dict[combination]['median change']
            # dates = stats_dict[combination]['dates']
            coefficient_of_variance = abs(stdev/mean)
            if mean > 0 and median > 0 and coefficient_of_variance < 20.0:
                print(combination)
                print(mean, median, stdev)

    # win rate per change
    # column = 'change%'
    # values = df[column]
    # value_ranges = []
    # for i in range(5, 105, 5):
    #     range_start = np.percentile(values, i - 5)
    #     range_end = np.percentile(values, i)
    #     if not np.isnan(range_end):
    #         value_ranges.append((range_start, range_end))
    #     else:
    #         value_ranges.append((range_start, np.max(values)))
    # exclude_from_stats_columns = ['symbol',
    #                               'type',
    #                               'change%',
    #                               'win',
    #                               'enter_date',
    #                               'enter_price',
    #                               'exit_date',
    #                               'exit_price',
    #                               'period_max',
    #                               'period_min',
    #                               'period_max_date',
    #                               'period_min_date',
    #                               'Unnamed: 0']
    # stats_columns = [x for x in df.columns.tolist() if x not in exclude_from_stats_columns]
    # win_rate_per_change = {}
    # for value_range in value_ranges:
    #     print('range:', value_range)
    #     test_df = df.loc[(df[column] >= value_range[0]) & (df[column] < value_range[1])].copy()
    #     test_df['days'] = (pd.to_datetime(test_df['exit_date']) - pd.to_datetime(test_df['enter_date'])).dt.days
    #     print('total trades:', len(test_df))
    #     value_range_str = f'{value_range[0]}_to_{value_range[1]}'
    #     value_range_stats_dict = {'total trades': len(test_df),
    #                                             'trade period mean': test_df['days'].mean(),
    #                                             'trade period median': np.median(test_df['days'].tolist()),
    #                                             'trade period stdev': np.std(test_df['days'].tolist())}
    #     for stats_column in stats_columns:
    #         value_range_stats_dict[f'{stats_column}_mean'] = test_df[stats_column].mean()
    #         value_range_stats_dict[f'{stats_column}_median'] = np.median(test_df[stats_column].tolist())
    #         value_range_stats_dict[f'{stats_column}_stdev'] = np.std(test_df[stats_column].tolist())
    #
    #     win_rate_per_change[value_range_str] = value_range_stats_dict
    #
    # with open(save_under_results_path(f'{name}_win_rate_per_change.json'), 'w') as f:
    #     json.dump(win_rate_per_change, f, indent=4)