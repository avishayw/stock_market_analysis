import pandas as pd
import numpy as np
from indicators.momentum_indicators import rsi, simple_moving_average


def rsi_sell_entry(df, period):
    df = rsi(df ,period)
    df['RSI_angle'] = (df['RSI'] - df.shift(1)['RSI']).apply(lambda x: np.arctan(x) * (180 / np.pi))
    df['rsi_down_entry'] = np.where((df['RSI_angle'] < 0) & (df['RSI'] > 80.0), True, False)
    df.drop(columns=['RSI', 'RSI_angle'], axis=1, inplace=True)
    return df


def sma_sell(df, sma_period, lower_period):
    df = simple_moving_average(df, sma_period)
    df[f'high_lower_than_sma{sma_period}'] = np.where(df['High'] < df[f'SMA{sma_period}'], 1, 0)
    df[f'last_{lower_period}_days'] = df[f'high_lower_than_sma{sma_period}'].rolling(lower_period).sum()
    df[f'lower_than_sma{sma_period}_for_{lower_period}_days'] = np.where(df[f'last_{lower_period}_days'] == lower_period, True, False)
    df.drop(columns=[f'last_{lower_period}_days', f'high_lower_than_sma{sma_period}'], axis=1, inplace=True)
    return df


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import json

    with open(save_under_results_path("down_trend_tickers.json"), 'r') as f:
        tickers = json.load(f)['tickers']

    sma_sell_entry_tickers = []
    rsi_sell_entry_tickers = []
    sma_rsi_sell_entry_tickers = []

    sma_period = 50
    lower_than_sma_period = 10

    rsi_period = 10

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        df = df[-365:]
        df = rsi_sell_entry(df, rsi_period)
        df = sma_sell(df, sma_period, lower_than_sma_period)
        if df.iloc[-1][f'lower_than_sma{sma_period}_for_{lower_than_sma_period}_days'] and not df.iloc[-1]['rsi_down_entry']:
            print(ticker)
            sma_sell_entry_tickers.append(ticker)
        elif not df.iloc[-1][f'lower_than_sma{sma_period}_for_{lower_than_sma_period}_days'] and df.iloc[-1]['rsi_down_entry']:
            print(ticker)
            rsi_sell_entry_tickers.append(ticker)
        elif df.iloc[-1][f'lower_than_sma{sma_period}_for_{lower_than_sma_period}_days'] and df.iloc[-1]['rsi_down_entry']:
            print(ticker)
            sma_rsi_sell_entry_tickers.append(ticker)

    sma_sell_entry_tickers_dict = {}
    sma_sell_entry_tickers_dict['tickers'] = sma_sell_entry_tickers

    with open(save_under_results_path("sma_sell_entry_tickers.json"), 'w') as f:
        json.dump(sma_sell_entry_tickers_dict, f, indent=4)

    rsi_sell_entry_tickers_dict = {}
    rsi_sell_entry_tickers_dict['tickers'] = rsi_sell_entry_tickers

    with open(save_under_results_path("rsi_sell_entry_tickers.json"), 'w') as f:
        json.dump(rsi_sell_entry_tickers_dict, f, indent=4)

    sma_rsi_sell_entry_tickers_dict = {}
    sma_rsi_sell_entry_tickers_dict['tickers'] = sma_rsi_sell_entry_tickers

    with open(save_under_results_path("sma_rsi_sell_entry_tickers.json"), 'w') as f:
        json.dump(sma_rsi_sell_entry_tickers_dict, f, indent=4)