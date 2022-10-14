import numpy as np


def doji(df, max_body_ratio=0.002, max_shadow_ratio=0.02):
    """
    Doji represents an equilibrium between supply and demand, a tug of war that neither the bulls
    nor bears are winning. In the case of an uptrend, the bulls have by definition won previous battles
    because prices have moved higher. Now, the outcome of the latest skirmish is in doubt. After a long
    downtrend, the opposite is true. The bears have been victorious in previous battles, forcing prices
    down. Now the bulls have found courage to buy, and the tide may be ready to turn.
    :param df:
    :param open_close_ratio:
    :param max_shadow_ratio:
    :return: df
    """
    # TODO: fix and test values
    df['doji'] = np.where(((df['Close'] - df['Open']).abs()/df['Open'] <= max_body_ratio) &
                          ((df['High'] - df['Open'])/df['Open'] <= max_shadow_ratio) &
                          ((df['Open'] - df['Low'])/df['Open'] <= max_shadow_ratio), True, False)
    return df


def long_legged_doji(df, max_body_ratio=0.002, min_shadow_ratio=0.08):
    """
    Long legged doji is a far more dramatic candle. It says that prices moved far higher on the
    day, but then profit taking kicked in. Typically, a very large upper shadow is left. A close below the
    midpoint of the candle shows a lot of weakness.
    :param df:
    :param open_close_ratio:
    :param min_shadow_ratio:
    :return: df
    """
    # TODO: fix and test values
    df['long_legged_doji'] = np.where(((df['Close'] - df['Open']).abs()/df['Open'] <= max_body_ratio) &
                          ((df['High'] - df['Open'])/df['Open'] >= min_shadow_ratio) &
                          ((df['Open'] - df['Low'])/df['Open'] >= min_shadow_ratio), True, False)
    return df


def dragonfly_doji(df, max_body_ratio=0.002, max_upper_shadow_ratio=0.002, min_lower_shadow_ratio=0.08):
    """
    depicts a day on which prices opened high, sold off, and then returned to the
    opening price. Dragonflies are fairly infrequent. When they do occur, however, they often resolve
    bullishly (provided the stock is not already overbought as show by Bollinger bands and indicators such
    as stochastic).
    Note: Should be used after a definitive downtrend
    :param df:
    :param open_close_ratio:
    :param max_upper_shadow_ratio:
    :param min_lower_shadow_ratio:
    :return: df
    """
    # TODO: fix and test values
    df['dragonfly_doji'] = np.where(((df['Close'] - df['Open']).abs()/df['Open'] <= max_body_ratio) &
                          ((df['High'] - df['Open'])/df['Open'] <= max_upper_shadow_ratio) &
                          ((df['Open'] - df['Low'])/df['Open'] >= min_lower_shadow_ratio), True, False)
    return df


def gravestone_doji(df, max_body_ratio=0.002, min_upper_shadow_ratio=0.08, max_lower_shadow_ratio=0.002):
    """
    As the name implies, is probably the most ominous candle of all, on that
    day, price rallied, but could not stand the altitude they achieved. By the end of the day. They came
    back and closed at the same level.
    Note: Should be used after a definitive uptrend
    :param df:
    :param open_close_ratio:
    :param min_upper_shadow_ratio:
    :param max_lower_shadow_ratio:
    :return: df
    """
    # TODO: fix and test values
    df['gravestone_doji'] = np.where(((df['Close'] - df['Open']).abs()/df['Open'] <= max_body_ratio) &
                          ((df['High'] - df['Open'])/df['Open'] >= min_upper_shadow_ratio) &
                          ((df['Open'] - df['Low'])/df['Open'] <= max_lower_shadow_ratio), True, False)
    return df


