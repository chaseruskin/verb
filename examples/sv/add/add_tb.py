#!/usr/bin/env python3

# Project: Verb
# Model: add
#
# This script generates the I/O test vector files to be used with the 
# add_tb.vhd testbench.
#
# Generates a coverage report as well to indicate the robust of the test.

import random

import verb as vb
from verb.model import *
from verb.coverage import *

# Define the functional model
class Add:

    def __init__(self, width: int):
        """
        Create a new design unit model.
        """
        # parameters
        self.width = width
        # inputs
        self.in0 = Signal(
            width, 
            dist=Distribution(
                space=[0, vb.pow2m1(width), range(1, vb.pow2m1(width))], 
                weights=[0.1, 0.1, 0.8]
            )
        )
        self.in1 = Signal(
            width, 
            dist=Distribution(
                space=[0, vb.pow2m1(width), range(1, vb.pow2m1(width))], 
                weights=[0.1, 0.1, 0.8]
            )
        )
        self.cin = Signal()
        # outputs
        self.sum = Signal(width)
        self.cout = Signal()
        pass

    def setup(self):
        """
        Determine the next set of inputs.
        """
        vb.randomize(self)

    def compute(self):
        """
        Model the functional behavior of the design unit.
        """
        temp = Signal(self.width+1)
        temp.set(int(self.in0) + int(self.in1) + int(self.cin))
        
        # update the output port values
        self.sum.set(temp[self.width-1::-1])
        self.cout.set(temp[self.width])
        return self
    
    def force_carry_out(x: Signal, y: Signal):
        """
        Generate a test case when the carry out signal should be triggered.
        """
        x.set(random.randint(1, x.max()))
        y.set(y.max()+1-x.get(int))
    
    pass


def apply_coverage(add: Add):
    """
    Define coverage areas.
    """

    # Cover the entire range for in0 into at most 16 bins and make sure
    # each bin is tested at least once.
    cg_in0_full = CoverRange(
        name="in0 full",
        span=add.in0.span(),
        goal=1,
        max_steps=16,
        target=add.in0
    )

    # Cover the entire range for in1 into at most 16 bins and make sure 
    # each bin is tested at least once.
    cg_in1_full = CoverRange(
        name="in1 full",
        span=add.in1.span(),
        goal=1,
        max_steps=16,
        target=add.in1,
    )

    # Make sure all combinations of input bins are tested at least once. It is possible
    # to define this cross coverage as a CoverRange.
    CoverCross(
        name="in0 cross in1",
        nets=[cg_in0_full, cg_in1_full],
    )

    # Cover the case that cin is asserted at least 100 times.
    CoverPoint(
        name="cin asserted",
        goal=100,
        target=add.cin,
        checker=lambda x: int(x) == 1,
    )

    # Cover the extreme edge cases for in0 (min and max) at least 10 times.
    CoverGroup(
        name="in0 extremes",
        goal=10,
        target=add.in0,
        bins=[add.in0.min(), add.in0.max()]
    )

    # Cover the extreme edge cases for in1 (min and max) at least 10 times.
    CoverGroup(
        name="in1 extremes",
        goal=10,
        target=add.in1,
        bins=[add.in1.min(), add.in1.max()]
    )

    # Check to make sure both inputs are 0 at the same time at least once.
    CoverPoint(
        name="in0 and in1 equal 0",
        goal=1,
        target=(add.in0, add.in1),
        advancer=lambda x, y: (x.set(x.min()), y.set(y.min())),
        checker=lambda x, y: int(x) == x.min() and int(y) == y.min()
    )

    # Check to make sure both inputs are the maximum value at the same time at least once.
    CoverPoint(
        name="in0 and in1 equal max",
        goal=1,
        target=(add.in0, add.in1),
        advancer=lambda x, y: (x.set(x.max()), y.set(y.max())),
        checker=lambda x, y: int(x) == x.max() and int(y) == y.max()
    )

    # Cover the case that the carry out is generated at least 10 times.
    CoverPoint(
        name="cout generated",
        goal=10,
        source=(add.in0, add.in1),
        advancer=Add.force_carry_out,
        sink=add.cout,
        checker=lambda x: int(x) == 1
    )


def main():
    # Create an instance of the model
    add = Add(
        width=vb.load_param('WORD_SIZE', type=int)
    )
    
    # Provide coverage on the model
    apply_coverage(add)

    # Run the model
    with vb.vectors('inputs.txt') as vi, vb.vectors('outputs.txt') as vo:
        while vb.running(10_000):
            # Generate inputs
            add.setup()
            vi.push(add)
            # Compute outputs
            add.compute()
            vo.push(add)
            pass
        pass


if __name__ == '__main__':
    main()