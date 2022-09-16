from plotting.candlestick_chart import candlestick_chart_fig, add_markers_to_candlestick_chart
import pandas as pd
import numpy as np
from utils.download_stock_csvs import download_stock_day
from utils.get_all_stocks import get_all_snp_stocks
from locators.peaks_and_toughs import is_peak_loose, is_tough_loose, is_peak_definitive, is_tough_definitive
import plotly.graph_objects as go
from utils.paths import save_under_results_path

stocks_peaks_and_toughs = []

tickers = get_all_snp_stocks()

for ticker in tickers:
    try:
        df = pd.read_csv(download_stock_day(ticker))[-1008:]
    except ValueError:
        continue
    print(ticker)
    for i in range(len(df)):
        if is_peak_definitive(df, i):
            peak_dict = {'ticker': ticker, 'type': 'definitive_peak', 'date': df.iloc[i]['Date'], 'price': df.iloc[i]['High']}
            print(peak_dict)
            stocks_peaks_and_toughs.append(peak_dict)

        elif is_peak_loose(df, i):
            peak_dict = {'ticker': ticker, 'type': 'loose_peak', 'date': df.iloc[i]['Date'],
                         'price': df.iloc[i]['High']}
            print(peak_dict)
            stocks_peaks_and_toughs.append(peak_dict)
        if is_tough_definitive(df, i):
            tough_dict = {'ticker': ticker, 'type': 'definitive_tough', 'date': df.iloc[i]['Date'], 'price': df.iloc[i]['Low']}
            print(tough_dict)
            stocks_peaks_and_toughs.append(tough_dict)
        elif is_tough_loose(df, i):
            tough_dict = {'ticker': ticker, 'type': 'loose_tough', 'date': df.iloc[i]['Date'],
                          'price': df.iloc[i]['Low']}
            print(tough_dict)
            stocks_peaks_and_toughs.append(tough_dict)
    pd.DataFrame(stocks_peaks_and_toughs).to_csv(save_under_results_path('peaks_and_toughs_snp_stocks.csv'))