def hanging_man(df, min_body_ratio=0.005, max_body_ratio=0.012, max_upper_shadow_body_ratio=1.2, min_lower_shadow_body_ratio=2):
    """
    So named because it looks like a person who has been executed with legs
    swinging beneath, always occurs after an extended uptrend The hangman occurs because traders,
    seeing a sell-off in the shares, rush in to grab the stock a bargain price
    Note: Should be used after a definitive uptrend
    :param df:
    :param min_body_ratio:
    :param max_body_ratio:
    :param max_upper_shadow_body_ratio:
    :param min_lower_shadow_body_ratio:
    :return: df
    """
    df['hanging_man'] = np.where(((df['Close'] > df['Open']) &
                             ((df['Open'] - df['Low']) >= min_lower_shadow_body_ratio * (
                                     df['Close'] - df['Open'])) &
                             ((df['Close'] - df['Open']) / df['Open'] >= min_body_ratio) &
                             ((df['Close'] - df['Open']) / df['Open'] <= max_body_ratio) &
                             ((df['High'] - df['Close']) <= max_upper_shadow_body_ratio * (
                                     df['Close'] - df['Open']))) |
                            ((df['Open'] > df['Close']) &
                             ((df['Close'] - df['Low']) >= min_lower_shadow_body_ratio * (
                                     df['Open'] - df['Close'])) &
                             ((df['Open'] - df['Close']) / df['Open'] >= min_body_ratio) &
                             ((df['Open'] - df['Close']) / df['Open'] <= max_body_ratio) &
                             ((df['High'] - df['Open']) <= max_upper_shadow_body_ratio * (
                                     df['Open'] - df['Close']))), True, False)
    return df


def hammer(df, min_body_ratio=0.005, max_body_ratio=0.012, max_upper_shadow_body_ratio=1.2, min_lower_shadow_body_ratio=2):
    """
    Puts in its appearance after prolonged downtrend. On the day of the hammer candle,
    there is strong selling, often beginning at the opening bell. As the day goes on, however, the market
    recovers and closes near the unchanged mark, or in some cased even higher. In these cases the
    market potentially is “hammering” out a bottom.
    Note: Should be used after a definitive downtrend
    :param df:
    :param min_body_ratio:
    :param max_body_ratio:
    :param max_upper_shadow_body_ratio:
    :param min_lower_shadow_body_ratio:
    :return:
    """
    df['hammer'] = np.where(((df['Close'] > df['Open']) &
                                  ((df['Open'] - df['Low']) >= min_lower_shadow_body_ratio * (
                                              df['Close'] - df['Open'])) &
                                  ((df['Close'] - df['Open']) / df['Open'] >= min_body_ratio) &
                                  ((df['Close'] - df['Open']) / df['Open'] <= max_body_ratio) &
                                  ((df['High'] - df['Close']) <= max_upper_shadow_body_ratio * (
                                              df['Close'] - df['Open']))) |
                                 ((df['Open'] > df['Close']) &
                                  ((df['Close'] - df['Low']) >= min_lower_shadow_body_ratio * (
                                              df['Open'] - df['Close'])) &
                                  ((df['Open'] - df['Close']) / df['Open'] >= min_body_ratio) &
                                  ((df['Open'] - df['Close']) / df['Open'] <= max_body_ratio) &
                                  ((df['High'] - df['Open']) <= max_upper_shadow_body_ratio * (
                                              df['Open'] - df['Close']))), True, False)
    return df


