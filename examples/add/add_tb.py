# Project: veriti
# Script: add_tb.py
#
# This script generates the I/O test vector files to be used with the 
# add_tb.vhd testbench. Generic values for `LEN` can be passed through the 
# command-line. 
#
# Generates a coverage report as well to indicate the robust of the test.

from vertex.context import *
from vertex.model import *
from vertex.coverage import *

# also allow to specify the set of command-line arguments
# .param_args(sys.argv) \
c = Context() \
    .tb_interface('examples/add/add_tb_if.json') \
    .dut_interface('examples/add/add_if.json') \
    .max_test_count(5_000) \
    .seed(0) \
    .build()

# define the functional model
class Add:

    def __init__(self, width: int):
        # inputs
        self.width = width
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


add = Add(width=c.param('WORD_SIZE', type=int))

# add.in0.store(4)
add.in0.data = 4
add.in1.data = 3
add.eval()
print(int(add.cout), int(add.sum))

# # Specify coverage areas

# Coverage()

# # Cover the entire range for in0 into at most 16 bins and make sure
# # each bin is tested at least once.
# cg_in0_full = CoverRange(
#     "in0 full",
#     span=model.in0.get_range(),
#     goal=1,
#     max_steps=16,
#     target=model.in0,
# )

# # Cover the entire range for in1 into at most 16 bins and make sure 
# # each bin is tested at least once.
# cg_in1_full = CoverRange(
#     "in1 full",
#     span=model.in1.get_range(),
#     goal=1,
#     max_steps=16,
#     target=model.in1,
# )

# # Cover the case that cin is asserted at least 100 times.
# cp_cin_asserted = CoverPoint(
#     "cin asserted",
#     goal=100,
#     cover=lambda x: int(x) == 1,
#     target=model.cin,
# )

# # Cover the extreme edge cases for in0 (min and max) at least 10 times.
# cg_in0_extremes = CoverGroup(
#     "in0 extremes",
#     bins=[model.in0.min(), model.in0.max()],
#     goal=10,
#     target=model.in0,
# )

# # Cover the extreme edge cases for in1 (min and max) at least 10 times.
# cg_in1_extremes = CoverGroup(
#     "in1 extremes",
#     bins=[model.in1.min(), model.in1.max()],
#     goal=10,
#     target=model.in1,
# )

# # Make sure all combinations of input bins are tested at least once. It is possible
# # to define this cross coverage as a CoverRange.
# cg_in0_cross_in1 = CoverCross(
#     "in0 cross in1",
#     nets=[cg_in0_full, cg_in1_full]
# )

# # Check to make sure both inputs are 0 at the same time at least once.
# cp_in0_in1_eq_0    = CoverPoint(
#     "in0 and in1 equal 0", 
#     goal=1,
#     target=(model.in0, model.in1),
#     advance=lambda p: (p[0].min(), p[1].min()),
#     cover=lambda p: int(p[0]) == 0 and int(p[1]) == 0,
# )

# # Check to make sure both inputs are the maximum value at the same time at least once.
# cp_in0_in1_eq_max  = CoverPoint(
#     "in0 and in1 equal max", 
#     goal=1,
#     target=(model.in0, model.in1),
#     advance=lambda p: (p[0].max(), p[1].max()),
#     cover=lambda p: int(p[0]) == p[0].max() and int(p[1]) == p[1].max(),
# )

# def fn_cp_cout_gen(p):
#     in0 = random.randint(1, p[0].max())
#     return (in0, p[1].max() + 1 - in0)

# # Cover the case that the carry out is generated at least 10 times.
# cp_cout_gen = CoverPoint(
#     "cout generated", 
#     goal=10,
#     source=(model.in0, model.in1),
#     advance=fn_cp_cout_gen,
#     sink=model.cout,
#     cover=lambda x: int(x) == 1,
# )

# # Prepare the traces for simulation

# # create empty test vector files
# inputs = VectorFile('inputs.txt', Mode.IN).open()
# outputs = VectorFile('outputs.txt', Mode.OUT).open()

# # initialize the randomness seed
# random.seed(rng_seed(0))

# while coverage.is_met() == False:

#     pass

# # generate test cases until total coverage is met or we reached max count
# while Coverage.all_passed(MAX_SIMS) == False:

#     # Create a new input to enter through the algorithm and
#     # use coverage-driven test generation (CDTG) using linear priorities.
    
#     # When specifying CDTG ('linear'), it provides a 7x reduction in tests 
#     # required to meet coverage as compared to truly random ('none').
#     # It reduces 2010 tests to 288 to achieve the same coverage.
#     txn = randomize(model, strategy='linear')

#     # write each incoming transaction to the DUT
#     inputs.append(txn)
#     # compute expected values to send to simulation
#     txn = model.evaluate()
#     # write each expected outgoing transaction from the DUT
#     outputs.append(txn)
#     pass

# inputs.close()
# outputs.close()