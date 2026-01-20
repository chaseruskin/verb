import random
import cocotb
import verb as vb
from verb import Model, Signal, Constant, Logics, Dist


class Adder(Model):

    def __init__(self):
        # parameters
        self.WORD_SIZE = Constant()
        super().mirror()
        # inputs
        self.in0 = Signal( 
            dist=Dist(
                space=[0, 2**self.WORD_SIZE.value-1, range(1, 2**self.WORD_SIZE.value-1)], 
                weights=[0.1, 0.1, 0.8]
            )
        )
        self.in1 = Signal(
            dist=Dist(
                space=[0, 2**self.WORD_SIZE.value-1, range(1, 2**self.WORD_SIZE.value-1)], 
                weights=[0.1, 0.1, 0.8]
            )
        )
        self.cin = Signal()
        # outputs
        self.sum = Signal()
        self.cout = Signal()
        super().mirror()

    def define_coverage(self):
        from verb.coverage import CoverRange, CoverCross, CoverPoint, CoverGroup

        def force_min(x: Signal, y: Signal):
            x.value = x.min()
            y.value = y.min()

        def force_max(x: Signal, y: Signal):
            x.value = x.max()
            y.value = y.max()

        def force_carry_out(x: Signal, y: Signal):
            """
            Generate a test case when the carry out signal should be triggered.
            """
            x.value = random.randint(1, x.max())
            y.value = y.max()+1-int(x)

        # Cover the entire range for in0 into at most 16 bins and make sure
        # each bin is tested at least once.
        cg_in0_full = CoverRange(
            name="in0 full",
            span=self.in0.span(),
            goal=1,
            max_steps=16,
            target=self.in0
        )

        # Cover the entire range for in1 into at most 16 bins and make sure 
        # each bin is tested at least once.
        cg_in1_full = CoverRange(
            name="in1 full",
            span=self.in1.span(),
            goal=1,
            max_steps=16,
            target=self.in1,
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
            target=self.cin,
            checker=lambda x: int(x) == 1,
        )

        # Cover the extreme edge cases for in0 (min and max) at least 10 times.
        CoverGroup(
            name="in0 extremes",
            goal=10,
            target=self.in0,
            bins=[self.in0.min(), self.in0.max()]
        )

        # Cover the extreme edge cases for in1 (min and max) at least 10 times.
        CoverGroup(
            name="in1 extremes",
            goal=10,
            target=self.in1,
            bins=[self.in1.min(), self.in1.max()]
        )

        # Check to make sure both inputs are 0 at the same time at least once.
        CoverPoint(
            name="in0 and in1 equal 0",
            goal=1,
            target=(self.in0, self.in1),
            advancer=force_min,
            checker=lambda x, y: int(x.value) == x.min() and int(y.value) == y.min()
        )

        # Check to make sure both inputs are the maximum value at the same time at least once.
        CoverPoint(
            name="in0 and in1 equal max",
            goal=1,
            target=(self.in0, self.in1),
            advancer=force_max,
            checker=lambda x, y: int(x.value) == x.max() and int(y.value) == y.max()
        )

        # Cover the case that the carry out is generated at least 10 times.
        CoverPoint(
            name="cout generated",
            goal=10,
            source=(self.in0, self.in1),
            advancer=force_carry_out,
            sink=self.cout,
            checker=lambda x: int(x) == 1
        )
        super().cover()

    async def setup(self):
        """
        Determine the next set of inputs.
        """
        while vb.running():
            self.randomize()
            await vb.falling_edge()

    async def model(self):
        """
        Model the functional behavior of the design unit.
        """
        while vb.running():
            await vb.rising_edge()
            sum = int(self.in0.value) + int(self.in1.value) + int(self.cin.value)
            temp = Logics(sum, self.WORD_SIZE.value+1)
            # update the output port values
            self.sum.value = temp[self.WORD_SIZE.value-1:0]
            self.cout.value = temp[self.WORD_SIZE.value]
            # verify the outputs
            vb.assert_eq(self.sum.get_handle(), self.sum)
            vb.assert_eq(self.cout.get_handle(), self.cout)


@cocotb.test()
async def test(top):
    vb.initialize(top)
    # Create an instance of the model
    mdl = Adder()
    mdl.define_coverage()

    # Run the model
    await vb.first(
        cocotb.start_soon(mdl.setup()),
        cocotb.start_soon(mdl.model())
    )
    vb.complete()
