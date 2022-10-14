

def is_peak_definitive(df, i):
    if df.shift(2).iloc[i]['High'] > df.shift(1).iloc[i]['High']:
        return False
    elif df.shift(1).iloc[i]['High'] > df.iloc[i]['High']:
        return False
    elif df.shift(-1).iloc[i]['High'] > df.iloc[i]['High']:
        return False
    elif df.shift(-2).iloc[i]['High'] > df.shift(-1).iloc[i]['High']:
        return False
    return True


def is_peak_loose(df, i):
    if (df.shift(2).iloc[i]['High'] < df.shift(1).iloc[i]['High']) and (
            df.shift(1).iloc[i]['High'] < df.iloc[i]['High']) and (
            df.shift(-1).iloc[i]['High'] < df.iloc[i]['High']):
        return True
    elif (df.shift(1).iloc[i]['High'] < df.iloc[i]['High']) and (
            df.shift(-1).iloc[i]['High'] < df.iloc[i]['High']) and (
            df.shift(-2).iloc[i]['High'] < df.shift(-1).iloc[i]['High']):
        return True
    return False


def is_tough_definitive(df, i):
    if df.shift(2).iloc[i]['Low'] < df.shift(1).iloc[i]['Low']:
        return False
    elif df.shift(1).iloc[i]['Low'] < df.iloc[i]['Low']:
        return False
    elif df.shift(-1).iloc[i]['Low'] < df.iloc[i]['Low']:
        return False
    elif df.shift(-2).iloc[i]['Low'] < df.shift(-1).iloc[i]['Low']:
        return False
    return True


def is_tough_loose(df, i):
    if (df.shift(2).iloc[i]['Low'] > df.shift(1).iloc[i]['Low']) and (
            df.shift(1).iloc[i]['Low'] > df.iloc[i]['Low']) and (
            df.shift(-1).iloc[i]['Low'] > df.iloc[i]['Low']):
        return True
    elif (df.shift(1).iloc[i]['Low'] > df.iloc[i]['Low']) and (
            df.shift(-1).iloc[i]['Low'] > df.iloc[i]['Low']) and (
            df.shift(-2).iloc[i]['Low'] > df.shift(-1).iloc[i]['Low']):
        return True
    return False
