import pandas as pd
import numpy as np


def breakouts_signals(df, bull_signal=1.2, bear_signal=0.8):
    start_idx = df.index[0]
    df['bull_signal'] = np.nan
    df['bear_signal'] = np.nan

    idx = 2
    bull_high = 0
    bear_low = 0
    bull_run = False
    bear_run = False
    potential_breakout = False
    while idx < len(df):
        if potential_breakout:
            if df.iloc[idx]['Close'] > max*1.1:
                bull_run = True
                df.loc[start_idx + idx, 'bull_signal'] = True
            else:
                if df[:idx-1]['High'].max() == max:
                    pass
        max = df[:idx-1]['High'].max()

