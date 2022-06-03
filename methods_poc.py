import pandas as pd
import plotly.graph_objects as go
import glob
import json


method = "Method: \n\n1. Check for down trend, i.e. high & low prices of day x-1 are lower then the correspondant high & low" \
             "\nprices of day x-2. If passed - we have a down trend " \
             "\n2. Check for buyers-sellers balance i.e. open & close prices of day x are of max. difference of 0.5%. " \
             "\nIf passed - we have Doji paradigm." \
          "\n3. Check for up trend, i.e. high & low prices of day x+2 are higher then the correspondant high & low " \
          "\nprices of day x+1. If passed - we have an up trend" \
          "\n4. Check if there has been a positive change of 5% within 10 days period after the paradigm was identified. If so -" \
          "\nthe paradigm succeeded."

stocks_csv_paths = glob.glob(r"C:\Users\Avishay Wasse\Downloads\stocks" + "/*.csv")
print(stocks_csv_paths)

method_results = {}

for stock_csv in stocks_csv_paths:
    stock_df = pd.read_csv(stock_csv)

    # Doji
    # This will answer the question: Given the stock trend is Doji - did the
    # stock went up for at least 10% ?

    down_trend = 0
    doji_trend = 0
    up_trend_after_doji = 0
    five_percent_change = 0


    for i in range(len(stock_df)-15):
        j = i+2
        if (stock_df.iloc[j-1]['High'] < stock_df.iloc[j-2]['High']) and (stock_df.iloc[j-1]['Low'] < stock_df.iloc[j-2]['Low']):
            down_trend += 1
            if (stock_df.iloc[j]['Open'] - stock_df.iloc[j]['Open']*0.005) < stock_df.iloc[j]['Close'] < (stock_df.iloc[j]['Open'] + stock_df.iloc[j]['Open']*0.005):
                doji_trend += 1
                if (stock_df.iloc[j+1]['High'] < stock_df.iloc[j+2]['High']) and (stock_df.iloc[j+1]['Low'] < stock_df.iloc[j+2]['Low']):
                    up_trend_after_doji += 1
                    for k in range(len(stock_df)-15-j):
                        if ((stock_df.iloc[j+k+4]['Close'] - stock_df.iloc[j+3]['Open']) / stock_df.iloc[j+3]['Open'])*100 <= -5.0:
                            break
                        elif ((stock_df.iloc[j+k+4]['Close'] - stock_df.iloc[j+3]['Open']) / stock_df.iloc[j+3]['Open'])*100 >= 10.0:
                            five_percent_change += 1
                            break
                        elif k == 30:
                            break
                    # doji_era_df = pd.DataFrame.copy(stock_df[j-10:j+11])
                    # fig = go.Figure(data=[go.Candlestick(x=doji_era_df['Date'],
                    #                                      open=doji_era_df['Open'],
                    #                                      high=doji_era_df['High'],
                    #                                      low=doji_era_df['Low'],
                    #                                      close=doji_era_df['Close'])])
                    # fig.show()

    # print(down_trend)
    # print(doji_trend)
    # print(up_trend_after_doji)
    # print(five_percent_change)
    method_results[stock_csv] = (float(five_percent_change) / float(up_trend_after_doji)) * 100

values = method_results.values()
method_results["average_success_rate"] = sum(values)/len(values)
method_results["method"] = method
with open("method_results.json", 'w') as f:
    json.dump(method_results,f,indent=4)

# print("Method: \n\n1. Check for down trend, i.e. high & low prices of day x-1 are lower then the correspondant high & low "
#       "\nprices of day x-2. If passed - we have a down trend"
#       "\n2. Check for buyers-sellers balance i.e. open & close prices of day x are of max. difference of 0.5%. "
#       "\nIf passed - we have Doji paradigm."
#       "\n3. Check for up trend, i.e. high & low prices of day x+2 are higher then the correspondant high & low "
#       "\nprices of day x+1. If passed - we have an up trend"
#       "\n4. Check if there has been a positive change of 5% within 10 days period after the paradigm was identified. If so -"
#       "\nthe paradigm succeeded."
#       f"\n\nDown trend: {down_trend}\nDoji: {doji_trend}\nUp trend aftet Doji: {up_trend_after_doji}"
#       f"\nFive percent change: {five_percent_change}"
#       f"\n\nGiven there was an uptrend after Doji and we buy at Open price the next day, the success rate for 5% change is: "
#       f"{(float(five_percent_change)/float(up_trend_after_doji))*100}")