def shooting_star(df, min_body_ratio=0.005, max_body_ratio=0.012, max_lower_shadow_body_ratio=1.2, min_upper_shadow_body_ratio=2):
    """
    Can appear only at a potential market top. If a shooting star occurs after a candle
    with a large real body, typically it is that much stronger a warning because it shows that the price
    cannot sustain high levels. The day the shooting star occurs, the market ideally should gap higher . The
    stock should then rally sharply. At this point, it appears as though the longs are in complete control.
    Sometime during the day, however, profit taking ensues. The stock closes near the unchanged market,
    as shown by a small real body. Therefore a shooting star has a small real body and a large upper
    shadow. Typically, there will be either no lower shadow or a very small one.
    :param df:
    :param min_body_ratio:
    :param max_body_ratio:
    :param max_lower_shadow_body_ratio:
    :param min_upper_shadow_body_ratio:
    :return:
    """
    df['shooting_star'] = np.where(((df['Close'] > df['Open']) &
                                 ((df['High'] - df['Close']) >= min_upper_shadow_body_ratio*(df['Close']-df['Open'])) &
                                    ((df['Close'] - df['Open']) / df['Open'] >= min_body_ratio) &
                                    ((df['Close'] - df['Open']) / df['Open'] <= max_body_ratio) &
                                 ((df['Open'] - df['Low']) < max_lower_shadow_body_ratio*(df['Close'] - df['Open']))) |
                                 ((df['Open'] > df['Close']) &
                                  ((df['Open'] - df['Close']) / df['Open'] >= min_body_ratio) &
                                  ((df['Open'] - df['Close']) / df['Open'] <= max_body_ratio) &
                                  ((df['High'] - df['Open']) >= min_upper_shadow_body_ratio * (df['Open'] - df['Close'])) &
                                  ((df['Close'] - df['Low']) <= max_lower_shadow_body_ratio*(df['Open'] - df['Close']))), True, False)
    return df


def inverted_hammer(df, min_body_ratio=0.005, max_body_ratio=0.012, max_lower_shadow_body_ratio=1.2, min_upper_shadow_body_ratio=2):
    """
    Can only occur after a sustained downtrend, the stock is in all probability
    already oversold. Therefore, the inverted hammer signifies that traders who have held long positions
    in the security, most of whom are now showing large losses, often are quick to dump their shares by
    selling into strength.
    :param df:
    :param min_body_ratio:
    :param max_body_ratio:
    :param max_lower_shadow_body_ratio:
    :param min_upper_shadow_body_ratio:
    :return:
    """
    df['inverted_hammer'] = np.where(((df['Close'] > df['Open']) &
                                    ((df['High'] - df['Close']) >= min_upper_shadow_body_ratio * (
                                                df['Close'] - df['Open'])) &
                                    ((df['Close'] - df['Open']) / df['Open'] >= min_body_ratio) &
                                    ((df['Close'] - df['Open']) / df['Open'] <= max_body_ratio) &
                                    ((df['Open'] - df['Low']) < max_lower_shadow_body_ratio * (
                                                df['Close'] - df['Open']))) |
                                   ((df['Open'] > df['Close']) &
                                    ((df['Open'] - df['Close']) / df['Open'] >= min_body_ratio) &
                                    ((df['Open'] - df['Close']) / df['Open'] <= max_body_ratio) &
                                    ((df['High'] - df['Open']) >= min_upper_shadow_body_ratio * (
                                                df['Open'] - df['Close'])) &
                                    ((df['Close'] - df['Low']) <= max_lower_shadow_body_ratio * (
                                                df['Open'] - df['Close']))), True, False)
    return df


def bullish_engulfing(df, min_body_ratio=0.01):
    """
    Occurs after a significant downtrend. Note that the engulfing candle must
    encompass the real body of the previous candle, but need not surround the shadow.
    Note: Should be used after a definitive downtrend
    :param df:
    :param min_body_ratio:
    :return: df
    """
    # TODO: test
    df['bullish_engulfing'] = np.where((df.shift(1)['Open'] > df.shift(1)['Close']) &
                                       ((df.shift(1)['Open'] - df.shift(1)['Close'])/df.shift(1)['Open'] > min_body_ratio) &
                                       (df['Close'] > df['Open']) &
                                       (df['Open'] < df.shift(1)['Close']) &
                                       (df['Close'] > df.shift(1)['Open']), True, False)
    return df


def bearish_engulfing(df, min_body_ratio=0.01):
    """
    Occurs after a significant uptrend. Again, the shadows need not be surrounded.
    Note: Should be used after a definitive uptrend
    :param df:
    :param min_body_ratio:
    :return: df
    """
    # TODO: test
    df['bearish_engulfing'] = np.where((df.shift(1)['Close'] > df.shift(1)['Open']) &
                                       ((df.shift(1)['Close'] - df.shift(1)['Open'])/df.shift(1)['Open'] > min_body_ratio) &
                                       (df['Open'] > df['Close']) &
                                       (df['Close'] < df.shift(1)['Open']) &
                                       (df['Open'] > df.shift(1)['Close']), True, False)
    return df


