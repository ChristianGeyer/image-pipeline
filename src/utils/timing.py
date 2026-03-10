import time
import numpy as np 

class RateMonitor:
    def __init__(self, 
                 T):
        self.T = T 
        self.t_start = 0
        self.n = 0
        self.t_curr = 0
        self.t_prev = 0
        self.dts = []
    
    def reset(self, t_curr=None):
        if t_curr is None:
            t_curr = time.perf_counter()
        self.t_curr = t_curr
        self.t_prev = t_curr
        self.t_start = t_curr
        self.n = 0
        self.dts = []
    
    def increment(self, t_curr=None):
        if t_curr is None:
            t_curr = time.perf_counter()
        self.t_curr = t_curr
        self.dts.append(self.t_curr - self.t_prev)
        self.t_prev = self.t_curr
        self.n += 1
        if self.t_curr - self.t_start >= self.T:
            rate = self.n / (self.t_curr - self.t_start)
            print(f"rate={rate}Hz, n={self.n}, t={self.t_curr-self.t_start}s, max(dt)={max(self.dts)}s, mean(dt)={np.mean(self.dts)}s.")
            self.reset(t_curr)