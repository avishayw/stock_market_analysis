from ta.volume import VolumePriceTrendIndicator


def vpt(df):
    df[f'VPT'] = VolumePriceTrendIndicator(df['Close'], df['Volume']).volume_price_trend()
    return df