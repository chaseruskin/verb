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
    '''
    Compiles the list of ports into a mapping where the 'key' is the defined name
    and the 'value' is a tuple (Signal, Dict).
    '''
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
    '''
    Collects the attributes defined in the `model` into a list storing
    the tuples of their (name, signal).
    '''
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


def __compile_signals(model):
    '''
    Compiles the list of internal signals into a mapping where the 'key' is the defined name
    and the 'value' is a Signal.
    '''
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
    '''
    Collects the attributes defined in the `model` into a list storing the tuples
    of their (name, signal).
    '''
    results = []

    key: str
    info: Signal
    port: dict
    for (key, val) in __compile_signals(model).items():
        results += [(key, val)]
        pass

    results.sort()
    # store tuple with (name, signal)
    results = [(x[0], x[1]) for x in results]
    # return the list of signals
    return results
