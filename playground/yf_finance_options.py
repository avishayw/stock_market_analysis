import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.download_stock_csvs import download_stock_day

# Getting all SPY expiration dates
ticker = 'SPY'
stock = yf.Ticker(ticker)
expiration_dates = stock.options

# Filtering the expiration dates to be 1 month to 3 months from now
filtered_expiration_dates = []
now = datetime.now()
one_month = now + relativedelta(months=1)
three_months = now + relativedelta(months=3)
for date in expiration_dates:
    if one_month <= datetime.strptime(date, '%Y-%m-%d') <= three_months:
        filtered_expiration_dates.append(date)


# Taking the first date for practice
expiration_date = filtered_expiration_dates[0]
print(f'Expiration date: {expiration_date}')

# Getting the calls and puts for the expiration date
options = stock.option_chain(date=expiration_date)
calls_df = options.calls
puts_df = options.puts

# # Choosing the call and put which have the closest strike price to stock current price
# closest_call_df = calls_df.loc[calls_df['inTheMoney']].iloc[-1]
# closest_put_df = puts_df.loc[puts_df['inTheMoney']].iloc[0]
# print('Closest Call:')
# print(closest_call_df)
# print('Closest Put:')
# print(closest_put_df)

# Choosing the call and put which have the furthers strike price to stock current price
furthest_call_df = calls_df.loc[calls_df['inTheMoney']].iloc[0]
furthest_put_df = puts_df.loc[puts_df['inTheMoney']].iloc[-1]
print('Furthest Call:')
print(furthest_call_df)
print('Furthest Put:')
print(furthest_put_df)

# Assumption: Higher option price might result in higher implied volatility
# I'd like to check if increase in option price resulted in higher stock price
# I'll start with the call option

# Getting the option historical price
option_ticker = furthest_call_df['contractSymbol']
option_df = yf.Ticker(option_ticker).history(period='1mo', interval='1d')
option_df.reset_index(inplace=True)
print(option_df.head())

# Getting the stock historical price
stock_df = stock.history(period='1mo', interval='1d')
stock_df.reset_index(inplace=True)
print(stock_df.head())

# Combining both closing prices to one df
stock_dates = stock_df['Date'].tolist()
stock_close = stock_df['Close'].tolist()
option_dates = option_df['Date'].tolist()
option_close = option_df['Close'].tolist()
combined_dict = {}

if stock_dates[0] == option_dates[0]:
    if len(stock_dates) == len(option_dates):
        combined_dict['Date'] = stock_dates
        combined_dict['stock_close'] = stock_close
        combined_dict['option_close'] = option_close
        combined_df = pd.DataFrame(combined_dict)
    else:
        print('different lengths')
        exit()
else:
    print('different starting dates')
    exit()

combined_df['stock_change%'] = ((combined_df['stock_close'] - combined_df.shift(1)['stock_close'])/combined_df.shift(1)['stock_close'])*100.0
combined_df['option_change%'] = ((combined_df['option_close'] - combined_df.shift(1)['option_close'])/combined_df.shift(1)['option_close'])*100.0
print(combined_df)



# ticker = 'AAPL220828C00100000'
# option = yf.Ticker(ticker)
# print(option.history(interval='1d'))

# Let us ask a question - how much does the purchase of an option will immediately benefit in profit?
# i.e. Get the stock last closing price > Check call option prices history > For every price:
# multiply by 100 > multiply (stock last closing price - strike price) by 100 > calculate the diff/option_price ratio

# stock_price = yf.Ticker('AAPL').history(period='1d').iloc[0]['Close']
# option = yf.Ticker('AAPL240621C00050000')
# strike = 50.0
# stock_strike_profit = (stock_price - strike)*100.0
# option_price_history = option.history(interval='1d')
# option_price_history['profit_option_ratio'] = np.nan
# option_price_history.reset_index(inplace=True)
#
# for i in range(len(option_price_history)):
#     option_close = option_price_history.iloc[i]['Close']*100.0
#     # print(stock_strike_profit/option_close)
#     option_price_history.loc[i, 'profit_option_ratio'] = stock_strike_profit/option_close
#
# pd.set_option("display.max_rows", None, "display.max_columns", None)
# print(option_price_history[['Date', 'profit_option_ratio']])
