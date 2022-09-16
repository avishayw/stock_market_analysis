import string

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


if __name__=="__main__":
    from stocksymbol import StockSymbol

    api_key = '32205225-709a-4d1a-bcb8-c728e175d8c3'
    ss = StockSymbol(api_key)

    us_symbols = ss.get_symbol_list(market='us', symbols_only=True)
    print(us_symbols)



