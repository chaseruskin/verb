# Project: Vertex
# Model: add
#
# This script generates the I/O test vector files to be used with the 
# add_tb.vhd testbench.
#
# Generates a coverage report as well to indicate the robust of the test.

import random
from vertex.context import *
from vertex.model import *
from vertex.coverage import *

# define the functional model
class Add:

    def __init__(self, width: int):
        # parameters
        self.width = width
        # inputs
        self.in0 = Signal(width, distribution=Distribution(space=[0, pow2m1(width), range(1, pow2m1(width))], weights=[0.1, 0.1, 0.8]))
        self.in1 = Signal(width, distribution=Distribution(space=[0, pow2m1(width), range(1, pow2m1(width))], weights=[0.1, 0.1, 0.8]))
        self.cin = Signal(1)
        # outputs
        self.sum = Signal(width)
        self.cout = Signal(1)
        pass


    def eval(self):
        temp = Signal(self.width+1)
        temp.data = int(self.in0) + int(self.in1) + int(self.cin)
        
        # update the output port values
        self.sum.data = temp[self.width-1::-1]
        self.cout.data = temp[self.width]
        return self
    pass


add = Add(width=context.param('WORD_SIZE', type=int))

# Specify coverage areas

# Cover the entire range for in0 into at most 16 bins and make sure
# each bin is tested at least once.
cg_in0_full = CoverRange(
    "in0 full",
    span=add.in0.span(),
    goal=1,
    max_steps=16,
    target=add.in0,
)

# Cover the entire range for in1 into at most 16 bins and make sure 
# each bin is tested at least once.
cg_in1_full = CoverRange("in1 full",
    span=add.in1.span(),
    goal=1,
    max_steps=16,
    target=add.in1,
)

# Cover the case that cin is asserted at least 100 times.
cp_cin_asserted = CoverPoint("cin asserted",
    goal=100,
    cover=lambda x: int(x) == 1,
    target=add.cin,
)

# Cover the extreme edge cases for in0 (min and max) at least 10 times.
cg_in0_extremes = CoverGroup("in0 extremes",
    bins=[add.in0.min(), add.in0.max()],
    goal=10,
    target=add.in0,
)

# Cover the extreme edge cases for in1 (min and max) at least 10 times.
cg_in1_extremes = CoverGroup("in1 extremes",
    bins=[add.in1.min(), add.in1.max()],
    goal=10,
    target=add.in1,
)

# Make sure all combinations of input bins are tested at least once. It is possible
# to define this cross coverage as a CoverRange.
cg_in0_cross_in1 = CoverCross("in0 cross in1",
    nets=[cg_in0_full, cg_in1_full]
)

# Check to make sure both inputs are 0 at the same time at least once.
cp_in0_in1_eq_0 = CoverPoint("in0 and in1 equal 0", 
    goal=1,
    target=(add.in0, add.in1),
    advance=lambda p: (p[0].min(), p[1].min()),
    cover=lambda p: int(p[0]) == 0 and int(p[1]) == 0,
)

# Check to make sure both inputs are the maximum value at the same time at least once.
cp_in0_in1_eq_max = CoverPoint("in0 and in1 equal max", 
    goal=1,
    target=(add.in0, add.in1),
    advance=lambda p: (p[0].max(), p[1].max()),
    cover=lambda p: int(p[0]) == p[0].max() and int(p[1]) == p[1].max(),
)

def fn_cp_cout_gen(p):
    in0 = random.randint(1, p[0].max())
    return (in0, p[1].max() + 1 - in0)

# Cover the case that the carry out is generated at least 10 times.
cp_cout_gen = CoverPoint("cout generated", 
    goal=10,
    source=(add.in0, add.in1),
    advance=fn_cp_cout_gen,
    sink=add.cout,
    cover=lambda x: int(x) == 1,
)

with vectors('inputs.txt', 'i') as inputs, vectors('outputs.txt', 'o') as outputs:
    while Coverage.met() == False:
        outcome: Add = randomize(add)
        inputs.append(outcome)

        outcome.eval()
        outputs.append(outcome)
        pass
    pass

print(Coverage.summary())