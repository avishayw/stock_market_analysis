# Find all the inequality relationships between different R%
# I want to derive from it what's possible and then think what it means on what the market is thinking
from indicators.my_indicators import williams_r_all
from indicators.momentum_indicators import rate_of_change
import yfinance as yf
import json


ticker = 'BA'
df = yf.Ticker(ticker).history(period='max', interval='1d')[-1008:]

# periods = list(range(2, 20, 3))
periods = [14, 21, 63]

relationships = {}  # List of strings, each string is inequality
williams_list = []

for period in periods:
    df = williams_r_all(df, period)
    williams_list = williams_list + [f'Williams_R%_High_{period}', f'Williams_R%_Close_{period}',
                                     f'Williams_R%_Open_{period}', f'Williams_R%_Median_{period}',
                                     f'Williams_R%_Low_{period}']

sources = ['High', 'Close', 'Open', 'Low', 'Median']

for row in range(len(df)):
    change = ((df.shift(-1).iloc[row]['Close'] - df.shift(-1).iloc[row]['Open'])/df.shift(-1).iloc[row]['Open'])*100.0
    if change > 0:
        change = 'positive'
    else:
        change = 'negative'
    for src in sources:
        if src not in relationships.keys():
            relationships[src] = []
        williams_dict = {}
        for william in williams_list:
            if src in william:
                try:
                    williams_dict[william] = df.iloc[row][william]
                except IndexError as e:
                    print(e)
                    print(i)
                    print(len(df))
                    exit()
        # Sorting
        sorted_williams_items = list({k: v for k, v in sorted(williams_dict.items(), key=lambda item: item[1])}.items())
        # Checking that all periods are included
        if len(sorted_williams_items) != len(periods):
            print('different len')
            exit()
        inequality_string = f'{change}: '
        for i in range(len(sorted_williams_items)):
            if inequality_string == f'{change}: ':
                inequality_string = inequality_string + sorted_williams_items[i][0]
            else:
                if sorted_williams_items[i][1] > sorted_williams_items[i-1][1]:
                    inequality_string = inequality_string + ' < ' + sorted_williams_items[i][0]
                elif sorted_williams_items[i][1] < sorted_williams_items[i-1][1]:
                    inequality_string = inequality_string + ' > ' + sorted_williams_items[i][0]
                else:
                    inequality_string = inequality_string + ' = ' + sorted_williams_items[i][0]
        relationships[src] = list(set(relationships[src] + [inequality_string]))

with open('williams_r_relationships.json', 'w') as f:
    json.dump(relationships, f, indent=4)