def dark_cloud_cover(df, min_body_ratio=0.03):
    """
    The stock closes at least halfway into the previous white capping candle.
    The larger the penetration of the previous candle (that is , the closer this candle is a being a bearish
    engulfing), the more powerful the signal. Traders should pay particular attention to a dark cloud cover
    candle if it occurs at an important resistance area and if the end of day volume is strong.
    Note: Should be used after a definitive uptrend
    """
    # TODO: test
    df['dark_cloud_cover'] = np.where((df.shift(1)['Close'] > df.shift(1)['Open']) &
                                      ((df.shift(1)['Close'] - df.shift(1)['Open']) / df.shift(1)[
                                          'Open'] > min_body_ratio) &
                                      (df['Open'] > df['Close']) &
                                      (df['Open'] > df.shift(1)['Close']) &
                                       (df['Close'] < ((df.shift(1)['Close'] - df.shift(1)['Open'])/2 + df.shift(1)[
                                           'Open']))
                                      , True, False)
    return df


def bullish_piercing(df, min_body_ratio=0.01):
    """
    Often will end a minor downtrend (a downtrend that often lasts between five a
    fifteen trading days) The day before the piercing candle appears, the daily candle should ideally have a
    fairly large dark real body, signifying a strong down day. In the classic piercing pattern, the next day’s
    candle gaps below the lower shadow, or previous day’s low.
    Note: Should be used after a definitive downtrend
    """
    # TODO: test
    df['bullish_piercing'] = np.where((df.shift(1)['Open'] > df.shift(1)['Close']) &
                              ((df.shift(1)['Open'] - df.shift(1)['Close']) / df.shift(1)['Open'] > min_body_ratio) &
                                      (df['Close'] > df['Open']) &
                                      (df['Open'] < df.shift(1)['Close']) &
                                      (df['Close'] > ((df.shift(1)['Open'] - df.shift(1)['Close']) / 2 + df.shift(1)[
                                          'Close']))
                                      , True, False)
    return df


def bearish_piercing(df, min_body_ratio=0.01):
    # TODO: test
    df['bearish_piercing'] = np.where((df.shift(1)['Close'] > df.shift(1)['Open']) &
                              ((df.shift(1)['Close'] - df.shift(1)['Open']) / df.shift(1)['Open'] > min_body_ratio) &
                                      (df['Open'] > df['Close']) &
                                      (df['Open'] > df.shift(1)['Close']) &
                                      (df['Close'] < ((df.shift(1)['Close'] - df.shift(1)['Open']) / 2 + df.shift(1)[
                                          'Open']))
                                      , True, False)
    return df


