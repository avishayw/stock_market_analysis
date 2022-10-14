"""
This strategy will look for close[1]-open gaps which are lower than negative_gap_th. Then it will check the linear
regression for the 200 days before. If the slope is negative - enter short position.
Exit signal: for now take profit & stop loss
"""
import pandas as pd
import numpy as np
import pathos
from machine_learning_stuff.linear_regression import backward_linear_regression
from utils.download_stock_csvs import download_stock_day


def negative_gap_in_bear_trend(ticker, negative_gap_th=-15.0, sl=-5.0, tp=20.0, backwards_period=200):

    df = pd.read_csv(download_stock_day(ticker)).reset_index()
    # df.reset_index(inplace=True)
    df['gap'] = (df['Open']/df.shift(1)['Close'] - 1)*100.0
    df['negative_gap'] = np.where(df['gap'] < negative_gap_th, True, False)
    # print(len(df.loc[df['negative_gap']]))
    negative_gap_idx = list(np.array(df.loc[df['negative_gap']].index))
    df['coef'] = np.nan
    df['score'] = np.nan

    for idx in negative_gap_idx:
        if idx > backwards_period:
            try:
                roc, coef, score, model = backward_linear_regression(df, 'Close', idx, backwards_period)
            except TypeError as e:
                print(e)
                print(idx, len(df))
                continue
        # print(roc, coef[0], score)
            df.loc[idx, 'coef'] = coef[0]
            df.loc[idx, 'score'] = score

    df['short_signal'] = np.where((df['negative_gap']) & (df['coef'] < 0), True, False)

    i = 0
    short_position = False
    enter_price = None
    enter_date = None
    cap = 100.0

    trades = []

    while i < len(df):
        if short_position:
            if df.iloc[i]['High'] > enter_price*(1-(sl/100.0)) or df.iloc[i]['Low'] < enter_price*(1-(tp/100.0)):
                if df.iloc[i]['Open'] > enter_price*(1-(sl/100.0)):
                    exit_price = df.iloc[i]['Open']
                elif df.iloc[i]['High'] > enter_price*(1-(sl/100.0)):
                    exit_price = enter_price * (1 - (sl / 100.0))
                elif df.iloc[i]['Open'] < enter_price*(1-(tp/100.0)):
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = enter_price*(1-(tp/100.0))
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((enter_price - exit_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'short',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price < enter_price,
                              'change%': ((enter_price - exit_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                short_position = False
        elif df.iloc[i]['short_signal'] and df.iloc[i]['Open'] != 0.0 and df.iloc[i]['Close'] != 0.0:
            enter_price = df.iloc[i]['Open']
            enter_date = df.iloc[i]['Date']
            short_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


def negative_gap_in_bear_trend_long(ticker, negative_gap_th=-5.0, sl=-5.0, tp=20.0, backwards_period=200):

    df = pd.read_csv(download_stock_day(ticker)).reset_index()
    # df.reset_index(inplace=True)
    df['gap'] = (df['Open']/df.shift(1)['Close'] - 1)*100.0
    df['negative_gap'] = np.where(df['gap'] < negative_gap_th, True, False)
    # print(len(df.loc[df['negative_gap']]))
    negative_gap_idx = list(np.array(df.loc[df['negative_gap']].index))
    df['coef'] = np.nan
    df['score'] = np.nan

    for idx in negative_gap_idx:
        if idx > backwards_period:
            try:
                roc, coef, score, model = backward_linear_regression(df, 'Close', idx, backwards_period)
            except TypeError as e:
                print(e)
                print(idx, len(df))
                continue
        # print(roc, coef[0], score)
            df.loc[idx, 'coef'] = coef[0]
            df.loc[idx, 'score'] = score

    df['buy_signal'] = np.where((df['negative_gap']) & (df['coef'] < 0), True, False)

    i = 0
    long_position = False
    enter_price = None
    enter_date = None
    cap = 100.0

    trades = []

    while i < len(df):
        if long_position:
            if df.iloc[i]['Low'] < enter_price*(1+(sl/100.0)) or df.iloc[i]['High'] > enter_price*(1+(tp/100.0)):
                if df.iloc[i]['Open'] > enter_price*(1+(tp/100.0)):
                    exit_price = df.iloc[i]['Open']
                elif df.iloc[i]['High'] > enter_price*(1+(tp/100.0)):
                    exit_price = enter_price*(1+(tp/100.0))
                elif df.iloc[i]['Open'] < enter_price*(1+(sl/100.0)):
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = enter_price*(1+(sl/100.0))
                exit_date = df.iloc[i]['Date']
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'short',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
                long_position = False
        elif df.iloc[i]['buy_signal'] and df.iloc[i]['Open'] != 0.0 and df.iloc[i]['Close'] != 0.0:
            enter_price = df.iloc[i]['Open']
            enter_date = df.iloc[i]['Date']
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


if __name__ == '__main__':
    import pandas as pd
    import random
    from utils.paths import save_under_results_path
    from utils.in_sample_tickers import *
    from itertools import product, repeat

    # negative_gap_th_list = [-5.0, -10.0, -15.0, -20.0]
    # sl_list = [-5.0, -10.0, 15.0, -20.0]
    # tp_list = [5.0, 10.0, 15.0, 20.0]
    #
    # params_list = [negative_gap_th_list, sl_list, tp_list]
    # combinations = list(product(*params_list))
    # random.shuffle(combinations)
    # print(len(combinations))
    #
    # combinations_dict = {'negative_gap_th': [],
    #                      'sl': [],
    #                      'tp': [],
    #                      'win_rate': [],
    #                      'total_trades': []}
    #
    # tickers = IN_SAMPLE_TICKERS
    #
    # for combination in combinations:
    #     negative_gap_th = combination[0]
    #     sl = combination[1]
    #     tp = combination[2]
    #
    #     all_trades = []
    #
    #     with pathos.multiprocessing.ProcessPool() as executor:
    #         results = executor.map(negative_gap_in_bear_trend,
    #                                tickers,
    #                                repeat(negative_gap_th),
    #                                repeat(sl),
    #                                repeat(tp))
    #         for result in results:
    #             all_trades = all_trades + result[0]
    #
    #     trades_df = pd.DataFrame(all_trades)
    #     combinations_dict['negative_gap_th'].append(negative_gap_th)
    #     combinations_dict['sl'].append(sl)
    #     combinations_dict['tp'].append(tp)
    #     combinations_dict['win_rate'].append(len(trades_df.loc[trades_df['win']])/len(trades_df))
    #     combinations_dict['total_trades'].append(len(trades_df))
    #
    #     pd.DataFrame(combinations_dict).to_csv(save_under_results_path('negative_gap_in_bear_trend_combinations.csv'))

    tickers = IN_SAMPLE_TICKERS

    all_trades = []

    with pathos.multiprocessing.ProcessPool() as executor:
        results = executor.map(negative_gap_in_bear_trend_long, tickers)

        for result in results:
            all_trades = all_trades + result[0]

    trades_df = pd.DataFrame(all_trades)
    print(len(trades_df.loc[trades_df['win']])/len(trades_df))
    trades_df.to_csv(save_under_results_path(f'negative_gap_in_bear_trend_gap_-5.0_sl_-5.0_tp_20.0_all_trades.csv'))
