
def doji_method(stock_df, sl_percentage, tp_percentage, trade_max_days):
    """
    This function will return the **method success rate** with the given stock history, STOP-LOSS percentage,
    TAKE-PROFIT percentage and the maximum amount of days for the trade

    Doji Method:

    1. Check for down trend, i.e. high & low prices of day x-1 are lower then the correspondent high & low prices
    of day x-2. If passed - we have a down trend
    2. Check for buyers-sellers balance i.e. open & close prices of day x are of max. difference of 0.5%. If passed
    - we have Doji paradigm."
    3. Check for up trend, i.e. high & low prices of day x+2 are higher then the correspondent high & low prices
    of day x+1. If passed - we have an up trend"
    4. Check if there has been a positive change of 5% within 10 days period after the paradigm was identified.
    If so the paradigm succeeded.

    :param stock_df: DataFrame of stock daily history prices
    :param sl_percentage: float - POSITIVE percentage. Example: 5.0
    :param tp_percentage: float - POSITIVE percentage. Example: 10.0
    :param trade_max_days: int - Example: 30
    :return: float - Method success rate
    """

    down_trend = 0.0
    doji_trend = 0.0
    up_trend_after_doji = 0.0
    profitable_change = 0.0
    for i in range(len(stock_df)-trade_max_days-3):
        j = i+2
        if (stock_df.iloc[j-1]['High'] < stock_df.iloc[j-2]['High']) and (stock_df.iloc[j-1]['Low'] < stock_df.iloc[j-2]['Low']):
            down_trend += 1
            if (stock_df.iloc[j]['Open'] - stock_df.iloc[j]['Open']*0.005) < stock_df.iloc[j]['Close'] < (stock_df.iloc[j]['Open'] + stock_df.iloc[j]['Open']*0.005):
                doji_trend += 1
                if (stock_df.iloc[j+1]['High'] < stock_df.iloc[j+2]['High']) and (stock_df.iloc[j+1]['Low'] < stock_df.iloc[j+2]['Low']):
                    up_trend_after_doji += 1
                    for k in range(len(stock_df)-trade_max_days-3-j):
                        if not stock_df.iloc[j+3]['Open'] == 0.0:
                            if ((stock_df.iloc[j+k+4]['Close'] - stock_df.iloc[j+3]['Open']) / stock_df.iloc[j+3]['Open'])*100 <= sl_percentage*-1.0:
                                break
                            elif ((stock_df.iloc[j+k+4]['Close'] - stock_df.iloc[j+3]['Open']) / stock_df.iloc[j+3]['Open'])*100 >= tp_percentage:
                                profitable_change += 1
                                break
                        elif k == trade_max_days:
                            break
    if not up_trend_after_doji==0.0:
        return profitable_change/up_trend_after_doji
    else:
        return None


if __name__=="__main__":
    ticker = 'FB'
