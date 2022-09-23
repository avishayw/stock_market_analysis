import string
import json
import pandas as pd


def get_all_snp_stocks():
    payload = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    return payload[0]['Symbol'].tolist()


def get_all_nasdaq_100_stocks():
    payload = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100#Components')
    return payload[4]['Ticker'].tolist()


def get_all_nyse_composite_stocks():
    alphabet = list(string.ascii_uppercase)
    pages = ['0%E2%80%939'] + alphabet
    stocks = []
    for page in pages:
        payload = pd.read_html(f'https://en.wikipedia.org/wiki/Companies_listed_on_the_New_York_Stock_Exchange_({page})')
        stocks = stocks + payload[1]['Symbol'].tolist()
    return stocks


def get_all_dow_jones_industrial_stocks():
    payload = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')
    return payload[1]['Symbol'].tolist()


def market_eras():
    return {'bull': ('2020-07-01', '2021-11-01'),
            'bear': ('2006-04-01', '2009-11-01'),
            'erratic': ('2017-12-01', '2020-05-01'),
            'combined': ('1997-01-01', '2003-01-01')}


def in_sample_tickers():
    with open(r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\utils\in_sample_symbols.json", 'r') as f:
        tickers = json.load(f)['tickers']
    return tickers


def out_sample_tickers():
    with open(r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\utils\out_sample_symbols.json", 'r') as f:
        tickers = json.load(f)['tickers']
    return tickers


if __name__=="__main__":
    from stocksymbol import StockSymbol
    import random
    import yfinance as yf
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import json

    api_key = '32205225-709a-4d1a-bcb8-c728e175d8c3'
    ss = StockSymbol(api_key)

    us_symbols = ss.get_symbol_list(market='us', symbols_only=True)
    snp_stocks = get_all_snp_stocks()
    nasdaq_stocks = get_all_nasdaq_100_stocks()
    all_stocks = list(set(us_symbols + snp_stocks + nasdaq_stocks))

    in_sample_stocks = in_sample_tickers()

    out_sample_stocks = []

    for stock in all_stocks:
        if stock in in_sample_stocks:
            continue
        df = yf.Ticker(stock).history(period='max', interval='1d')
        if not df.empty:
            print(stock)
            out_sample_stocks.append(stock)

    out_sample_stocks_dict = {'tickers': out_sample_stocks}

    with open('out_sample_symbols.json', 'w') as f:
        json.dump(out_sample_stocks_dict, f, indent=4)

