
def calc_needed_success_ratio_for_profit(tp,sl):
    ratio = 1.05
    p = 1
    profit_multplier = 1.0 + tp/100.0
    loss_multiplier = 1.0 - sl/100.0
    if profit_multplier*loss_multiplier >= ratio:
        while profit_multplier*pow(loss_multiplier, p) >= ratio:
            p += 1
        return (1/(p+1))
    elif profit_multplier*loss_multiplier < ratio:
        while pow(profit_multplier,p)*loss_multiplier < ratio:
            p += 1
        return (p/(p+1))


if __name__=="__main__":
    print(calc_needed_success_ratio_for_profit(30.0, 5.0))
