from utils.download_stock_csvs import download_stock_day
from utils import get_all_stocks
import pandas as pd
from utils.paths import save_under_results_path


def fifty_two_week(ticker, df, abs_change_pct=10.0):
    """
    This function will check the statistics of what is happening to a stock price once it breaks the 52-week high
    or low.

    The test will be like this: First, checking the 52-week high and low for every day, and if the stock price
    passes the high or low - check for every day if the stock reached 10% up or down since the 52-week-high/low
    price.

    This function will return a list of dictionaries describing the results.
    :param ticker:
    :param df:
    :return:
    """

    df['Datetime'] = pd.to_datetime(df['Date'])
    # df.set_index('Datetime', inplace=True)
    df['52weekHigh'] = df.shift(1)['High'].rolling(252).max()
    df['52weekHighIndex'] = df.shift(1)['High'].rolling(252).apply(lambda x: x[::-1].idxmax())
    df['52weekHighDatetime'] = df['52weekHighIndex'].apply(lambda x: df['Datetime'].loc[x] if not pd.isnull(x) else x)
    df['52weekLow'] = df.shift(1)['Low'].rolling(252).min()
    df['52weekLowIndex'] = df.shift(1)['Low'].rolling(252).apply(lambda x: x[::-1].idxmin())
    df['52weekLowDatetime'] = df['52weekLowIndex'].apply(lambda x: df['Datetime'].loc[x] if not pd.isnull(x) else x)
    df.dropna()

    price_crossing_list = []
    i = 0
    new_high = False
    new_low = False

    while i < len(df):
        if new_high:
            if df.iloc[i]['High'] > tp:
                if df.iloc[i]['Open'] > tp:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = tp
                exit_date = df.iloc[i]['Date']
                change = ((exit_price - enter_price)/enter_price)*100.0
                new_dict = {'symbol': ticker,
                                 'type': '52weekHigh',
                                 'newDate': enter_date,
                                 'changeThresholdDate': exit_date,
                                 'change': change,
                            'result': 'up'}
                print(new_dict)
                price_crossing_list.append(new_dict)
                new_high = False
            elif df.iloc[i]['Low'] < sl:
                if df.iloc[i]['Open'] < sl:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = sl
                exit_date = df.iloc[i]['Date']
                change = ((exit_price - enter_price)/enter_price)*100.0
                new_dict = {'symbol': ticker,
                                 'type': '52weekHigh',
                                 'newDate': enter_date,
                                 'changeThresholdDate': exit_date,
                                 'change': change,
                            'result': 'down'}
                print(new_dict)
                price_crossing_list.append(new_dict)
                new_high = False
        elif new_low:
            if df.iloc[i]['High'] > tp:
                if df.iloc[i]['Open'] > tp:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = tp
                exit_date = df.iloc[i]['Date']
                change = ((exit_price - enter_price) / enter_price) * 100.0
                new_dict = {'symbol': ticker,
                                 'type': '52weekLow',
                                 'newDate': enter_date,
                                 'changeThresholdDate': exit_date,
                                 'change': change,
                            'result': 'up'}
                print(new_dict)
                price_crossing_list.append(new_dict)
                new_low = False
            elif df.iloc[i]['Low'] < sl:
                if df.iloc[i]['Open'] < sl:
                    exit_price = df.iloc[i]['Open']
                else:
                    exit_price = sl
                exit_date = df.iloc[i]['Date']
                change = ((exit_price - enter_price) / enter_price) * 100.0
                new_dict = {'symbol': ticker,
                                 'type': '52weekLow',
                                 'newDate': enter_date,
                                 'changeThresholdDate': exit_date,
                                 'change': change,
                            'result': 'down'}
                print(new_dict)
                price_crossing_list.append(new_dict)
                new_low = False
        elif (df.iloc[i]['High'] > df.iloc[i]['52weekHigh']) and (df.iloc[i]['Datetime'] - df.iloc[i]['52weekHighDatetime']).days > 30:
            if df.iloc[i]['Open'] > df.iloc[i]['52weekHigh']:
                enter_price = df.iloc[i]['Open']
            else:
                enter_price = df.iloc[i]['52weekHigh']
            enter_date = df.iloc[i]['Date']
            tp = enter_price*(1+(abs_change_pct/100.0))
            sl = enter_price*(1-(abs_change_pct/100.0))
            new_high = True
        elif (df.iloc[i]['Low'] < df.iloc[i]['52weekLow']) and (df.iloc[i]['Datetime'] - df.iloc[i]['52weekLowDatetime']).days > 30:
            if df.iloc[i]['Open'] < df.iloc[i]['52weekLow']:
                enter_price = df.iloc[i]['Open']
            else:
                enter_price = df.iloc[i]['52weekLow']
            enter_date = df.iloc[i]['Date']
            tp = enter_price * (1 + (abs_change_pct / 100.0))
            sl = enter_price * (1 - (abs_change_pct / 100.0))
            new_low = True
        i += 1

    return price_crossing_list


research_results = []
pct = 3

tickers = list(set(get_all_stocks.get_all_nasdaq_100_stocks() +
                   get_all_stocks.get_all_snp_stocks() +
                   get_all_stocks.get_all_dow_jones_industrial_stocks()))

for ticker in tickers:
    try:
        df = pd.read_csv(download_stock_day(ticker))[-2016:].reset_index()
    except ValueError:
        continue

    research_results = research_results + fifty_two_week(ticker, df, abs_change_pct=pct)
    pd.DataFrame(research_results).to_csv(save_under_results_path(f"52-week-new-30d-diff-results-{pct}.csv"))

