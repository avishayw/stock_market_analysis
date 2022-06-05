import random
import statistics

def sl_tp_method(initial_cap, final_cap_win, final_cap_loss, sl_percentage,tp_percentage,success_probability):
    cap = initial_cap
    trades = 0
    wins = 0
    losses = 0
    while not (cap > initial_cap*final_cap_win or cap < initial_cap*final_cap_loss):
        trades += 1
        result = random.randint(1,100)
        if result < success_probability:
            cap = cap*(1.0+(tp_percentage/100))
            wins += 1
        elif result >= success_probability:
            cap = cap * (1.0-(sl_percentage/100))
            losses += 1
        # print(cap)
    # print(f"Initial: {initial_cap} Final: {cap}")
    # print(f"Total trades: {trades}")
    # print(f"Wins: {wins} Losses: {losses}")
    return cap > initial_cap*final_cap_win, trades


if __name__=="__main__":
    import time
    start = time.time()
    num_loops = 100000
    wins = 0
    trades_list = []
    for i in range(num_loops):
        win, trades = sl_tp_method(100,10.0, 0.5, 2.0,5.0,40.0)
        if win:
            wins += 1
            trades_list.append(trades)
    print(float(wins)/float(num_loops), max(trades_list), statistics.mean(trades_list), statistics.median(trades_list))
    print(f"Time: {time.time() - start}")
