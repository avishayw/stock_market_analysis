from methods.doji_method import doji_method
import time

start = time.time()
print(doji_method("AAPL", 5.0, 3.0, 5))
print(time.time() - start)
