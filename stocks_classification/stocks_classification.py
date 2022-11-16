"""
I define speculative stocks by the ratio between average volume of stocks trades out of total shares outstanding
"""
from utils.get_all_stocks import get_all_snp_stocks
import yfinance as yf
import pandas as pd


def speculative_stocks(tickers):
    tickers_ratio = {'ticker': [], 'ratio': []}
    for ticker in tickers:
        try:
            ticker_info = yf.Ticker(ticker).info
            shsouts = int(ticker_info['sharesOutstanding'])
            avgvol = int(ticker_info['averageVolume'])
            ratio = avgvol*100.0/shsouts
            print(ticker, ratio)
            tickers_ratio['ticker'].append(ticker)
            tickers_ratio['ratio'].append(ratio)
        except Exception as e:
            print(ticker, e)

    tickers_ratio_df = pd.DataFrame(tickers_ratio)
    tickers_ratio_df.sort_values(by=['ratio'], ascending=False, inplace=True)
    tickers_ratio_df.to_csv('stocks_volume_shares_outstanding_ratio.csv')


def institutional_support(tickers):
    tickers_ratio = {'ticker': [], 'inst_pct': []}
    for ticker in tickers:
        try:
            ticker_info = yf.Ticker(ticker).info
            inst_pct = float(ticker_info['heldPercentInstitutions'])*100.0
            print(ticker, inst_pct)
            tickers_ratio['ticker'].append(ticker)
            tickers_ratio['inst_pct'].append(inst_pct)
        except Exception as e:
            print(ticker, e)

    tickers_ratio_df = pd.DataFrame(tickers_ratio)
    tickers_ratio_df.sort_values(by=['inst_pct'], ascending=False, inplace=True)
    tickers_ratio_df.to_csv('stocks_institutional_percentage_held.csv')


def insider_holding(tickers):
    tickers_ratio = {'ticker': [], 'insd_pct': []}
    for ticker in tickers:
        try:
            ticker_info = yf.Ticker(ticker).info
            insr_pct = float(ticker_info['heldPercentInsiders']) * 100.0
            print(ticker, insr_pct)
            tickers_ratio['ticker'].append(ticker)
            tickers_ratio['insd_pct'].append(insr_pct)
        except Exception as e:
            print(ticker, e)

    tickers_ratio_df = pd.DataFrame(tickers_ratio)
    tickers_ratio_df.sort_values(by=['insd_pct'], ascending=False, inplace=True)
    tickers_ratio_df.to_csv('stocks_insider_percentage_held.csv')


def retail_holding(tickers):
    """
    Not accurate because big money (institutional/insider) can affect the volume much. Also, not accurate due to HFT
    """
    tickers_ratio = {'ticker': [], 'retail_pct': [], 'avg_vol_retail_shs_ratio': []}
    for ticker in tickers:
        try:
            ticker_info = yf.Ticker(ticker).info
            insd_pct = float(ticker_info['heldPercentInsiders']) * 100.0
            inst_pct = float(ticker_info['heldPercentInstitutions']) * 100.0
            avgvol = int(ticker_info['averageVolume'])
            shsouts = int(ticker_info['sharesOutstanding'])
            retail_pct = 100.0 - insd_pct - inst_pct
            avg_vol_retail_shs_ratio = avgvol/((retail_pct/100.0)*shsouts)
            print(ticker, retail_pct, avg_vol_retail_shs_ratio)
            tickers_ratio['ticker'].append(ticker)
            tickers_ratio['retail_pct'].append(retail_pct)
            tickers_ratio['avg_vol_retail_shs_ratio'].append(avg_vol_retail_shs_ratio)
        except Exception as e:
            print(ticker, e)

    tickers_ratio_df = pd.DataFrame(tickers_ratio)
    tickers_ratio_df.sort_values(by=['retail_pct'], ascending=False, inplace=True)
    tickers_ratio_df.to_csv('stocks_retail_percentage_held.csv')


if __name__ == '__main__':

    tickers = get_all_snp_stocks()
    retail_holding(tickers)
