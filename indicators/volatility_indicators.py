from ta.volatility import AverageTrueRange


def average_true_range(df, period):
    df['ATR'] = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=period).average_true_range()
    return df


