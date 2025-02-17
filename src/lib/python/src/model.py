from .signal import *
from .vectors import *
from enum import Enum as _Enum

class Strategy(_Enum):
    """
    Method for constrained randomization.
    """
    NONE = 0,
    LINEAR = 1,
    RANDOM = 2,
    WEIGHTS = 3,

    @staticmethod
    def from_str(s: str):
        s = s.lower()
        if s == 'none':
            return Strategy.NONE
        elif s == 'linear':
            return Strategy.LINEAR
        elif s == 'uniform':
            return Strategy.RANDOM
        elif s == 'weights':
            return Strategy.WEIGHTS
        else:
            raise Exception('Failed to convert str '+s+' to class `Strategy`')
    pass


def __compile_ports(model):
    """
    Compiles the list of ports into a mapping where the 'key' is the defined name
    and the 'value' is a tuple (Signal, Dict).
    """
    from .context import Context, Runner

    # save computations
    if hasattr(model, '__verb_cached_ports') == True:
        return model.__verb_cached_ports

    runner: Runner = Context.current()
    
    model.__verb_cached_ports = dict()
    for (key, val) in vars(model).items():
        # only python variables declared as signals can be a port
        if isinstance(val, Signal) == False:
            continue
        # override variable name with explicit name provided
        defined_name = key if val._name == None else val._name
        # check if the name is in the port interface data
        port = runner.port(defined_name)
        if port != None:
            index = runner.port_index(defined_name)
            # store the interface data and the signal data together
            model.__verb_cached_ports[defined_name] = (index, val, port)
        pass
    return model.__verb_cached_ports


def _extract_ports(model, mode: Mode):
    """
    Collects the attributes defined in the `model` into a list storing
    the tuples of their (name, signal).
    """
    results = []

    key: str
    info: Signal
    port: dict
    for (key, (index, info, port)) in __compile_ports(model).items():
        use_mode = Mode.from_str(port['mode']) if info._mode == Mode.INFER else info._mode
        info._inferred_mode = use_mode
        if use_mode != mode:
            continue
        results += [(index, key, info)]
        pass

    results.sort()
    # store tuple with (name, signal)
    results = [(x[1], x[2]) for x in results]
    # return the list of ports
    return results


def __compile_signals(model) -> dict:
    """
    Compiles the list of internal signals into a mapping where the 'key' is the defined name
    and the 'value' is a Signal.
    """
    from .context import Context, Runner

    # save computations
    if hasattr(model, '__verb_cached_signals') == True:
        return model.__verb_cached_signals

    runner: Runner = Context.current()
    
    model.__verb_cached_signals = dict()
    for (key, val) in vars(model).items():
        # only python variables declared as signals can be a port
        if isinstance(val, Signal) == False:
            continue
        # override variable name with explicit name provided
        defined_name = key if val._name == None else val._name
        # check if the name is in the port interface data
        port = runner.port(defined_name)
        if port == None:
            # store the signal data
            model.__verb_cached_signals[defined_name] = val
        pass
    return model.__verb_cached_signals


def _extract_signals(model):
    """
    Collects the attributes defined in the `model` into a list storing the tuples
    of their (name, signal).
    """
    results = []

    key: str
    for (key, val) in __compile_signals(model).items():
        results += [(key, val)]
        pass

    results.sort()
    # store tuple with (name, signal)
    results = [(x[0], x[1]) for x in results]
    # return the list of signals
    return results


import copy as _copy

class Clock:
    """
    Introduces the notion of time for things that require it within the model.
    """

    def __init__(self):
        """
        Create a new clock instance.
        """
        self._ticks = 0
        self._domain = []

    def tick(self):
        """
        Allow the clock to advance to the next time step.
        """
        self._ticks += 1
        for reg in self._domain:
            reg.prev = _copy.deepcopy(reg.now)
            reg.now = _copy.deepcopy(reg.next)

    def get_count(self) -> int:
        """
        Return the number of times this clock instance has ticked.
        """
        return self._ticks
    

class Reg:
    """
    Force updates to variables to be restricted to certain time advances.
    """

    def __init__(self, clk: Clock, val):
        """
        Encapsulate any variable/value `val` within a register instance bound to
        the clock domain of `clk`.

        The register stores 3 instances of the value:
        - `.prev`: a copy of the variable storing the value from the previous time step
        - `.now`: a reference to the variable storing the value for the current time step
        - `.next`: a copy of the variable storing the value for the upcoming time step

        Note the variable at `.now` is not guaranteed to maintain a reference to the same memory location
        as the original variable as the model updates over time.

        The values are updated in the following order when the `clk` variable calls the `.tick()` method:
        1. `.now` passes its value to `.prev`
        2. `.next` passes its value to `.now`
        """
        # initialize the previous state
        self.prev = _copy.deepcopy(val)
        # initialize interal "registered" state
        self.now = val
        # initailize incoming "next" state
        self.next = _copy.deepcopy(val)
        # add this register to the clock's domain
        clk._domain += [self]