def evening_doji_star(df, bull_min_body_ratio=0.03, doji_star_max_body_ratio=0.002, bear_min_body_ratio=0.03,
                      doji_star_max_shadow=0.01):
    """
    Occurs during a sustained uptrend. On the first day we see a candle with a
    long white body. Everything looks normal and the bulls appear to have full control of the stock. Tn the
    second day, however, a star candle occur. For this to be a valid evening star pattern, the stock must
    gap higher on the day of the star. The star can be either black or white. A star candle has a small real
    body and often contains a large upper shadow. On the third day, a candle with a black real body
    emerges. This candle retreats substantially into the real body of the first day. The pattern is made
    more powerful if there is a gap between the second and third day’s candles. However, this gap is
    unusual, particularly when it comes to equity trading. The further this third candle retreats into the
    real body of the first day’s candle, the more powerful the reversal signal.
    Note: Should be used after a definitive uptrend
    :param df:
    :param bull_min_body_ratio:
    :param doji_max_body_ratio:
    :param bear_min_body_ratio:
    :return: df
    """
    df['evening_doji_star'] = np.where(((df.shift(1)['Open'] - df.shift(1)['Close']).abs()/df.shift(1)['Open'] < doji_star_max_body_ratio) &
                                       ((df.shift(1)['High'] - df.shift(1)['Open'])/df.shift(1)['Open'] < doji_star_max_shadow) &
                                       ((df.shift(1)['Open'] - df.shift(1)['Low']) / df.shift(1)[
                                           'Open'] < doji_star_max_shadow) &
                                       (df.shift(2)['Close'] > df.shift(2)['Open']) &
                                       ((df.shift(2)['Open'] - df.shift(2)['Close']).abs()/df.shift(2)['Open'] > bull_min_body_ratio) &
                                       (df['Close'] < df['Open']) &
                                       ((df['Open'] - df['Close']).abs()/df['Open'] > bear_min_body_ratio) &
                                       (df['Close'] <= ((df.shift(2)['Close'] - df.shift(2)['Open'])/2 + df.shift(2)['Open'])) &
                                       (((df.shift(1)['Open'] > df.shift(1)['Close']) & (df.shift(1)['Close'] > df.shift(2)['Close'])) |
                                        ((df.shift(1)['Close'] > df.shift(1)['Open']) & (df.shift(1)['Open'] > df.shift(2)['Close']))), True, False)
    return df


def evening_star(df, bull_min_body_ratio=0.03, star_max_body_ratio=0.01, bear_min_body_ratio=0.03):
    """
    Occurs during a sustained uptrend. On the first day we see a candle with a
    long white body. Everything looks normal and the bulls appear to have full control of the stock. Tn the
    second day, however, a star candle occur. For this to be a valid evening star pattern, the stock must
    gap higher on the day of the star. The star can be either black or white. A star candle has a small real
    body and often contains a large upper shadow. On the third day, a candle with a black real body
    emerges. This candle retreats substantially into the real body of the first day. The pattern is made
    more powerful if there is a gap between the second and third day’s candles. However, this gap is
    unusual, particularly when it comes to equity trading. The further this third candle retreats into the
    real body of the first day’s candle, the more powerful the reversal signal.
    Note: Should be used after a definitive uptrend
    :param df:
    :param bull_min_body_ratio:
    :param doji_max_body_ratio:
    :param bear_min_body_ratio:
    :return: df
    """
    df['evening_star'] = np.where(((df.shift(1)['Open'] - df.shift(1)['Close']).abs()/df.shift(1)['Open'] < star_max_body_ratio) &
                                       (df.shift(2)['Close'] > df.shift(2)['Open']) &
                                       ((df.shift(2)['Open'] - df.shift(2)['Close']).abs()/df.shift(2)['Open'] > bull_min_body_ratio) &
                                       (df['Close'] < df['Open']) &
                                       ((df['Open'] - df['Close']).abs()/df['Open'] > bear_min_body_ratio) &
                                  (df['Close'] <= (
                                              (df.shift(2)['Close'] - df.shift(2)['Open']) / 2 + df.shift(2)['Open'])) &
                                       (((df.shift(1)['Open'] > df.shift(1)['Close']) & (df.shift(1)['Close'] > df.shift(2)['Close'])) |
                                        ((df.shift(1)['Close'] > df.shift(1)['Open']) & (df.shift(1)['Open'] > df.shift(2)['Close']))), True, False)
    return df


