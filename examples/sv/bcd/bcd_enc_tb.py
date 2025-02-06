#!/usr/bin/env python3

# Generates the I/O test vector files to be used with the 
# bcd_enc_tb.vhd testbench. It also produces a coverage report to indicate the 
# robust of the tests.
#
# The following table highlights the relationship between the length of the
# input binary word and the number of cycles it takes to reach a result:
#       LEN | CYCLES
#       --- | ----------
#        4  | 7  = 4 + 4 - 1 
#        5  | 9  = 5 + 5 - 1
#        6  | 11 = 6 + 6 - 1 

import random

import verb
from verb.model import *
from verb.coverage import *

class BcdEncoder:

    def __init__(self, width: int, digits: int):
        """
        Create a new hardware model with the defined interface.
        """
        self.num_digits = digits
        self.width = width

        self.go = Signal(1, mode=Mode.IN, distribution=[0.3, 0.7])
        self.bin = Signal(width, mode=Mode.IN)

        self.bcd = Signal(4*digits, mode=Mode.OUT)
        self.ovfl = Signal(1, mode=Mode.OUT)
        self.done = Signal(1, mode=Mode.OUT)

        # Store the number of cycles it takes to compute a result
        self.fsm_cycle_delay = width+width-1
        pass

    def setup(self, explicit_go_val: int=None):
        """
        Assign a new set of inputs for the model to compute.
        """
        randomize(self)
        if explicit_go_val != None:
            self.go.assign(explicit_go_val)

    def exec(self):
        """
        Model the functional behavior of the design unit.
        """
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


def apply_coverage(real_mdl, fake_mdl):
    """
    Specify coverage areas.
    """
    CoverRange(
        name="input span",
        span=real_mdl.bin.span(),
        target=real_mdl.bin,
    )

    CoverPoint(
        name="overflow enabled",
        goal=10,
        bypass=real_mdl.bin.max() < (10**real_mdl.num_digits),
        target=real_mdl.ovfl,
        checker=lambda x: int(x) == 1,
    )

    CoverGroup(
        name="overflow variants",
        bins=[0, 1],
        bypass=real_mdl.bin.max() < (10**real_mdl.num_digits),
        target=real_mdl.ovfl,
    )

    CoverGroup(
        name="extreme inputs",
        bins=[real_mdl.bin.min(), real_mdl.bin.max()],
        target=real_mdl.bin
    )

    CoverPoint(
        name="input changes while active",
        goal=100
    )

    CoverPoint(
        name="go while active",
        goal=100,
        target=fake_mdl.go,
        checker=lambda x: int(x) == 1,
    )


def main():
    # Setup - collect parameters and create models

    DIGITS = verb.load_param('DIGITS', type=int)
    LEN  = verb.load_param('LEN', type=int)

    real_mdl = BcdEncoder(width=LEN, digits=DIGITS)
    fake_mdl = BcdEncoder(width=LEN, digits=DIGITS)

    # Coverage Goals - specify coverage areas
    apply_coverage(real_mdl, fake_mdl)
    
    # Run - generate the test vectors from the model(s)
    with vectors('inputs.txt') as inputs, vectors('outputs.txt') as outputs:
        # initialize the values with defaults
        while verb.running(1_000):
            # get a new set of inputs to process
            real_mdl.setup(1)
            inputs.push(real_mdl)

            # alter the input with random data while the computation is running
            for _ in range(0, real_mdl.fsm_cycle_delay):
                fake_mdl.setup()
                Coverage["input changes while active"].check(int(fake_mdl.bin) != int(real_mdl.bin))
                inputs.push(fake_mdl)

            # compute the output
            real_mdl.exec()
            outputs.push(real_mdl)

            # place some random 'idle' time after a finished computation
            for _ in range(0, random.randint(0, 10)):
                fake_mdl.setup(0)
                inputs.push(fake_mdl)
            pass
        pass

    pass


if __name__ == '__main__':
    main()
    pass
