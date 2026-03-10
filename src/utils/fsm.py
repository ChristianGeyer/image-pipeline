import numpy as np
import time

class FSM:
    def __init__(self, initial_state):
        self.state = initial_state
        self.prev_state = -1
        self.tes = time.perf_counter()
        self.tis = 0.0

    def update(self, state, t_curr=None):
        if t_curr is None:
            t_curr = time.perf_counter()
        if state != self.state:
            # entered new state
            self.tes = t_curr # set tes
            self.tis = 0.0 # reset tis
        else:
            # same state
            self.tis = t_curr - self.tes # update tis
        self.prev_state = self.state
        self.state = state
    


            



