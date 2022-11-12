"""
Using the method for measuring movements (playground/measuring_movements_with_er.py):
1. Measure weekly movement using efficiency ratio of minimum 0.7.
2. If 2 weeks completed with the same movement, and using the movement's weekly prices - measure the weekly change
    by creating a straight line. Compare the weekly change to weekly ATR of period TBD (optimization parameter?).
3. Given the weekly change given by the movement implies clear trend (HOW TO MEASURE?), up or down, enter a position the
    same direction of the movement.
4. Exit the position once the movement is finished (the week's weekend in which the movement efficiency ratio becomes
    noisy, i.e. less than 0.7.
"""