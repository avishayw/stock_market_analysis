import random
import pandas as pd
import json
from datetime import datetime
from utils.get_all_stocks import get_all_snp_stocks, get_all_nyse_composite_stocks, get_all_nasdaq_100_stocks
from utils.download_stock_csvs import download_stock_day
from utils.paths import save_under_random_stock_data_path
from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart


def random_stock_data():
    # random stock
    tickers = get_all_nasdaq_100_stocks()
    stock_ok = False

    while not stock_ok:
        ticker = random.choice(tickers)
        df = pd.read_csv(download_stock_day(ticker))
        if len(df) < 1020:
            continue
        else:
            stock_ok = True

    # No date
    df['Datetime'] = pd.to_datetime(df['Date'])
    df['Days'] = pd.to_timedelta((df['Datetime'] - df.iloc[0]['Datetime']), unit='d').astype(str).map(
        lambda x: x[:-5])
    df['Old Date'] = df['Date']
    df['Date'] = df['Days']
    df.drop(columns=['Datetime', 'Days'])

    df = df[-1008:]
    # random range
    end = random.randint(600, len(df))
    start = end - random.randint(0, end-300)
    df = df[start:end]

    now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    # csv
    csv_path = save_under_random_stock_data_path(f'random_stock_data_{now}.csv')
    df.to_csv(csv_path)

    # json
    stock_dict = {'ticker': ticker,
                  'start_index': start,
                  'end_index': end}

    json_path = save_under_random_stock_data_path(f'random_stock_data_{now}.json')

    with open(json_path, 'w') as f:
        json.dump(stock_dict, f, indent=4)

    print(csv_path)
    return csv_path


def draw_result(save_time):
    json_file = save_time + '.json'
    with open(save_under_random_stock_data_path(json_file), 'r') as f:
        stock = json.load(f)
    ticker = stock['ticker']
    df = pd.read_csv(download_stock_day(ticker))
    print(f"Start date: {df.iloc[stock['start_index']]['Date']}" )
    print(f"End date: {df.iloc[stock['end_index']]['Date']}")
    fig = candlestick_chart_fig(df)
    fig.show()



if __name__=="__main__":
    import json
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from utils.paths import random_stock_data_path
    from indicators.my_indicators import percental_atr
    from indicators.momentum_indicators import simple_moving_average, rsi
    from indicators.trend_indicators import exponential_moving_average
    from indicators.volatility_indicators import average_true_range
    from plotting.candlestick_chart import candlestick_chart_fig, add_line_to_candlestick_chart

    df = pd.read_csv(random_stock_data())

    # indicators period
    sma_rapid = 10
    sma_fast = 20
    sma_medium = 50
    sma_slow = 200
    atr_priod = 14
    percental_atr_period = 14
    rsi_period = 14

    df = simple_moving_average(df, sma_rapid)
    df = simple_moving_average(df, sma_fast)
    df = simple_moving_average(df, sma_medium)
    df = simple_moving_average(df, sma_slow)
    df = rsi(df, rsi_period)
    # df = average_true_range(df, atr_priod)
    df = percental_atr(df, percental_atr_period)

    # Create subplots and mention plot grid size
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, subplot_titles=('OHLC', '%ATR', 'RSI'),
                        row_width=[0.2, 0.2, 0.7])

    # Plot OHLC on 1st row
    fig.add_trace(go.Candlestick(x=df["Date"], open=df["Open"], high=df["High"],
                                 low=df["Low"], close=df["Close"], name="OHLC"),
                  row=1, col=1
                  )

    fig.add_trace(go.Scatter(x=df['Date'], y=df[f'SMA{sma_rapid}'], name=f'SMA{sma_rapid}'),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df[f'SMA{sma_fast}'], name=f'SMA{sma_fast}'),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df[f'SMA{sma_medium}'], name=f'SMA{sma_medium}'),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df[f'SMA{sma_slow}'], name=f'SMA{sma_slow}'),
                  row=1, col=1)

    # Bar trace for volumes on 2nd row without legend
    # fig.add_trace(go.Bar(x=df['Date'], y=df[f'ATR{atr_priod}'], showlegend=False), row=2, col=1)
    fig.add_trace(go.Bar(x=df['Date'], y=df[f'%ATR{percental_atr_period}'], showlegend=False), row=2, col=1)
    fig.add_trace(go.Bar(x=df['Date'], y=df[f'RSI{rsi_period}'], showlegend=False), row=3, col=1)

    # Do not show OHLC's rangeslider plot
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.show()

