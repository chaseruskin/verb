"""
Software drivers for modeling hardware.
"""

# metadata
__all__ = ["primitives", "context", "signal", "model", "coverage"]
__version__ = "0.1.0"
__author__ = "Chase Ruskin"
__email__ = "c.ruskin@ufl.edu"
__copyright__ = "Copyright 2025 Chase Ruskin"
__license__ = "MIT"

# imports
from . import primitives as _primitives
from . import context as _context
from . import signal as _signal

from . import coverage as coverage
from . import model as model

from .primitives import *

from .model import Vectors as _Vectors
from .model import Mode as _Mode

# module-level (easilty public-facing) functions

def load_param(key: str, dtype: type):
    """
    Accesses the HDL parameter/generic based upon the provided `key`.

    ### Parameters
    - `key`: name of the HDL parameter/generic
    - `dtype`: datatype to interpret the value of the HDL parameter/generic

    By providing a value for `dtype` (such as `int`), the value of the HDL parameter/generic
    will be converted to the Python-friendly datatype. By default, all values returned are
    left as `str`.
    """
    return _context.generic(key, dtype)


def reset():
    """
    Reset the internal iteration counter.

    This function may be used if a model script wants to call the
    `running()` method multiple times in a single execution.
    """
    coverage._CoverageNet._counter = 0


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

    if _context.Context.current()._context._max_test_count > -1:
        limit = int(_context.Context.current()._context._max_test_count)

    # force the modeling to end if reached the iteration limit
    if limit > 0 and coverage._CoverageNet._counter >= limit:
        coverage.Coverage.save()
        return False
    # allow modeling to end when all coverages are met
    if stop_if_covered == True and len(coverage._CoverageNet._group) > 0:
        net: coverage._CoverageNet
        for net in coverage._CoverageNet._group:
            if net.skipped() == False and net.passed() == False:
                # increment the counter
                coverage._CoverageNet._counter += 1
                # keep the model running
                return True
        # passed all coverages... stop modeling
        coverage.Coverage.save()
        return False
    # increment as normal counter
    else:
        coverage._CoverageNet._counter += 1
    return True


def vectors(path: str, mode: _Mode=None) -> _Vectors:
    """
    Creates a test vectors file to write stimuli/results for a future hardware simulation.

    ### Parameters
    - `name`: the file's path name
    - `mode`: which directional ports to write to the file

    If `mode` is set to None, then the mode can be inferred from the path's file name.
    The following names (excluding file extension) allow port inference:
    - "inputs": inferred to capture ports of mode `IN`
    - "outputs": inferred to capture ports of mode `OUT`
    """
    import os
    from .model import Vectors, Mode

    if mode == None:
        fname, _ = os.path.splitext(os.path.basename(path))
        if fname == 'inputs':
            mode = Mode.IN
        elif fname == 'outputs':
            mode = Mode.OUT
        else:
            raise Exception("cannot assume port mode for vectors file: " + str(path))
    return Vectors(path, mode)


def randomize(model, strategy: str="weights"):
    """
    Assign random input values to each attribute of the model instance that is
    a known input port.

    After this function is called, all the known input ports under the `model`
    instance will have a random value according to the `strategy`. Calling this
    function allows the user to leverage constrained randommization and avoid
    having to individually sample each input port.

    ### Parameters
    - `model`: mutable reference to an instance that has attributes of known input ports
    - `strategy`: specify how to constrain the random input generation

    This function mutates the object `model` and returns a reference to the same object.

    A strategy can be provided to provide coverage-driven input test vectors. The following
    strategies are currently available:
    - "none": use the default distributions for each input
    - "linear": iterate through the list of coverage nets and draw the next value to help close the first failing coverage net
    - "random": sample a failing coverage net at random using uniform distribution and draw the next value to help close its coverage
    - "weights": sample a coverage net to advance according to its normalized weighted distribution of its distance from its goal
    """
    from .coverage import _CoverageNet, Coverage
    from .model import Signal, Strategy, Mode, _extract_ports
    import random

    net: _CoverageNet
    port: Signal

    strat: Strategy = Strategy.from_str(strategy)

    ports = [p[1] for p in _extract_ports(model, mode=Mode.IN)]

    # always randomize all inputs no matter the strategy (default strategy)
    for port in ports:
        port.sample()
        pass

    # use default provided distributions for each signal
    if strat == Strategy.NONE:
        pass
    # go down list of each coverage net and draw a next value to help close coverage
    elif strat == Strategy.LINEAR:
        # collect the set of nets
        failing_nets = Coverage.get_failing_nets()
        # only work with coverage nets that deal with this model
        for net in failing_nets:
            # only work on coverage nets that are allowed to be auto-written
            if net.has_source() == True:
                sources = net.get_source_list()
                # verify each writer exists in this current model
                for source in sources:
                    if type(source) == Signal and source not in ports:
                        break
                else:
                    net.advance(rand=True)
                # exit- we only want to ensure we progress toward one coverage
                break
            pass
        pass
    # select a coverage net at random using uniform distribution for next value to help close coverage
    elif strat == Strategy.RANDOM:
        candidates = []
        # collect the set of nets
        failing_nets = Coverage.get_failing_nets()
        # only work with coverage nets that deal with this model
        for net in failing_nets:
            # only work on coverage nets that are allowed to be auto-written
            if net.has_source() == True:
                sources = net.get_source_list()
                # verify each writer exists in this current model
                for source in sources:
                    if type(source) == Signal and source not in ports:
                        break
                else:
                    candidates += [net]
                pass
            pass
        # choose a failing net at random
        if len(candidates) > 0:
            sel: _CoverageNet = random.choice(candidates)
            sel.advance(rand=True)
            pass
        pass
    # select a coverage net according to a weighted distribution using its distance to its goal
    elif strat == Strategy.WEIGHTS:
        candidates = []
        weights = []
        # collect the set of nets
        failing_nets = Coverage.get_failing_nets()
        # only work with coverage nets that deal with this model
        for net in failing_nets:
            # only work on coverage nets that are allowed to be auto-written
            if net.has_source() == True:
                sources = net.get_source_list()
                # verify each writer exists in this current model
                for source in sources:
                    if type(source) == Signal and source not in ports:
                        break
                else:
                    candidates += [net]
                    weights += [net.get_goal() - net.get_count()]
                pass
            pass
        # create the distribution weights for probability assignments
        total_weight = 0
        for i in weights: total_weight += i
        weights = [w/total_weight for w in weights]
        # choose a failing net at random
        if len(candidates) > 0:
            sel = random.choices(candidates, weights=weights)[0]
            sel.advance(rand=True)
            pass   
        pass
    pass