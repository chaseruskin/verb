# Model: alu
#
# This script generates test vectors for running simulations using file IO as
# well as generates a coverage report as well to indicate the robust of the 
# test.

from enum import Enum

from verb.coverage import *
from verb.model import Signal, Clock, Reg, Mode, Distribution

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
        return func < 10
    

class Alu:

    def __init__(self, PHYS_REG_WIDTH=6):
        """
        Create an instance of the model.
        """
        self.FUNC_CODES = [*range(0, 10)]
        self.DATA_WIDTH = 32
        self.FUNC_WIDTH = 4

        # inputs
        self.clear = Signal(dist=Distribution([0, 1], [0.90, 0.10]))
        self.en = Signal(dist=Distribution([0, 1], [0.2, 0.8]))

        self.alu_func = Signal(self.FUNC_WIDTH)
        self.rs1 = Signal(self.DATA_WIDTH)
        self.rs2 = Signal(self.DATA_WIDTH)

        self.broadcasted = Signal(dist=Distribution([0, 1], [0.3, 0.7]))

        self.dest_tag_in = Signal(PHYS_REG_WIDTH)
        self.dest_tag_wr_en_in = Signal()

        # outputs
        self.result = Signal(self.DATA_WIDTH)

        self.next_valid = Signal()
        self.ready_next = Signal(value=1)

        self.dest_tag_out = Signal(PHYS_REG_WIDTH)
        self.dest_tag_wr_en_out = Signal()

        # clocks
        self.clk = Clock()
        # internal registers
        self.valid_r = Reg(self.clk, self.next_valid)
        self.ready_r = Reg(self.clk, self.ready_next)
        self.rs1_r = Reg(self.clk, self.rs1)
        self.rs2_r = Reg(self.clk, self.rs2)
        self.clear_r = Reg(self.clk, self.clear)
        self.dest_tag_r = Reg(self.clk, self.dest_tag_in)
        self.dest_tag_wr_en_r = Reg(self.clk, self.dest_tag_wr_en_in)
        pass

    def setup(self):
        """
        Setup the inputs for the model
        """
        # randomly sample all inputs if the unit is able to accept new inputs
        if self.ready_r.prev:
            vb.randomize(self)
        else:
            self.broadcasted.sample()
            self.clear.sample()

        # can only receive a broadcast if there was data available on last cycle
        if not self.valid_r.prev:
            self.broadcasted.set(0)

        # assign input registers
        self.clear_r.now = self.clear
        self.rs1_r.now = self.rs1
        self.rs2_r.now = self.rs2
        self.dest_tag_r.now = self.dest_tag_in
        self.dest_tag_wr_en_r.now = self.dest_tag_wr_en_in
    
    def model(self):
        """
        Model the functional behavior of the design unit.
        """
        # handle control logic
        save_data = False

        # determine valid next signal  
        self.next_valid.set(self.valid_r.prev)
        if self.clear:
            self.next_valid.set(0)
        elif self.broadcasted:
            self.next_valid.set(self.en)
        
        # # determine if we should save the results of this data
        # save_data = self.en if self.ready_ else 0

        # set the outputs based on the current inputs
        if self.next_valid:
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

        # determine ready next for current cycle
        self.ready_next.set((self.broadcasted or not self.next_valid) and not self.clear)

        # re-update the ready next signal to be used in the next state of the `setup`
        self.ready_next.set(int((self.broadcasted.get(int) == 1 or self.next_valid.get(int) == 0) and self.clear.get(int) == 0))
        
        # assign output registers
        self.valid_r.now = self.next_valid
        self.ready_r.now = self.ready_next


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
    
    CoverPoint(
        name="invalid function codes",
        goal=10,
        sink=mdl.alu_func,
        checker=lambda x: AluFunc.is_valid(int(x)),
    )


def main():
    alu = Alu()

    # Specify coverage areas
    apply_coverage(alu)

    # Run the model!
    print('info: running software model ...')
    with vb.vectors('inputs.txt') as vi, vb.vectors('outputs.txt') as vo:
        while vb.running(1_000):
            print('cycle:', alu.clk.get_count())
            # determine which inputs to assign next
            alu.setup()
            # save the inputs for this transaction
            vi.push(alu)
            # let the model act on this set of inputs
            alu.model()
            # save the outputs associated with this set of inputs
            vo.push(alu)
            # proceed to next time-step
            alu.clk.tick()
        pass

if __name__ == '__main__':
    main()
