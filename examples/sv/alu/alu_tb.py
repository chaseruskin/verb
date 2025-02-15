# Model: alu
#
# This script generates test vectors for running simulations using file IO as
# well as generates a coverage report as well to indicate the robust of the 
# test.

from enum import Enum

from verb.coverage import *
from verb.model import *

import verb as vb

class AluFunc(Enum):
    """Represents ALU Functions defined in sys_defs.sv"""
    ALU_ADD   = 0
    ALU_SUB   = 1
    ALU_SLT   = 2
    ALU_SLTU  = 3
    ALU_AND   = 4
    ALU_OR    = 5
    ALU_XOR   = 6
    ALU_SLL   = 7
    ALU_SRL   = 8
    ALU_SRA   = 9
    INVALID_A = 10
    INVALID_B = 11
    INVALID_C = 12
    INVALID_D = 13
    INVALID_E = 14
    INVALID_F = 15

    @staticmethod
    def is_valid(func: int) -> bool:
        return not (func == 10 and func == 11 and func == 12 and func == 13 and func == 14 and func == 15)
    pass

# Define the functional model
class Alu:

    def __init__(self, PHYS_REG_WIDTH=6):
        """
        Create an instance of the model.
        """
        self.FUNC_CODES = [*range(0, 10)]

        # inputs
        self.clear = Signal(dist=Distribution([0, 1], [0.90, 0.10]))
        self.en = Signal(dist=Distribution([0, 1], [0.2, 0.8]))

        self.alu_func = Signal(4)
        self.rs1 = Signal(32)
        self.rs2 = Signal(32)

        self.broadcasted = Signal(dist=Distribution([0, 1], [0.3, 0.7]))

        self.dest_tag_in = Signal(PHYS_REG_WIDTH)
        self.dest_tag_wr_en_in = Signal()

        # outputs
        self.result = Signal(32)

        self.next_valid = Signal()
        self.ready_next = Signal(value=1)

        self.dest_tag_out = Signal(PHYS_REG_WIDTH)
        self.dest_tag_wr_en_out = Signal()

        # internal
        self._prev_valid = Signal(mode=Mode.LOCAL)

        self._prev_rs1 = Signal(32)
        self._prev_rs2 = Signal(32)
        self._prev_alu_func = Signal(4)
        self._prev_clear = Signal()
        self._prev_dest_tag = Signal(PHYS_REG_WIDTH)
        self._prev_dest_tag_wr_en = Signal()
        pass

    def setup(self):
        '''
        Setup the inputs for the model
        '''
        self._prev_clear.set(self.clear.get(int))

        vb.randomize(self)

        # can only broadcast if there is valid data
        if self._prev_valid.get(int) == 1:
            self.broadcasted.sample()
        else:
            self.broadcasted.set(0)

        self.en.sample()

        self.clear.sample()

        # hold inputs constant
        if self.ready_next.get(int) == 0:
            self.rs1.set(self._prev_rs1.get(int))
            self.rs2.set(self._prev_rs2.get(int))
            self.alu_func.set(self._prev_alu_func.get(int))
            self.dest_tag_in.set(self._prev_dest_tag.get(int))
            self.dest_tag_wr_en_in.set(self._prev_dest_tag_wr_en.get(int))
            pass

        if AluFunc.is_valid(self.alu_func.get(int)) == False:
            print('error: Assumption invalidated: func')
            exit(101)

        # update previous states
        self._prev_rs1.set(self.rs1.get(int))
        self._prev_rs2.set(self.rs2.get(int))
        self._prev_alu_func.set(self.alu_func.get(int))
        self._prev_dest_tag.set(self.dest_tag_in.get(int))
        self._prev_dest_tag_wr_en.set(self.dest_tag_wr_en_in.get(int))
        return self
    
    def model(self):
        """
        Model the functional behavior of the design unit.
        """
        # handle control logic
        save_data = 0

        self.ready_next.set(int((self.broadcasted.get(int) == 1 or self.next_valid.get(int) == 0) and self.clear.get(int) == 0))

        if self.clear.get(int) == 1:
            valid_next = 0
        elif self.ready_next.get(int) == 1:
            valid_next = self.en.get(int)
        else:
            valid_next = self.next_valid.get(int)

        # determine if we should save the results of this data
        save_data = self.en.get(int) if self.ready_next.get(int) == 1 else 0

        # set the outputs based on the current inputs
        if save_data == 1:
            func = AluFunc(self.alu_func.get(dtype=int))
            a = self.rs1.get(dtype=int)
            b = self.rs2.get(dtype=int)

            self.dest_tag_out.set(self.dest_tag_in.get(int))
            self.dest_tag_wr_en_out.set(self.dest_tag_wr_en_in.get(int))

            if func == AluFunc.ALU_ADD:
                self.result.set((a + b) & 0xFFFFFFFF)
            elif func == AluFunc.ALU_SUB:
                self.result.set((a - b) & 0xFFFFFFFF)
            elif func == AluFunc.ALU_SLT:
                self.result.set(7)
                a = Signal(32, self.rs1.get(dtype=str), signed=True).get(int)
                b = Signal(32, self.rs2.get(dtype=str), signed=True).get(int)
                self.result.set(1 if a < b else 0)
            elif func == AluFunc.ALU_SLTU:
                self.result.set(int(a < b))
            elif func == AluFunc.ALU_AND:
                self.result.set(a & b)
            elif func == AluFunc.ALU_OR:
                self.result.set(a | b)
            elif func == AluFunc.ALU_XOR:
                self.result.set(a ^ b)
            elif func == AluFunc.ALU_SLL:
                self.result.set((a << (b & 0x1F)) & 0xFFFFFFFF)
            elif func == AluFunc.ALU_SRL:
                self.result.set((a & 0xFFFFFFFF) >> (b & 0x1F))
            elif func == AluFunc.ALU_SRA:
                a_bits = self.rs1.get(dtype=str)
                # take the MSB to LSB of the lower 5 bits
                b_bits = self.rs2[:5][::-1]
                # do a shift based on leftmost bit for a
                shift_bit = a_bits[0]
                for _ in range(Signal(5, b_bits).get(int)):
                    a_bits = shift_bit + a_bits[:len(a_bits)-1]
                # set the result
                self.result.set(a_bits)
            else:
                self.result.set(0xdeadbeef)
            pass

        # remember the last state's valid
        self._prev_valid.set(int(self.next_valid.get(int) == 1 and self.clear.get(int) == 0))

        # update the valid register
        self.next_valid.set(valid_next)

        # re-update the ready next signal to be used in the next state of the `setup`
        self.ready_next.set(int((self.broadcasted.get(int) == 1 or self.next_valid.get(int) == 0) and self.clear.get(int) == 0))

        return self

