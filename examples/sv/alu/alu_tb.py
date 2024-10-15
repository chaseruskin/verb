# Model: alu
#
# This script generates test vectors for running simulations using file IO as
# well as generates a coverage report as well to indicate the robust of the 
# test.

import random
from verb import context, coverage
from verb.model import *
from verb.coverage import *

# Define the functional model
class Alu:

    def __init__(self):
        '''
        Create a new design unit model.
        '''
        # parameters

        # inputs
        self.opa = Signal(32)
        self.opb = Signal(32)
        self.alu_func = Signal(4)
        # outputs
        self.result = Signal(32)

    def eval(self):
        '''
        Model the functional behavior of the design unit.
        '''


        return self


def main():
    '''
    Run the model.
    '''
    alu = Alu(
    )

    # Specify coverage areas

    cr_alu_func = CoverRange("alu func") \
        .span(alu.alu_func.span()) \
        .goal(1) \
        .target(alu.alu_func) \
        .apply()
    
    cr_opa = CoverRange("op a") \
        .span(alu.opa.span()) \
        .goal(3) \
        .target(alu.opa) \
        .apply()
        
    cr_opb = CoverRange("op b") \
        .span(alu.opb.span()) \
        .target(alu.opb) \
        .goal(3) \
        .apply()
        
    CoverCross("input cross") \
        .nets(cr_alu_func, cr_opa, cr_opb) \
        .apply()

    # Run the model!

    with vectors('inputs.txt', 'i') as inputs, vectors('outputs.txt', 'o') as outputs:
        while coverage.met(1_000) == False:
            # randomize the set of inputs (while progressing toward coverage)
            txn: Alu = randomize(alu)
            # save the inputs for this transaction
            inputs.push(txn)
            # let the model act on this set of inputs
            txn.eval()
            # save the outputs associated with this set of inputs
            outputs.push(txn)


if __name__ == '__main__':
    main()
