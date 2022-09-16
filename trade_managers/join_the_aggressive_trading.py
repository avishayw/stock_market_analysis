from indicators.my_indicators import percental_atr
import numpy as np
import pandas as pd
from datetime import datetime


def join_aggressive_buy(ticker, df, period, vol_ratio=2.0):

    df['Datetime'] = pd.to_datetime(df['Date'])
    df = percental_atr(df, period)
    df[f'SMVA{period}'] = df['Volume'].rolling(period).mean()
    df['change%'] = ((df['Close']-df.shift(1)['Close'])/df.shift(1)['Close'])*100.0

    df['buy_signal'] = np.where((df['change%'] > df.shift(1)[f'%ATR{period}']) &
                                (df['Volume'] >= df.shift(1)[f'SMVA{period}']*vol_ratio), True, False)

    i = 0
    long_position = False
    enter_price = None
    enter_date = None
    cap = 100.0
    take_profit_ratio = 1.1

    trades = []

    while i < len(df):
        if long_position:
            if df.iloc[i]['High'] >= enter_price*take_profit_ratio:
                if df.iloc[i]['Open'] >= enter_price*take_profit_ratio:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = enter_price*take_profit_ratio
                long_position = False
            elif df.iloc[i]['Low'] <= stop_loss:
                if df.iloc[i]['Open'] <= stop_loss:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = stop_loss
                long_position = False
            if not long_position:
                exit_date = df.iloc[i]['Date']
                period_df = df.loc[(df['Datetime'] >= datetime.strptime(enter_date, '%Y-%m-%d')) &
                                   (df['Datetime'] <= datetime.strptime(exit_date, '%Y-%m-%d'))].copy()
                period_max = period_df['High'].max()
                period_max_pct = ((period_max - enter_price) / enter_price) * 100
                period_min = period_df['Low'].min()
                period_min_pct = ((period_min - enter_price) / enter_price) * 100
                period_max_idx = period_df['High'].idxmax()
                period_min_idx = period_df['Low'].idxmin()
                max_before_min = period_max_idx < period_min_idx
                # try:
                #     print(f'period_max: {period_max}\n'
                #           f'rapid_angle: {df.loc[period_max_idx, f"EMA{rapid}angle"]}\n'
                #           f'rapid_angle+day: {df.loc[period_max_idx + 1, f"EMA{rapid}angle"]}\n'
                #           f'fast_angle: {df.loc[period_max_idx, f"EMA{fast}angle"]}\n'
                #           f'fast_angle+day: {df.loc[period_max_idx + 1, f"EMA{fast}angle"]}\n'
                #           f'avg_vol_rapid_angle: {df.loc[period_max_idx, f"avg_volume_{rapid}_angle"]}\n'
                #           f'avg_vol_rapid_angle+day: {df.loc[period_max_idx + 1, f"avg_volume_{rapid}_angle"]}\n'
                #           f'avg_vol_fast_angle: {df.loc[period_max_idx, f"avg_volume_{fast}_angle"]}\n'
                #           f'avg_vol_fast_angle+day: {df.loc[period_max_idx + 1, f"avg_volume_{fast}_angle"]}\n')
                # except IndexError:
                #     print(period_max_idx)
                #     print(len(df))
                #     exit()
                cap = cap * (1.0 + ((exit_price - enter_price) / enter_price))
                trade_dict = {'symbol': ticker,
                              'type': 'long',
                              'enter_date': enter_date,
                              'enter_price': enter_price,
                              'exit_date': exit_date,
                              'exit_price': exit_price,
                              'period_max': period_max,
                              'period_max_%': period_max_pct,
                              'period_min': period_min,
                              'period_min_%': period_min_pct,
                              'max_before_min': max_before_min,
                              'win': exit_price > enter_price,
                              'change%': ((exit_price - enter_price) / enter_price) * 100}
                print(trade_dict)
                trades.append(trade_dict)
        elif df.iloc[i]['buy_signal']:
            enter_price = df.shift(-1).iloc[i]['Open']
            enter_date = df.shift(-1).iloc[i]['Date']
            stop_loss = df.iloc[i]['Low']
            long_position = True

        i += 1

    print(ticker, cap)
    return trades, cap


if __name__=="__main__":
    from utils.get_all_stocks import get_all_snp_stocks, get_all_nasdaq_100_stocks, get_all_dow_jones_industrial_stocks
    from utils.download_stock_csvs import download_stock_day
    from utils.paths import save_under_results_path
    import pandas as pd
    import time

    start_time = time.time()

    tickers = list(set(get_all_snp_stocks() + get_all_nasdaq_100_stocks() + get_all_dow_jones_industrial_stocks() + ['SPY']))
    # tickers = ['SPY']
    ticker_returns = []
    all_trades = []

    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        df = df[-1008:]
        trades, final_cap = join_aggressive_buy(ticker, df, 14, vol_ratio=1.2)
        buy_and_hold = ((df.iloc[-1]["Close"])/df.iloc[0]["Close"])*100.0
        print(f'buy & hold: {buy_and_hold}')
        all_trades = all_trades + trades
        ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0, 'buy&hold': buy_and_hold})
        pd.DataFrame(all_trades).to_csv(
            save_under_results_path(f'pvt_trading_long_all_trades.csv'))
        pd.DataFrame(ticker_returns).to_csv(
            save_under_results_path('pvt_trading_long_ticker_returns.csv'))

    print(time.time() - start_time)
