import dateutil.parser
from dateutil.relativedelta import relativedelta
from datetime import datetime
import pandas as pd
import numpy as np


def add_trading_dates_to_df(df, end_datetime):
    columns = df.columns.tolist()
    new_dates = []
    final_day = pd.to_datetime(df['Date']).iloc[-1]
    num_days = (end_datetime - final_day).days

    for i in range(1, num_days):
        date = final_day + relativedelta(days=i)
        if date.weekday() != 5 and 6:
            new_dates.append(date)

    list_for_df = []
    for i in range(len(new_dates)):
        list_for_df.append([new_dates[i].strftime('%Y-%m-%d'), np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN])

    df_new = pd.DataFrame(list_for_df, columns=columns)
    df = pd.concat([df, df_new])

    return df


if __name__=="__main__":
    from utils.download_stock_csvs import download_stock_day
    from datetime import datetime
    import numpy as np

    ticker = 'AAPL'
    df = pd.read_csv(download_stock_day(ticker))
    end_datetime = datetime(2022, 9, 22, 0, 0, 0)


