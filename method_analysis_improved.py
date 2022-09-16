import json
import statistics
import pandas as pd
from datetime import datetime
from methods.doji_method import doji_method
from utils.get_all_stocks import get_all_snp_stocks


run_start_time = datetime.utcnow().strftime("%Y-%m-%d")


print(f"{datetime.utcnow().strftime('%Y-%m-%d-%H:%M:%S')} Gathering all S&P500 tickers")
snp_tickers = get_all_snp_stocks()


sl_list = [2.0, 5.0, 10.0]
tp_list = [2.0, 3.0, 5.0, 10.0, 20.0, 30.0]

method_results = {}
method_detailed_results = {}
dates_results_per_stock = {}
no_trend_stocks = []

for tp in tp_list:
    method_results[tp] = {}
    method_detailed_results[tp] = {}
    dates_results_per_stock[tp] = {}
    for sl in sl_list:
        dates_results_per_stock[tp][sl] = {}
        print(f"{datetime.utcnow().strftime('%Y-%m-%d-%H:%M:%S')} Exploring for take profit {tp}% and stop loss {sl}%")
        total_summary = {"Stock": [],
            "Best case profits ratio": [],
                       "Worst case profits ratio": [],
                       "Best case losses ratio": [],
                       "Worst case losses ratio": [],
                       "Max. trade period in days": [],
                       "Min. trade period in days": [],
                       "Avg. trade period in days": [],
                       "Median trade period in days": [],
                       "Total exploration time": []}


        for ticker in snp_tickers:
            print(f"{datetime.utcnow().strftime('%Y-%m-%d-%H:%M:%S')} Exploring for {ticker}")
            try:
                result, dates = doji_method(ticker, sl, tp)
                if result is None:
                    no_trend_stocks.append(ticker)
                    no_trend_stocks = list(set(no_trend_stocks))
                    continue
                total_summary["Stock"].append(ticker)
                dates_results_per_stock[tp][sl][ticker] = dates
                for key in result.keys():
                    total_summary[key].append(result[key])

                method_detailed_results[tp][sl] = total_summary
                with open(f"method_detailed_results_{run_start_time}.json", "w") as f:
                    json.dump(method_detailed_results, f, indent=4)
                with open(f"dates_results_per_stock_{run_start_time}.json", "w") as f:
                    json.dump(dates_results_per_stock, f, indent=4)

            except TypeError as e:
                print(f"TypeError: {e}")
                pass

        total_summary_avg = {}
        for key in list(total_summary.keys())[1:]:
            total_summary_avg[key] = [statistics.mean(total_summary[key])]

        method_results[tp][sl] = total_summary_avg

        with open(f"method_results_{run_start_time}.json", "w") as f:
            json.dump(method_results, f, indent=4)

for tp in method_detailed_results.keys():
    for sl in method_detailed_results[tp].keys():
        results_df = pd.DataFrame(method_detailed_results[tp][sl])
        results_df.to_csv(f"results_tp_{tp}_sl_{sl}.csv")

print(*no_trend_stocks, sep='\n')
