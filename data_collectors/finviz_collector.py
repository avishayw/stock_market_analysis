import stat
import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
from utils.stocks_by_exchange import *
from datetime import datetime
import urllib
import random
from cloud_utils.bucket import download_from_bucket, upload_to_bucket, file_exist_in_bucket
import os
import pytz


def str_to_float(var):
    if isinstance(var, float):
        return var
    if not isinstance(var, str):
        return None
    if var[-1] == 'M':
        var = float(var.replace('M', '')) * 1000000.0
    elif var[-1] == 'K':
        var = float(var.replace('K', '')) * 1000.0
    elif var[-1] == 'B':
        var = float(var.replace('B', '')) * 1000000000.0
    elif var[-1] == '%':
        var = float(var.replace('%', ''))
    else:
        try:
            var = float(var)
        except ValueError:
            return None
    return var


def ticker_finviz_statistics(ticker):
    url = ("http://finviz.com/quote.ashx?t=" + ticker.lower())
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    html = soup(webpage, "html.parser")
    data = pd.read_html(str(html))
    statistics = data[4]
    keys_to_keep = ['Market Cap',
                    'Income',
                    'Sales',
                    'Book/sh',
                    'Cash/sh',
                    'Dividend',
                    'Dividend %',
                    'P/E',
                    'Forward P/E',
                    'PEG',
                    'P/S',
                    'P/B',
                    'P/C',
                    'Debt/Eq',
                    'LT Debt/Eq',
                    'EPS (ttm)',
                    'EPS next Y',
                    'EPS next Q',
                    'EPS this Y',
                    'EPS next Y',
                    'EPS past 5Y',
                    'Sales Q/Q',
                    'EPS Q/Q',
                    'Insider Own',
                    'Insider Trans',
                    'Inst Own',
                    'Inst Trans',
                    'ROA',
                    'ROE',
                    'ROI',
                    'Gross Margin',
                    'Oper. Margin',
                    'Profit Margin',
                    'Shs Outstand',
                    'Shs Float',
                    'Short Float',
                    'Short Ratio',
                    'Target Price',
                    'Avg Volume',
                    'Price']
    data_dict = {'time': int(datetime.now().timestamp()), 'symbol': ticker}
    for i in range(0, len(statistics.columns.tolist()), 2):
        keys = statistics[i].tolist()
        values = statistics[i + 1].tolist()
        for j in range(len(statistics)):
            key = keys[j]
            if not key in keys_to_keep:
                continue
            key = key.lower().replace('/', '_').replace(' ', '').replace('%', '_pct').replace('(', '_').replace(')', '_').replace('.', '_')
            value = values[j]
            if value == '-':
                data_dict.update({key: None})
            else:
                value_float = str_to_float(value)
                if value_float is not None:
                    data_dict.update({key: value_float})
                else:
                    data_dict.update({key: value})
    return data_dict


def tickers_finviz_data_list(tickers):
    dict_list = []
    for ticker in tickers:
        try:
            dict_list.append(ticker_finviz_statistics(ticker))
        except urllib.error.HTTPError as e:
            print(ticker, e)
            continue
    return dict_list


if __name__ == '__main__':

    def now():
        return datetime.now().astimezone(pytz.timezone('Asia/Jerusalem'))


    last_date = ''
    while True:
        today = datetime.now().astimezone(pytz.timezone('Asia/Jerusalem'))
        if today.strftime('%Y-%m-%d') != last_date:
            print(f'{now()} Started')
            last_date = today.strftime('%Y-%m-%d')
            finviz_file = 'finviz_data.parquet'
            if file_exist_in_bucket(finviz_file):
                download_from_bucket(finviz_file, finviz_file)
                print(f'{now()} Downloaded finviz file from bucket')
                df = pd.read_parquet(finviz_file)
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                all_dicts = df.to_dict('records')
                tickers = NASDAQ_COMMON_STOCKS + AMEX_COMMON_STOCKS + NYSE_COMMON_STOCKS
                tickers = random.choices(tickers, k=10)
                all_dicts = all_dicts + tickers_finviz_data_list(tickers)
                pd.DataFrame(all_dicts).to_parquet(finviz_file)
                upload_to_bucket(finviz_file, finviz_file)
                print(f'{now()} Uploaded finviz file to bucket')
            else:
                tickers = NASDAQ_COMMON_STOCKS + AMEX_COMMON_STOCKS + NYSE_COMMON_STOCKS
                tickers = random.choices(tickers, k=10)
                pd.DataFrame(tickers_finviz_data_list(tickers)).to_parquet(finviz_file)
                upload_to_bucket(finviz_file, finviz_file)
                print(f'{now()} Uploaded finviz file to bucket')
