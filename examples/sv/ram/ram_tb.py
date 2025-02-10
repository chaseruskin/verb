# Model a ram module

import verb as vb
from verb.model import *
from verb.coverage import *


class Ram:
    """
    Functional model for the `ram` module.
    """

    def __init__(self, addr_width: int, data_width: int):
        """
        Create a new design unit model.
        """
        # parameters
        self.addr_width = addr_width
        self.data_width = data_width
        # inputs
        self.waddr = Signal(addr_width)
        self.wdata = Signal(data_width)
        self.wen = Signal()
        self.raddr = Signal(addr_width)
        # outputs
        self.rdata = Signal(data_width)

        self.clk = Clock()  
        # registers
        self.mem = Reg(self.clk, [0] * (2**addr_width))
        pass

    def setup(self):
        """
        Assign the next set of inputs.
        """
        vb.randomize(self)

    def compute(self):
        """
        Model the functional behavior of the design unit.
        """
        # model how the output is set
        self.rdata.set(self.mem.now[self.raddr.get(int)])
        if self.raddr.get(int) == self.waddr.get(int):
            self.rdata.set(self.wdata.get(int))
        # model how to update the internal memory cells
        if self.wen.get(int) == 1:
            self.mem.next[self.waddr.get(int)] = self.wdata.get(int)
        # advance to next time
        self.clk.tick()
    
    pass


def apply_coverage(ram: Ram):
    """
    Define coverage areas.
    """

    cr0 = CoverRange(
        name="waddr range",
        goal=2,
        span=ram.waddr.span(),
        target=ram.waddr
    )

    cr1 = CoverRange(
        name="raddr range",
        goal=2,
        span=ram.raddr.span(),
        target=ram.raddr
    )

    cr2 = CoverRange(
        name="wdata range",
        goal=2,
        span=ram.wdata.span(),
        target=ram.wdata
    )

    cp0 = CoverPoint(
        name="wen",
        goal=50,
        target=ram.wen,
    )

    CoverCross(
        name="input combos",
        nets=[cr0, cr1, cr2, cp0]
    )

    CoverPoint(
        name="raddr is waddr",
        goal=10,
        sink=(ram.raddr, ram.waddr, ram.wen),
        checker=lambda x, y, z: x.get(int) == y.get(int) and z.get(int) == 1
    )
    pass


def main():
    # Create an instance of the model
    ram = Ram(
        addr_width=vb.load_param('ADDR_WIDTH', dtype=int),
        data_width=vb.load_param('DATA_WIDTH', dtype=int)
    )
    
    # Provide coverage on the model
    apply_coverage(ram)

    # Run the model
    with vb.vectors('inputs.txt') as vi, vb.vectors('outputs.txt') as vo:
        while vb.running(1_000):
            # Generate inputs
            ram.setup()
            vi.push(ram)
            # Compute outputs
            ram.compute()
            vo.push(ram)
            pass
        pass


if __name__ == '__main__':
    main()