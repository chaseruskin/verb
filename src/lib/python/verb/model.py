from .signal import *
from .vectors import *
from enum import Enum as _Enum

class Strategy(_Enum):
    NONE = 0,
    LINEAR = 1,

    @staticmethod
    def from_str(s: str):
        s = s.lower()
        if s == 'none':
            return Strategy.NONE
        elif s == 'linear':
            return Strategy.LINEAR
        else:
            raise Exception('Failed to convert str '+s+' to type Strategy')
    pass


def vectors(path: str, mode: Mode) -> Vectors:
    return Vectors(path, mode)


def randomize(model, strategy: str='linear'):
    '''
    Generates random input values for each attribute for the BFM. This is
    a convenience function for individually setting each signal randomly.

    This function mutates the object `model` and returns a reference to the same object.

    A strategy can be provided to provide coverage-driven input test vectors.
    '''
    from .coverage import CoverageNet, Coverage

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
                    if source not in ports:
                        break
                else:
                    values = net.advance(rand=True)
                    # force into an iterable type
                    if type(values) == int:
                        values = [values]
                    for i in range(len(sources)):
                        sources[i].assign(values[i])
                # exit- we only want to ensure we progress toward one coverage
                break
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