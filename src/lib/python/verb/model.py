from .signal import *
from .vectors import *
from enum import Enum as _Enum

class Strategy(_Enum):
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
            raise Exception('Failed to convert str '+s+' to type Strategy')
    pass


def vectors(path: str, mode: Mode) -> Vectors:
    return Vectors(path, mode)


def randomize(model, strategy: str='weights'):
    '''
    Generates random input values for each attribute for the BFM. This is
    a convenience function for individually setting each signal randomly.

    This function mutates the object `model` and returns a reference to the same object.

    A strategy can be provided to provide coverage-driven input test vectors.
    '''
    from .coverage import CoverageNet, Coverage
    import random

    net: CoverageNet
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
                    values = net.advance(rand=True)
                    # force into an iterable type
                    if type(values) == int:
                        values = [values]
                    for i in range(len(sources)):
                        if type(sources[i]) == Signal:
                            sources[i].assign(values[i])
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
            sel = random.choice(candidates)
            values = sel.advance(rand=True)
            # force into an iterable type
            if type(values) == int:
                values = [values]
            sources = sel.get_source_list()
            for i in range(len(sources)):
                if type(sources[i]) == Signal:
                    sources[i].assign(values[i])
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
            values = sel.advance(rand=True)
            # force into an iterable type
            if type(values) == int:
                values = [values]
            sources = sel.get_source_list()
            for i in range(len(sources)):
                if type(sources[i]) == Signal:
                    sources[i].assign(values[i])
            pass   
        pass

    return model


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
