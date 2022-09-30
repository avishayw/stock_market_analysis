import yfinance as yf
from datetime import datetime
import numpy as np
import pandas as pd


class Portfolio:

    def __init__(self, initial_capital, symbol_list, start_datetime, end_datetime):
        self.cap = initial_capital
        self.symbols = symbol_list
        self.datetime = start_datetime
        self.end_portfolio_datetime = end_datetime
        self.orders = []
        self.positions_id_counter = 0
        self.p_and_l = 0.0
        self.p_and_l_pct = 0.0

    def place_order(self, symbol: str, qty: int, order_type: str, slippage_pct=0.5):
        # Constraints
        if not (order_type == 'long' or 'short'):
            print("Invalid order type. Order wasn't placed.")
            return None

        df = yf.Ticker(symbol).history(interval='1d', start=self.datetime.strftime('%Y-%m-%d'))
        df['Datetime'] = pd.to_datetime(df['Date'])
        df = df.loc[df['Datetime'] == self.datetime]
        if df.empty:
            print(f"No data from date {self.datetime}")
            return None
        price = df.iloc[0]['Close']

        # Accounting for slippage
        if order_type == 'long':
            price = price * (1 - (slippage_pct / 100.0))
        else:
            price = price * (1 + (slippage_pct / 100.0))
        order_dict = {'symbol': symbol,
                      'type': order_type,
                      'qty': qty,
                      'avg_price': price}
        self.orders.append(order_dict)
        print('Placed new order', order_dict)


if __name__=='__main__':
    import pandas as pd
    import numpy as np
    import yfinance as yf

    trades_csv_path = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\ma_roc_er_trading_v5_all_trades.csv"
    df_backup = pd.read_csv(trades_csv_path)
    df_backup.sort_values(by='enter_date', inplace=True)
    spy_df_backup = yf.Ticker('SPY').history(period='max', interval='1d').reset_index()
    spy_df_backup['Datetime'] = pd.to_datetime(spy_df_backup['Date'])
    year = 1995
    while year < 2023:
        start_datetime = datetime(year, 1, 1, 0, 0, 0)
        end_datetime = datetime(year+1, 1, 1, 0, 0, 0)
        df = df_backup.copy()
        df['enter_datetime'] = pd.to_datetime(df['enter_date'])
        df['exit_datetime'] = pd.to_datetime(df['exit_date'])
        df = df.loc[(df['enter_datetime'] >= start_datetime) & (df['enter_datetime'] <= end_datetime)]

        spy_df = spy_df_backup.loc[(spy_df_backup['Datetime'] >= start_datetime) & (spy_df_backup['Datetime'] <= end_datetime)].copy()
        spy_return = (spy_df.iloc[-1]['Close']/spy_df.iloc[0]['Close'])

        initial_cap = 2000
        cash = initial_cap
        value = initial_cap
        monthly_deposit = 0
        # trade_size_cap_ratio = 0.05
        trade_size_cap_ratio = 0.05*(initial_cap/value)
        trade_size = trade_size_cap_ratio*value
        trades = []
        actual_trades = 0

        current_date = df.iloc[0]['enter_datetime']
        for i in range(len(df)):
            # print(value, cash, round(trade_size_cap_ratio, 3))
            if trades:
                if df.iloc[i]['enter_datetime'] > trades[-1][0]:
                    trades_to_pop = 0
                    for trade in trades:
                        if df.iloc[i]['enter_datetime'] > trade[0]:
                            trades_to_pop += 1
                    for p in range(trades_to_pop):
                        completed_trade = trades.pop()
                        cash = cash + completed_trade[2]
                        value = value + completed_trade[2] - completed_trade[1]
                        trade_size_cap_ratio = 0.05*(initial_cap/value)
                        trade_size = trade_size_cap_ratio * value
            if trade_size >= df.iloc[i]['enter_price'] and df.iloc[i]['exit_price'] > 0 and trade_size < cash and (cash - trade_size) > value*0.05:
                actual_trades += 1
                qty = int(np.floor((trade_size_cap_ratio*value)/df.iloc[i]['enter_price']))
                if qty > 100:
                    commission = 0.01*qty
                else:
                    commission = 1
                cash = cash - df.iloc[i]['enter_price']*qty - commission
                trades.append((df.iloc[i]['exit_datetime'], df.iloc[i]['enter_price']*qty*1.005, df.iloc[i]['exit_price']*qty*0.995))
                trades.sort(key=lambda tup: tup[0], reverse=True)
            if (df.iloc[i]['enter_datetime'] - current_date).days > 30:
                cash += monthly_deposit
                value += monthly_deposit

        # print(value, cash)
        # print(actual_trades, actual_trades/len(df))
        print(f'Year: {year}, Return: {value/initial_cap}, SPY Return: {spy_return}, Beat SPY: {value/initial_cap > spy_return}')
        year += 1