def morning_doji_star(df, bull_min_body_ratio=0.03, doji_star_max_body_ratio=0.002, bear_min_body_ratio=0.03,
                      doji_star_max_shadow=0.01):
    """
    That on the first day there is a large dark candle. The middle day is not a perfect
    star, because there is a small lower shadow, but the upper shadow on top of a small real body gives it
    a star quality. The third candle is a large white candle that completes the reversal. Not how the third
    candle recovered nearly to the highs of the first day and occurred on strong volume.
    :param df:
    :param bull_min_body_ratio:
    :param doji_star_max_body_ratio:
    :param bear_min_body_ratio:
    :param doji_star_max_shadow:
    :return: df
    """
    df['morning_doji_star'] = np.where(
        ((df.shift(1)['Open'] - df.shift(1)['Close']).abs() / df.shift(1)['Open'] < doji_star_max_body_ratio) &
        ((df.shift(1)['High'] - df.shift(1)['Open']) / df.shift(1)['Open'] < doji_star_max_shadow) &
        ((df.shift(1)['Open'] - df.shift(1)['Low']) / df.shift(1)[
            'Open'] < doji_star_max_shadow) &
        (df.shift(2)['Open'] > df.shift(2)['Close']) &
        ((df.shift(2)['Open'] - df.shift(2)['Close']).abs() / df.shift(2)['Open'] > bear_min_body_ratio) &
        (df['Close'] < df['Open']) &
        ((df['Open'] - df['Close']).abs() / df['Open'] > bull_min_body_ratio) &
        (df['Close'] >= ((df.shift(2)['Open'] - df.shift(2)['Close']) / 2 + df.shift(2)['Close'])) &
        (((df.shift(1)['Open'] > df.shift(1)['Close']) & (df.shift(1)['Open'] < df.shift(2)['Open'])) |
         ((df.shift(1)['Close'] > df.shift(1)['Open']) & (df.shift(1)['Close'] < df.shift(2)['Close']))), True, False)

    return df


def morning_star(df, bull_min_body_ratio=0.03, star_max_body_ratio=0.01, bear_min_body_ratio=0.03):
    """
    That on the first day there is a large dark candle. The middle day is not a perfect
    star, because there is a small lower shadow, but the upper shadow on top of a small real body gives it
    a star quality. The third candle is a large white candle that completes the reversal. Not how the third
    candle recovered nearly to the highs of the first day and occurred on strong volume.
    :param df:
    :param bull_min_body_ratio:
    :param star_max_body_ratio:
    :param bear_min_body_ratio:
    :return: df
    """
    df['morning_star'] = np.where(
        ((df.shift(1)['Open'] - df.shift(1)['Close']).abs() / df.shift(1)['Open'] < star_max_body_ratio) &
        (df.shift(2)['Open'] > df.shift(2)['Close']) &
        ((df.shift(2)['Open'] - df.shift(2)['Close']).abs() / df.shift(2)['Open'] > bear_min_body_ratio) &
        (df['Close'] < df['Open']) &
        ((df['Open'] - df['Close']).abs() / df['Open'] > bull_min_body_ratio) &
        (df['Close'] >= ((df.shift(2)['Open'] - df.shift(2)['Close']) / 2 + df.shift(2)['Close'])) &
        (((df.shift(1)['Open'] > df.shift(1)['Close']) & (df.shift(1)['Open'] < df.shift(2)['Open'])) |
         ((df.shift(1)['Close'] > df.shift(1)['Open']) & (df.shift(1)['Close'] < df.shift(2)['Close']))), True, False)
    return df


def spinning_top(df, max_body_ratio=0.02, min_body_ratio=0.002, min_shadow_body_ratio=2):
    """
    The shadow are relatively small and the candle has a very small range. When combined with
    low volume, traders may be expressing disinterest.
    Spinning Top High Wave Definition:
    A Spinning Top Wave, also called a High Wave candle, is candlestick that has an open and close price
    near each other which produces a small real body and color is of no importance. They also have long
    upper and lower shadows that significantly exceed the length of the body. These types of candlesticks
    indicate indecision and subsequent consolidation.
    Practical Use:
    Technical analysts will often watch for Spinning Top High Wave candlesticks and then "join the
    sidelines." After such a volatile session, traders will often wait for additional confirmation of an
    upward or downward price movement.
    :param df:
    :param max_body_ratio:
    :param min_body_ratio:
    :param min_shadow_body_ratio:
    :return: df
    """
    df['spinning_top'] = np.where(
        (min_body_ratio <= (df['Close'] - df['Open']).abs()/df['Open']) &
        ((df['Close'] - df['Open']).abs()/df['Open'] < max_body_ratio) &
        (
            ((df['Close'] > df['Open']) & ((df['High']-df['Close']) >= (df['Close'] - df['Open'])*min_shadow_body_ratio) &
             ((df['Open'] - df['Low']) >= (df['Close'] - df['Open'])*min_shadow_body_ratio)) |
            ((df['Open'] > df['Close']) & (
                        (df['High'] - df['Open']) >= (df['Open'] - df['Close']) * min_shadow_body_ratio) &
             ((df['Close'] - df['Low']) >= (df['Open'] - df['Close']) * min_shadow_body_ratio))
        ), True, False
    )
    return df


