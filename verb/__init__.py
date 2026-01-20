from .testbench import *
from .log import *
from .signal import Signal
from .constant import Constant
from .model import Model
from .signal import Dist
from cocotb.types import LogicArray as Logics
from cocotb.types import Logic


def running(limit: int=100_000, stop_if_covered: bool=True) -> bool:
    """
    Returns true for up to `limit` iterations.

    ### Parameters
    - `limit`: maximum number of iterations

    If coverages are created and `stop_if_covered` is set true, then this
    function will return false if all coverages have met their goal before
    reaching the `limit` iteration count.

    The limit can be overridden if the context received a value from the
    command-line.

    Setting the `limit` to -1 will allow the model to run infinitely.
    """
    from .coverage.net import CoverageNet
    from .coverage import Coverage
    # if _context.Context.current()._context._max_test_count > -1:
    #     limit = int(_context.Context.current()._context._max_test_count)

    # force the modeling to end if reached the iteration limit
    if limit > 0 and CoverageNet._counter >= limit:
        Coverage.save()
        return False
    # allow modeling to end when all coverages are met
    if stop_if_covered == True and len(CoverageNet._group) > 0:
        net: CoverageNet
        for net in CoverageNet._group:
            if net.skipped() == False and net.passed() == False:
                # increment the counter
                CoverageNet._counter += 1
                # keep the model running
                return True
        # passed all coverages... stop modeling
        Coverage.save()
        return False
    # increment as normal counter
    else:
        CoverageNet._counter += 1
    return True


async def combine(*trigger):
    '''
    Trigger that fires when all triggers have fired.
    '''
    import cocotb.triggers
    await cocotb.triggers.Combine(*trigger)


async def first(*trigger):
    '''
    Fires when the first trigger in triggers fires.
    '''
    import cocotb.triggers
    await cocotb.triggers.First(*trigger)