#!/usr/bin/env python3

# Generates the I/O test vector files to be used with the 
# bcd_enc_tb.vhd testbench. It also produces a coverage report to indicate the 
# robust of the tests.

import random
from verb import context, coverage
from verb.model import *
from verb.coverage import *

class BcdEncoder:

    def __init__(self, width: int, digits: int):
        '''
        Create a new hardware model with the defined interface.
        '''
        self.num_digits = digits
        self.width = width

        self.go = Signal(1, mode=Mode.IN, distribution=[0.3, 0.7])
        self.bin = Signal(width, mode=Mode.IN)

        self.bcd = Signal(4*digits, mode=Mode.OUT)
        self.ovfl = Signal(1, mode=Mode.OUT)
        self.done = Signal(1, mode=Mode.OUT)

        # LEN | CYCLES
        # --- | ----------
        #  4  | 7  = 4 + 4 - 1 
        #  5  | 9  = 5 + 5 - 1
        #  6  | 11 = 6 + 6 - 1 
        self.fsm_cycle_delay = width+width-1
        pass

    def eval(self):
        '''
        Model the functional behavior of the design unit.
        '''
        # separate each digit
        digits = []
        word = int(self.bin)
        while word >= 10:
            digits.insert(0, (word % 10))
            word = int(word/10)
        digits.insert(0, word)
        
        self.ovfl.assign(0)
        # check if an overflow exists on conversion given digit constraint
        diff = self.num_digits - len(digits)
        if(diff < 0):
            self.ovfl.assign(1)
            # trim off left-most digits
            digits = digits[abs(diff):]
        # pad left-most digit positions with 0's
        elif(diff > 0):
            for _ in range(diff):
                digits.insert(0, 0)
            pass

        # write each digit to output file
        bin_digits: str = ''
        for d in digits:
            bin_digits += str(Signal(4).assign(d))

        self.bcd.assign(bin_digits)
        self.done.assign(1)
        return self

    pass


def cover(real_mdl, fake_mdl):
    """
    Specify coverage areas.
    """
    CoverRange("input span") \
            .span(real_mdl.bin.span()) \
            .target(real_mdl.bin) \
            .apply()

    CoverPoint("overflow enabled") \
        .goal(10) \
        .bypass(real_mdl.bin.max() < (10**real_mdl.num_digits)) \
        .target(real_mdl.ovfl) \
        .checker(lambda x: int(x) == 1) \
        .apply()

    CoverGroup("overflow variants") \
        .bins([0, 1]) \
        .bypass(real_mdl.bin.max() < (10**real_mdl.num_digits)) \
        .target(real_mdl.ovfl) \
        .apply()

    CoverGroup("extreme inputs") \
        .bins([real_mdl.bin.min(), real_mdl.bin.max()]) \
        .target(real_mdl.bin) \
        .apply()

    cp_bin_while_active = CoverPoint("input changes while active") \
        .goal(100) \
        .apply()

    cp_go_while_active = CoverPoint("go while active") \
        .goal(100) \
        .target(fake_mdl.go) \
        .checker(lambda x: int(x) == 1) \
        .apply()
    
    return cp_bin_while_active


def main():
    # Setup - collect parameters and create models

    DIGITS = context.generic('DIGITS', type=int)
    LEN  = context.generic('LEN', type=int)

    real_mdl = BcdEncoder(width=LEN, digits=DIGITS)
    fake_mdl = BcdEncoder(width=LEN, digits=DIGITS)

    # Coverage Goals - specify coverage areas
    cp_bin_while_active = cover(real_mdl, fake_mdl)

    # Run - generate the test vectors from the model(s)
    with vectors('inputs.txt', 'i') as inputs, vectors('outputs.txt', 'o') as outputs:
        # initialize the values with defaults
        while coverage.met(1_000) == False:
            # get a new set of inputs to process
            randomize(real_mdl)
            real_mdl.go.assign(1)
            inputs.push(real_mdl)

            # alter the input while the computation is running
            for _ in range(0, real_mdl.fsm_cycle_delay):
                randomize(fake_mdl)
                cp_bin_while_active.check(int(fake_mdl.bin) != int(real_mdl.bin))
                inputs.push(fake_mdl)

            # compute the output
            real_mdl.eval()
            outputs.push(real_mdl)

            # place some random 'idle' time after a finished computation
            for _ in range(0, random.randint(0, 10)):
                randomize(fake_mdl)
                fake_mdl.go.assign(0)
                inputs.push(fake_mdl)
            pass
        pass

    pass


if __name__ == '__main__':
    main()
    pass
