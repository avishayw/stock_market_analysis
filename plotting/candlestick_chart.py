import plotly.graph_objects as go
from plotly.subplots import make_subplots


def candlestick_chart_fig(df, ticker):
    fig = go.Figure(go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'], name=ticker, yaxis='y1')).update_layout(xaxis_rangeslider_visible=False)
    return fig


def add_line_to_candlestick_chart(fig, x, y, name):
    fig.add_trace(go.Scatter(x=x, y=y, name=name, yaxis='y1'))
    return fig


def add_markers_to_candlestick_chart(fig, x, y, name, color):
    """
    colors: red, blue, green, yellow, black, white
    :param fig:
    :param x:
    :param y:
    :param name:
    :param color:
    :return:
    """
    colors = {'blue': 'rgb(0,0,255)', 'red': 'rgb(255,0,0)', 'green': 'rgb(0,255,0)', 'yellow': 'rgb(255,255,0)', 'black': 'rgb(0,0,0)', 'white': 'rgb(255,255,255)'}
    # fig.add_trace(go.Scatter(line=dict(color=colors[color]), x=x, y=y, name=name, mode='markers'))
    fig.add_trace(go.Scatter(x=x, y=y, name=name, mode='markers', marker=go.scatter.Marker(size=10, color=color, colorscale="Viridis")))
    return fig


def multiple_windows_chart(ticker, df, chart_dict):
    """
    Create multiple window chart
    :param ticker: For naming the chart
    :param df: Dataframe to get the data from

    :param kwargs: Dictionary of columns names and their respective row. Keys are tuples, with the first argument being
     the row number, and the second argument being the window name. values are list of columns to be drawn on that row.
    Note: Don't include the candle chart columns!
    Format: {(1, window_name): [columns], (2, window_name): [columns], ....}

    :return: fig
    """
    row_width = []
    subplot_titles = [f'{ticker}']
    for row in chart_dict.keys():
        if row[0] == 1:
            continue
        row_width.append(0.2)
        subplot_titles.append(row[1])
    row_width.append(0.5)

    fig = make_subplots(rows=len(row_width), cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, subplot_titles=tuple(subplot_titles),
                        row_width=row_width)

    # Plot OHLC on 1st row
    fig.add_trace(go.Candlestick(x=df["Date"], open=df["Open"], high=df["High"],
                                 low=df["Low"], close=df["Close"], name="OHLC"),
                  row=1, col=1)

    for row in chart_dict.keys():
        for column in chart_dict[row]:
            fig.add_trace(go.Scatter(x=df['Date'], y=df[column], name=column), row=row[0], col=1)

    fig.update(layout_xaxis_rangeslider_visible=False)

    return fig


if __name__ == "__main__":
    pass