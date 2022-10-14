import pandas as pd
import numpy as np


def both_trendlines(df, candleid, backcandles=100):
    """
    Returns slope and intercept. Use with X as idx number (not date/epoch)
    """
    brange = int(np.floor(backcandles*0.9))
    wind = 5

    # MAX
    max_touched_count_opt = 0

    for r1 in range(backcandles - brange, backcandles + brange):
        maxim = np.array([])
        xxmax = np.array([])

        if r1 > candleid:
            continue
        for i in range(candleid - r1, candleid + 1 - wind, wind):
            try:
                maxim = np.append(maxim, df.High.iloc[i:i + wind].max())
                xxmax = np.append(xxmax, df.High.iloc[i:i + wind].idxmax())
            except ValueError as e:
                print(e)
                print('i', i)
                print('len', len(df))
                print('r1', r1)
                print('candleid', candleid)
                exit()

        slmax, intercmax = np.polyfit(xxmax, maxim, 1)

        adjintercmax = (df.High.iloc[xxmax] - slmax * xxmax).max()

        max_breached = False
        max_touched_count = 0
        for i in range(int(min(xxmax)), int(max(xxmax))+1):
            y = df.High.iloc[i]
            y_tag = slmax*i+adjintercmax
            if y > y_tag*1.005:
                max_breached = True
                break
            elif y*0.995 <= y_tag <= y*1.005:
                max_touched_count += 1

        if max_touched_count > max_touched_count_opt and not max_breached:
            max_touched_count_opt = max_touched_count
            slmaxopt = slmax
            adjintercmaxopt = adjintercmax

    if max_touched_count_opt == 0:
        slmaxopt, adjintercmaxopt = None, None

    # MIN
    min_touched_count_opt = 0

    for r1 in range(backcandles - brange, backcandles + brange):
        minim = np.array([])
        xxmin = np.array([])

        if r1 > candleid:
            continue
        for i in range(candleid - r1, candleid + 1 - wind, wind):
            try:
                minim = np.append(minim, df.Low.iloc[i:i + wind].min())
                xxmin = np.append(xxmin, df.Low.iloc[i:i + wind].idxmin())
            except ValueError as e:
                print(e)
                print('i', i)
                print('len', len(df))
                print('r1', r1)
                print('candleid', candleid)
                exit()

        slmin, intercmin = np.polyfit(xxmin, minim, 1)

        adjintercmin = (df.Low.iloc[xxmin] - slmin * xxmin).min()

        min_breached = False
        min_touched_count = 0
        for i in range(int(min(xxmin)), int(max(xxmin)) + 1):
            y = df.Low.iloc[i]
            y_tag = slmin * i + adjintercmin
            if y < y_tag * 0.995:
                min_breached = True
                break
            elif y * 0.995 <= y_tag <= y * 1.005:
                min_touched_count += 1

        if min_touched_count > min_touched_count_opt and not min_breached:
            min_touched_count_opt = min_touched_count
            slminopt = slmin
            adjintercminopt = adjintercmin

    if min_touched_count_opt == 0:
        slminopt, adjintercminopt = None, None

    return slmaxopt, adjintercmaxopt, slminopt, adjintercminopt


def upper_trendline(df, candleid, backcandles=100):
    """
    Returns slope and intercept. Use with X as idx number (not date/epoch)
    """
    brange = int(np.floor(backcandles * 0.9))
    wind = 5

    # MAX
    max_touched_count_opt = 0

    for r1 in range(backcandles - brange, backcandles + brange):
        maxim = np.array([])
        xxmax = np.array([])

        if r1 > candleid:
            continue
        for i in range(candleid - r1, candleid + 1 - wind, wind):
            try:
                maxim = np.append(maxim, df.High.iloc[i:i + wind].max())
                xxmax = np.append(xxmax, df.High.iloc[i:i + wind].idxmax())
            except ValueError as e:
                print(e)
                print('i', i)
                print('len', len(df))
                print('r1', r1)
                print('candleid', candleid)
                exit()

        slmax, intercmax = np.polyfit(xxmax, maxim, 1)

        adjintercmax = (df.High.iloc[xxmax] - slmax * xxmax).max()

        max_breached = False
        max_touched_count = 0
        for i in range(int(min(xxmax)), int(max(xxmax)) + 1):
            y = df.High.iloc[i]
            y_tag = slmax * i + adjintercmax
            if y > y_tag * 1.005:
                max_breached = True
                break
            elif y * 0.995 <= y_tag <= y * 1.005:
                max_touched_count += 1

        if max_touched_count > max_touched_count_opt and not max_breached:
            max_touched_count_opt = max_touched_count
            slmaxopt = slmax
            adjintercmaxopt = adjintercmax
            backcandlesopt = r1

    if max_touched_count_opt == 0:
        return None, None, None

    return slmaxopt, adjintercmaxopt, backcandlesopt


def lower_trendline(df, candleid, backcandles=100):
    """
    Returns slope and intercept. Use with X as idx number (not date/epoch)
    """
    brange = int(np.floor(backcandles * 0.9))
    wind = 5

    # MIN
    min_touched_count_opt = 0

    for r1 in range(backcandles - brange, backcandles + brange):
        minim = np.array([])
        xxmin = np.array([])

        if r1 > candleid:
            continue
        for i in range(candleid - r1, candleid + 1 - wind, wind):
            try:
                minim = np.append(minim, df.Low.iloc[i:i + wind].min())
                xxmin = np.append(xxmin, df.Low.iloc[i:i + wind].idxmin())
            except ValueError as e:
                print(e)
                print('i', i)
                print('len', len(df))
                print('r1', r1)
                print('candleid', candleid)
                exit()

        slmin, intercmin = np.polyfit(xxmin, minim, 1)

        adjintercmin = (df.Low.iloc[xxmin] - slmin * xxmin).min()

        min_breached = False
        min_touched_count = 0
        for i in range(int(min(xxmin)), int(max(xxmin)) + 1):
            y = df.Low.iloc[i]
            y_tag = slmin * i + adjintercmin
            if y < y_tag * 0.995:
                min_breached = True
                break
            elif y * 0.995 <= y_tag <= y * 1.005:
                min_touched_count += 1

        if min_touched_count > min_touched_count_opt and not min_breached:
            min_touched_count_opt = min_touched_count
            slminopt = slmin
            adjintercminopt = adjintercmin
            backcandlesopt = r1

    if min_touched_count_opt == 0:
        return None, None, None

    return slminopt, adjintercminopt, backcandlesopt

