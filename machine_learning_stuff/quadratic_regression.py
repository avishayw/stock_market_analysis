import numpy as np
from utils.download_stock_csvs import download_stock_day
import pandas as pd
from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart


ticker = 'ASRT'

df = pd.read_csv(download_stock_day(ticker))
df['datetime'] = pd.to_datetime(df['Date'])
df['epoch'] = df['datetime'].apply(lambda x: x.timestamp())
df['quadreg'] = np.nan

df.reset_index(inplace=True)

length = 10

for i in range(length, len(df)):

    sample_df = pd.DataFrame.copy(df[i-length:i])
    x = df['epoch'].to_numpy()
    y = df['Close'].to_numpy()
    fittedParameters = np.polyfit(x, y, 20)
    df.loc[i, 'quadreg'] = np.polyval(fittedParameters, df.iloc[i]['epoch'])


fig = candlestick_chart_fig(df, ticker)
fig = add_line_to_candlestick_chart(fig, df['Date'], df['quadreg'], 'quadreg')
fig.show()


# if __name__=="__main__":
#     ticker = 'AAPL'
#
#     df = pd.read_csv(download_stock_day(ticker))[-1008:]
#
#     df['datetime'] = pd.to_datetime(df['Date'])
#     df['epoch'] = df['datetime'].apply(lambda x: x.timestamp())
#     df['median'] = (df['High'] - df['Low'])/2 + df['Low']
#     df['linreg10'] = np.nan
#
#     df.reset_index(inplace=True)
#
#     for i in range(10, len(df)-1):
#         sample_df = pd.DataFrame.copy(df[i-10:i])
#         x = sample_df['epoch'].to_numpy().reshape(-1, 1)
#         y = sample_df['median'].to_numpy()
        # model = LinearRegression()
        # model.fit(x, y)
        # df.loc[i, 'linreg10'] = model.predict(np.array(df.iloc[i]['epoch']).reshape(-1, 1))

    # fig = candlestick_chart_fig(df, ticker)
    # fig = add_line_to_candlestick_chart(fig, df['Date'], df['linreg10'], 'linreg10')

    # fig.show()