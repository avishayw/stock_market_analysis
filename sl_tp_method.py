import random

def sl_tp_method(initial_cap, sl_percentage,tp_percentage,success_probability):
    cap = initial_cap
    trades = 0
    while not (cap > initial_cap*10 or cap < initial_cap*0.5):
        trades += 1
        result = random.randint(1,100)
        if result < success_probability:
            cap = cap*(1.0+(tp_percentage/100))
        elif result >= success_probability:
            cap = cap * (1.0-(sl_percentage/100))
        # print(cap)
    print(f"Initial: {initial_cap}\nFinal: {cap}")
    print(f"Total trades: {trades}")


if __name__=="__main__":
    sl_tp_method(100,5.0,10.0,44.0)
