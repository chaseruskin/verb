'''
Software drivers for simulating hardware with Verb.
'''

__all__ = ["primitives", "context", "signal", "model", "coverage", "analysis"]
__version__ = '0.1.0'

from . import context as context
from . import coverage as coverage
from . import signal as signal
from . import model as model
from . import analysis as analysis

from .primitives import *


def running(limit: int=100_000, stop_if_covered: bool=True) -> bool:
    """
    Returns true for up to `limit` iterations.

    If coverages are created and `stop_if_covered` is set true, then this
    function will return false if all coverages have met their goal before
    reaching the `limit` iteration count.

    The limit can be overridden if the context received a value from the
    command-line.

    Setting the `limit` to -1 will allow the model to run infinitely.
    """

    if context.Context.current()._context._max_test_count > -1:
        limit = int(context.Context.current()._context._max_test_count)

    # force the modeling to end if reached the iteration limit
    if limit > 0 and coverage.CoverageNet._counter >= limit:
        coverage.Coverage.save()
        return False
    # allow modeling to end when all coverages are met
    if stop_if_covered == True and len(coverage.CoverageNet._group) > 0:
        net: coverage.CoverageNet
        for net in coverage.CoverageNet._group:
            if net.skipped() == False and net.passed() == False:
                # increment the counter
                coverage.CoverageNet._counter += 1
                # keep the model running
                return True
        # passed all coverages... stop modeling
        coverage.Coverage.save()
        return False
    # increment as normal counter
    else:
        coverage.CoverageNet._counter += 1
    return True