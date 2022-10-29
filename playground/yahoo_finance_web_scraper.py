import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Input
symbol = 'GME'

# Set up scraper
url = ("http://finviz.com/quote.ashx?t=" + symbol.lower())
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
html = soup(webpage, "html.parser")
# print(html)
data = pd.read_html(str(html))

# for i in range(len(data)):
#     print('\n\n', i, '\n\n')
#     print(data[i])
data_dict = {}
key_statistics = data[4]

for i in range(0, len(key_statistics.columns.tolist()), 2):
    keys = key_statistics[i].tolist()
    values = key_statistics[i+1].tolist()
    for j in range(len(key_statistics)):
        key = keys[j]
        value = values[j]
        try:
            value = float(value)
            data_dict.update({key: value})
        except:
            data_dict.update({key: value})

avg_volume = data_dict['Avg Volume']

if avg_volume[-1] == 'M':
    avg_volume = float(avg_volume.replace('M', ''))*1000000.0
elif avg_volume[-1] == 'K':
    avg_volume = float(avg_volume.replace('K', '')) * 1000.0
elif avg_volume[-1] == 'B':
    avg_volume = float(avg_volume.replace('B', '')) * 1000000000.0

shares_outstanding = data_dict['Shs Outstand']

if shares_outstanding[-1] == 'M':
    shares_outstanding = float(shares_outstanding.replace('M', ''))*1000000.0
elif shares_outstanding[-1] == 'K':
    shares_outstanding = float(shares_outstanding.replace('K', '')) * 1000.0
elif shares_outstanding[-1] == 'B':
    shares_outstanding = float(shares_outstanding.replace('B', '')) * 1000000000.0

print((avg_volume/shares_outstanding)*100.0)