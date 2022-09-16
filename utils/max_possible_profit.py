

def max_possible_profit_long(ticker, df):

    df['change'] = ((df['Close'] - df['Open'])/df['Open'])
    cap = 100.0

    for i in range(len(df)):
        change = df.iloc[i]['change']
        if change > 0:
            cap = cap * (1 + change)

    print(ticker, cap)
    return cap


def max_possible_profit(ticker, df):

    df['change'] = ((df['Close'] - df['Open']) / df['Open'])
    cap = 100.0

    for i in range(len(df)):
        change = df.iloc[i]['change']
        if change > 0:
            cap = cap * (1 + change)
        else:
            cap = cap * (1 - change)

    print(ticker, cap)
    return cap


def max_possible_profit_short(ticker, df):

    df['change'] = ((df['Close'] - df['Open'])/df['Open'])
    cap = 100.0

    for i in range(len(df)):
        change = df.iloc[i]['change']
        if change < 0:
            cap = cap * (1 - change)

    print(ticker, cap)
    return cap


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
        final_cap = max_possible_profit(ticker, df)
        buy_and_hold = ((df.iloc[-1]["Close"])/df.iloc[0]["Close"])*100.0
        ticker_returns.append({'ticker': ticker, 'return': ((final_cap - 100.0) / 100.0) * 100.0, 'buy&hold': buy_and_hold})
        pd.DataFrame(ticker_returns).to_csv(
            save_under_results_path('max_possible_profit.csv'))

    print(time.time() - start_time)