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

import verb as vb
from verb.model import *
from verb.coverage import *

class BcdEncoder:

    def __init__(self, width: int, digits: int):
        """
        Create a new hardware model with the defined interface.
        """
        self.num_digits = digits
        self.width = width

        self.go = Signal(1, mode=Mode.IN, dist=[0.3, 0.7])
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
        vb.randomize(self)
        if explicit_go_val != None:
            self.go.set(explicit_go_val)

    def model(self):
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
        
        self.ovfl.set(0)
        # check if an overflow exists on conversion given digit constraint
        diff = self.num_digits - len(digits)
        if(diff < 0):
            self.ovfl.set(1)
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
            bin_digits += str(Signal(4, d))

        self.bcd.set(bin_digits)
        self.done.set(1)

    pass


def apply_coverage(real_mdl: BcdEncoder, fake_mdl: BcdEncoder):
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
        sink=(fake_mdl.bin, real_mdl.bin),
        checker=lambda x, y: int(x) != int(y),
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

    DIGITS = vb.load_param('DIGITS', dtype=int)
    LEN  = vb.load_param('LEN', dtype=int)
 
    real_mdl = BcdEncoder(width=LEN, digits=DIGITS)
    fake_mdl = BcdEncoder(width=LEN, digits=DIGITS)

    # Coverage Goals - specify coverage areas
    apply_coverage(real_mdl, fake_mdl)
    
    # Run - generate the test vectors from the model(s)
    with vb.open('inputs.txt') as vi, vb.open('outputs.txt') as vo:
        # initialize the values with defaults
        while vb.running(1_000):
            # get a new set of inputs to process
            real_mdl.setup(1)
            vi.push(real_mdl)

            # alter the input with random data while the computation is running
            for _ in range(0, real_mdl.fsm_cycle_delay):
                fake_mdl.setup()
                vi.push(fake_mdl)

            # compute the output
            real_mdl.model()
            vo.push(real_mdl)

            # place some random 'idle' time after a finished computation
            for _ in range(0, random.randint(0, 10)):
                fake_mdl.setup(0)
                vi.push(fake_mdl)
            pass
        pass

    pass


if __name__ == '__main__':
    main()
    pass
