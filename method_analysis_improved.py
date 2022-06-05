import json
import statistics
from methods.doji_method import doji_method
from get_all_snp_companies import get_all_snp_companies


success_per_ticker = {}
snp_tickers = get_all_snp_companies()['Symbol'].tolist()


sl_list = [2.0, 5.0, 10.0]
tp_list = [2.0, 3.0, 5.0, 10.0, 20.0, 30.0]

method_results = {}
method_detailed_results = {}

for tp in tp_list:
    method_results[tp] = {}
    method_detailed_results[tp] = {}
    for sl in sl_list:
        print(f"Exploring for take profit {tp}% and stop loss {sl}%")
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
            print(f"Exploring for {ticker}")
            try:
                result = doji_method(ticker, sl, tp)
                total_summary["Stock"].append(ticker)
                for key in total_summary.keys():
                    total_summary[key].append(result[key])
            except TypeError:
                pass

        method_detailed_results[tp][sl] = total_summary
        total_summary_avg = {}
        for key in total_summary:
            total_summary_avg[key] = [statistics.mean(total_summary[key])]

        method_results[tp][sl] = total_summary_avg

        with open("method_results.json", "w") as f:
            json.dump(method_results, f, indent=4)
        with open("method_detailed_results.json", "w") as f:
            json.dump(method_detailed_results, f, indent=4)