if __name__ == "__main__":
    from datetime import datetime
    from utils.download_stock_csvs import download_stock_day
    from utils.get_all_stocks import get_all_nasdaq_100_stocks, get_all_snp_stocks, get_all_nyse_composite_stocks
    from utils.paths import save_under_results_path
    from detectors.trends import successive_trends_detector
    from indicators.trend_indicators import exponential_moving_average, average_directional_movement
    from indicators.momentum_indicators import simple_moving_average, stochastic
    import pandas as pd
    import numpy as np
    # Candlestick pattern recognition test - graph to code

    # ticker = 'AAPL'
    # candlestick_pattern_date = datetime.strptime('2022-02-16', '%Y-%m-%d')
    #
    # df = pd.read_csv(download_stock_day(ticker))
    # df['Datetime'] = pd.to_datetime(df['Date'])
    # df = hanging_man(df)
    #
    #
    # test_df = df.loc[df['Datetime'] == candlestick_pattern_date]
    # print(test_df)

    # Candlestick pattern recognition test - code to graph

    tickers = get_all_nasdaq_100_stocks()
    # ticker = 'AAPL'

    hammers = []
    for ticker in tickers:
        try:
            df = pd.read_csv(download_stock_day(ticker))
        except ValueError:
            continue
        df['Datetime'] = pd.to_datetime(df['Date'])
        df = df.loc[df['Datetime'] > datetime(2018, 8, 13, 0, 0, 0)]

        # Ratios
        df['upper_shadow_body_ratio'] = np.where(df['Close'] > df['Open'], ((df['High'] - df['Close'])/(df['Close'] - df['Open'])), ((df['High'] - df['Open'])/(df['Open'] - df['Close'])))
        df['lower_shadow_body_ratio'] = np.where(df['Close'] > df['Open'], ((df['Open'] - df['Low'])/(df['Close'] - df['Open'])), ((df['Close'] - df['Low'])/(df['Open'] - df['Close'])))
        df['body_ratio'] = (df['Close'] - df['Open']).abs()/df['Open']

        # Trends
        df = successive_trends_detector(df)

        # Indicators
        df = average_directional_movement(df, 14) #ADX
        df = stochastic(df, 14)
        df['stochastic_smooth'] = df['stochastic'].rolling(3).mean()
        df = simple_moving_average(df, 200)
        df['SMA200_angle'] = (df['SMA200'] - df.shift(1)['SMA200']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
        df = exponential_moving_average(df, 'Close', 50)
        df['EMA50_angle'] = (df['EMA50'] - df.shift(1)['EMA50']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))
        df = exponential_moving_average(df, 'Close', 20)
        df['EMA20_angle'] = (df['EMA20'] - df.shift(1)['EMA20']).apply(
        lambda x: np.arctan(x) * (180 / np.pi))

        # Patterns
        # df = doji(df)
        # df = long_legged_doji(df)
        # df = dragonfly_doji(df)
        # df = gravestone_doji(df)
        df = hammer(df)
        # df = hanging_man(df)
        # df = spinning_top(df)
        # df = shooting_star(df)
        # df = morning_star(df)
        # df = morning_doji_star(df)
        # df = evening_doji_star(df)
        # df = evening_star(df)
        # df = bearish_engulfing(df)
        # df = bullish_engulfing(df)
        # df = bullish_piercing(df)
        # df = dark_cloud_cover(df)
        df = inverted_hammer(df)
        df['pattern'] = np.where(df['hammer'] | df['inverted_hammer'], True, False)
        result_df = df.loc[df['pattern']]
        for index in result_df.index.tolist():

            uptrend_after = 0
            downtrend_after = 0
            i = 1
            while df.shift(-i)._get_value(index, 'uptrend') != 0 and not np.isnan(df.shift(-i)._get_value(index, 'uptrend')):
                uptrend_after = df.shift(-i)._get_value(index, 'uptrend')
                roc_after = (df.shift(-i)._get_value(index, 'median') - df._get_value(index,'median'))/df._get_value(index,'median')
                i += 1
            if uptrend_after == 0:
                i = 1
                while df.shift(-i)._get_value(index, 'downtrend') != 0 and not np.isnan(df.shift(-i)._get_value(index, 'downtrend')):
                    downtrend_after = df.shift(-i)._get_value(index, 'downtrend')
                    roc_after = (df.shift(-i)._get_value(index, 'median') - df._get_value(index,
                                                                                          'median')) / df._get_value(
                        index, 'median')
                    i += 1
            hammers.append(
                {'Stock': ticker,
                 'Date': result_df._get_value(index, 'Date'),
                 'body_ratio': result_df._get_value(index, 'body_ratio'),
                 'upper_shadow_body_ratio': result_df._get_value(index, 'upper_shadow_body_ratio'),
                 'lower_shadow_body_ratio': result_df._get_value(index, 'lower_shadow_body_ratio'),
                 'day_uptrend': df._get_value(index, 'uptrend'),
                 'day_before_uptrend': df.shift(1)._get_value(index, 'uptrend'),
                 'day_downtrend': df._get_value(index, 'downtrend'),
                 'day_before_downtrend': df.shift(1)._get_value(index, 'downtrend'),
                 'hammer?': result_df._get_value(index, 'hammer'),
                 'inverted_hammer?': result_df._get_value(index, 'inverted_hammer'),
                 'uptrend_after': uptrend_after,
                 'downtrend_after': downtrend_after,
                 'roc_after': roc_after,
                 'sma200_angle': df._get_value(index, 'SMA200_angle'),
                 'low_above_sma200': df._get_value(index, 'SMA200') > df._get_value(index, 'Low'),
                 'ema50_angle': df._get_value(index, 'EMA50_angle'),
                 'low_above_ema50': df._get_value(index, 'EMA50') > df._get_value(index, 'Low'),
                 'ema20_angle': df._get_value(index, 'EMA20_angle'),
                 'low_above_ema20': df._get_value(index, 'EMA20') > df._get_value(index, 'Low'),
                 'adx': df._get_value(index, 'ADX14'),
                 'DI+': df._get_value(index, 'DI+14'),
                 'DI-': df._get_value(index, 'DI-14'),
                 'stoch': df._get_value(index, 'stochastic'),
                 'stoch_sma3': df._get_value(index, 'stochastic_smooth')}
            )
        pd.DataFrame(hammers).to_csv(save_under_results_path('candle_stick_patterns/hammers/all_hammers.csv'))
        result_df.to_csv(save_under_results_path(f'candle_stick_patterns/hammers/{ticker}_hammers_recognized.csv'))

    # df['pattern'] = np.where(df['doji'] | df['long_legged_doji'] | df['dragonfly_doji'] | df['gravestone_doji'] |
    #                          df['hammer'] | df['inverted_hammer'] | df['shooting_star'] | df['hanging_man'] |
    #                          df['spinning_top'] | df['morning_star'] | df['morning_doji_star'] | df['evening_star'] |
    #                          df['evening_doji_star'] | df['bearish_engulfing'] | df['bullish_engulfing'] |
    #                          df['piercing'] | df['dark_cloud_cover'], True, False)




