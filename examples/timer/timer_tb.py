#!/usr/bin/env python3

# Project: Verb
# Script: timer_tb.py
#   
# This script generates the I/O test vector files to be used with the 
# timer_tb.vhd testbench. It also states a coverage report to indicate the 
# robust of the tests.
#
# This script generate tests cycle-by-cycle for the HDL simulation.

from verb import context, coverage
from verb.coverage import *
from verb.model import *

class Timer:
    def __init__(self, sub_delays, base_delay):
        self.sub_delays = sub_delays
        self.base_delay = base_delay

        bits = len(self.sub_delays)

        self.sub_ticks = Signal(bits, endianness='little')
        self.base_tick = Signal(1)

        self.base_count = 0
        self.counts = [0] * bits
        pass

    def evaluate(self):
        self.base_count += 1

        if self.base_count < self.base_delay:
            self.base_tick.store(0)
            self.sub_ticks.store(0)
            return self
        
        # base count has reached the number of expected delays
        self.base_count = 0
        self.base_tick.store(1)

        # check if any subtick counts have reached their delay times
        for i, delay in enumerate(self.sub_delays):
            time = self.counts[i]
            if time == delay-1:
                self.sub_ticks[i] = 1
                self.counts[i] = 0
            else:
                self.sub_ticks[i] = 0
                self.counts[i] += 1
            pass
        return self
    pass

# collect generics and create model
SUB_DELAYS  = context.generic('SUB_DELAYS', type=[int])
BASE_DELAY  = context.generic('BASE_DELAY', type=int)

model = Timer(SUB_DELAYS, BASE_DELAY)

# Define coverage goals

# verify each tick is enabled at least 3 times
for i, tick in enumerate(SUB_DELAYS):
    CoverPoint('tick '+str(tick)+' targeted') \
        .goal(3) \
        .sink(model.sub_ticks) \
        .checker(lambda x, i=i: int(x[i]) == 1) \
        .apply()
    pass

# verify the common delay is enabled
CoverPoint("base tick targeted") \
    .goal(3) \
    .sink(model.base_tick) \
    .apply()

# Run the model!
with vectors('inputs.txt', 'i') as inputs, vectors('outputs.txt', 'o') as outputs:
    while coverage.met(10_000) == False:
        # write each transaction to the input file
        inputs.append(model)
        # compute expected values to send to simulation
        model.evaluate()
        # write each expected output of the transaction to the output file
        outputs.append(model)
        pass
    pass