def apply_coverage(mdl: Alu):
    """
    Define coverage areas for the model.
    """

    cr_alu_func = CoverRange(
        name="alu function code",
        span=mdl.alu_func.span(),
        goal=50,
        target=mdl.alu_func,
    )
    
    cr_rs1 = CoverRange(
        name="operand a",
        span=mdl.rs1.span(),
        goal=5,
        target=mdl.rs1,
    )

    cr_rs2 = CoverRange(
        name="operand b",
        span=mdl.rs2.span(),
        goal=5,
        target=mdl.rs2,
    )
        
    CoverCross(
        name="input cross",
        nets=[cr_alu_func, cr_rs1, cr_rs2],
        goal=5,
    )

    CoverPoint(
        name="clear asserted",
        goal=10,
        target=mdl.clear,
    )
    
    CoverPoint(
        name="valids",
        goal=300,
        target=mdl.next_valid
    )


def main():
    alu = Alu()

    # Specify coverage areas
    apply_coverage(alu)

    # Run the model!
    print('info: running software model ...')
    with vb.vectors('inputs.txt') as vi, vb.vectors('outputs.txt') as vo:
        while vb.running(2_000):
            # determine which inputs to assign next
            alu.setup()
            # save the inputs for this transaction
            vi.push(alu)
            # let the model act on this set of inputs
            alu.model()
            # save the outputs associated with this set of inputs
            vo.push(alu)
        pass

if __name__ == '__main__':
    main()
