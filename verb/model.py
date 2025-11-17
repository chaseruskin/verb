import cocotb
from abc import ABC
import json
import os
from typing import List as _List

from .signal import Signal
from .signal import Mode
from .constant import Constant

from enum import Enum as _Enum

class Strategy(_Enum):
    """
    Method for constrained randomization.
    """
    NONE = 0,
    LINEAR = 1,
    UNIFORM = 2,
    WEIGHTS = 3,

    @staticmethod
    def from_str(s: str):
        s = s.lower()
        if s == 'none':
            return Strategy.NONE
        elif s == 'linear':
            return Strategy.LINEAR
        elif s == 'uniform':
            return Strategy.UNIFORM
        elif s == 'weights':
            return Strategy.WEIGHTS
        else:
            raise Exception('Failed to convert str '+s+' to class `Strategy`')
    pass


class Model(ABC):

    def mirror(self):
        """
        Links signal objects to their simulation handles.

        This method should be called after all signal objects have been created within a model's
        `__init__` method.
        """
        mdl_attrs = dir(self)
        top_sim_attrs = dir(cocotb.top)

        dut_json = dict()
        generics = []
        try:
            dut_json = json.loads(os.environ['VERB_DUT_JSON'])
            generics = [g['identifier'] for g in dut_json['generics']]
        except:
            pass

        for attr_name in mdl_attrs:
            mdl_attr = getattr(self, attr_name)
            # link the simulation handle to the signal object
            if isinstance(mdl_attr, Signal) and attr_name in top_sim_attrs:
                mdl_attr.set_handle(getattr(cocotb.top, attr_name))
            # use the json data to extract a type and it's constant value since unreliable for some simulators
            if isinstance(mdl_attr, Constant) and attr_name in generics:
                dut_gen = dut_json['generics'][generics.index(attr_name)]
                mdl_attr.set_value(dut_gen['default'], dut_gen['type'])
            # get the DUT information from environment variable to identify port directions
            try:
                for port in dut_json['ports']:
                    port_name = port['identifier']
                    if port_name == attr_name:
                        mdl_attr._mode = port['mode']
            except:
                pass

    def randomize(self, strategy: str="weights"):
        """
        Assign random input values to each `Signal` attribute of the model instance that is
        a known input port.

        After this function is called, all the known input ports under the `model`
        instance will have a random value according to the `strategy`. Calling this
        function allows the user to leverage constrained randomization and coverage-driven
        test generation to avoid having to individually set each input port.

        ### Parameters
        - `model`: mutable reference to an instance that has attributes of known input ports
        - `strategy`: specify how to constrain the random input generation

        This function mutates the object `model` and returns a reference to the same object.

        A strategy can be provided to provide coverage-driven input test vectors. The following
        strategies are currently available:
        - "none": use the default distributions for each input
        - "linear": iterate through the list of coverage nets and draw the next value to help close the first failing coverage net
        - "uniform": sample a failing coverage net at random using uniform distribution and draw the next value to help close its coverage
        - "weights": sample a coverage net to advance according to its normalized weighted distribution of its distance from its goal
        """
        from .coverage import Coverage
        from .coverage.net import CoverageNet
        from .signal import Signal, Mode
        import random

        net: CoverageNet
        port: Signal

        strat: Strategy = Strategy.from_str(strategy)

        ports = [p[1] for p in _extract_ports(self, mode=Mode.IN)]

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
        elif strat == Strategy.UNIFORM:
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
                sel: CoverageNet = random.choice(candidates)
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

    def cover(self):
        """
        Schedules a coroutine to run while the testcase is running to monitor when
        coverage nets are hit.

        This method should be called after all coverage nets have been created for a
        model.
        """
        cocotb.start_soon(_monitor_coverage(self), name='cover')

    def get_inputs(self) -> _List[Signal]:
        """
        Returns the list of Signals that were detected as input ports for the design
        under test.
        """
        from .signal import Mode
        result = [p[1] for p in _extract_ports(self, mode=Mode.IN)]
        return result
    
    def get_outputs(self) -> _List[Signal]:
        """
        Returns the list of Signals that were detected as output ports for the design
        under test.
        """
        from .signal import Mode
        result = [p[1] for p in _extract_ports(self, mode=Mode.OUT)]
        return result


def _extract_ports(model, mode: Mode=None):
    """
    Collects the attributes defined in the `model` into a list storing
    the tuples of their (name, signal).

    If `mode` is None, then collects all signals.
    """
    results = []
    attr_names = dir(model)
    for attr_name in attr_names:
        if isinstance(getattr(model, attr_name), Signal) == True:
            mdl_signal: Signal = getattr(model, attr_name)
            # verify it matches the port direction
            if mode is None or Mode.from_str(mdl_signal.mode()) == mode:
                # store tuple with (name, signal)
                results += [(attr_name, mdl_signal)]
        pass
    results.sort()
    # return the list of ports
    return results


async def _monitor_coverage(model):
    from .testbench import falling_edge
    from .coverage import Coverage
    from .coverage.net import CoverageNet
    from .signal import Signal

    all_signals = [p[1] for p in _extract_ports(model, mode=None)]

    net: CoverageNet
    while True:
        # check if there are coverages to automatically update
        for net in Coverage.get_nets():
            if net.has_sink() == True:
                # verify the observation involves only signals being written for this transaction
                sinks = net.get_sink_list()
                # allow the first sink to have priority on check
                pri_sink = sinks[0]
                # perform an observation if the priority sink belongs to this model
                if type(pri_sink) == Signal and pri_sink in all_signals:
                    try:
                        net.check(net.get_sink())
                    except ValueError:
                        pass
        await falling_edge()
