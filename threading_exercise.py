from threading import Thread
import time

def my_function(num):
    num += 1
    start = num
    while num < start*1000000:
        num += 1
    print(num)
    return num


if __name__=="__main__":
    start_time = time.time()
    for i in [1,2]:
        my_function(i)
    print(time.time() - start_time)
    start_time = time.time()
    x1 = Thread(target=my_function(1))
    x2 = Thread(target=my_function(2))
    x1.start()
    x2.start()
    print(time.time() - start_time)
