from cocotb.handle import SimHandleBase

from cocotb.types import LogicArray as Logics
from cocotb.types import Logic
import copy

from enum import Enum as _Enum

class Mode(_Enum):
    """
    The direction in which information travels.
    """
    
    IN  = 0
    """
    Assign the signal to be a receiver of information.
    """
    OUT = 1
    """
    Assign the signal to be a sender of information.
    """

    INOUT  = 2
    """
    Assign the signal to be both a receiver and sender of information.
    """

    LOCAL  = 3
    """
    Assign the signal to keep its information interal to its module.
    """
    
    # Allows interface data to decide what mode this signal is
    INFER = 4
    """
    Allow the library to infer the signal's direction based on any available
    information received about the signal from external sources.
    """

    @staticmethod
    def from_str(s: str):
        s = s.lower()
        if s == 'in' or s == 'i' or s == 'input':
            return Mode.IN
        elif s == 'out' or s == 'o' or s == 'output':
            return Mode.OUT
        elif s == 'inout' or s == 'io':
            return Mode.INOUT
        elif s == 'local' or s == 'l':
            return Mode.LOCAL
        else:
            raise Exception('failed to convert str '+s+' to type Mode')
    pass


class Dist:
    """
    Apply a distribution to a set of values defined within a space.
    """

    def __init__(self, space, weights=None, partition: bool=True):
        """
        If `weights` is set to None, then it is assumed to to be uniform distribution
        across the defined elements.

        If `partition` is set to true, it will divide up the total sample space `space`
        into evenly paritioned groups summing to the total number of provided weights.
        """
        import math as _math

        self._sample_space = space
        self._weights = weights
        # determine if to group the items together in divisible bins w/ weights weights[i]
        self._partition = partition
        self._events_per_weight = 1
        # re-group the items
        self._partitioned_space = self._sample_space
        # print(self._partition)
        if self._partition == True and type(self._weights) != type(None):
            self._partitioned_space = []
            self._events_per_weight = int(_math.ceil(len(self._sample_space) / len(weights)))
            # initialize the bins
            for i, element in enumerate(self._sample_space):
                # group the items together based on a common index that divides them into groups
                i_macro = int(i / self._events_per_weight)
                #print(i_macro)
                if len(self._partitioned_space) <= i_macro:
                    self._partitioned_space.append([])
                    pass
                self._partitioned_space[i_macro] += [element]
                pass
        pass

    def samples(self, k=1):
        """
        Produces a sample from the known distribution.
        """
        import random as _random

        outcomes = _random.choices(population=self._partitioned_space, weights=self._weights, k=k)
        results = []
        for event in outcomes:
            # unfold inner lists and ranges
            while type(event) == range or type(event) == list:
                event = _random.choice(event)
            results += [event]
        return results
    pass


class Signal:
    def __init__(self):
        self._handle: SimHandleBase = None
        self.value: Logic = Logic(0)
        self._dist = None
        self._width = None
        self._mode = None

    def mode(self) -> str:
        """
        Returns the mode of the port
        """
        return self._mode
    
    def width(self) -> int:
        """
        Returns the width of the signal.
        """
        if self._width is not None:
            return self._width
        try:
            rg = self.value.range
            self._width = 0
            for _ in rg.to_range():
                self._width += 1
        except:
            self._width = 1
        return self._width

    def min(self) -> int:
        """
        Returns the minimum unsigned integer value this signal can represent.
        """
        return 0
    
    def max(self) -> int:
        """
        Returns the maximum unsigned integer value this signal can represent.
        """
        return (2**self.width())-1

    def span(self) -> range:
        """
        Returns the enumerated range of possible values for the signal.
        
        The start is inclusive and the end is exclusive.
        """
        return range(self.min(), self.max()+1)

    def sample(self):
        """
        Sets the data to a random value based on its distribution.

        If no distribution was defined for the Signal, it will use a uniform
        distribution across the possible allowed values.
        """
        import random as _random
        # provide uniform distribution when no distribution is defined for the signal
        if self._dist == None:
            self.value = _random.randint(self.min(), self.max())
        else:
            self.value = self._dist.samples(k=1)[0]

    def set_handle(self, handle: SimHandleBase):
        """
        Sets the simulator object for this signal.
        """
        self._handle: SimHandleBase = handle
        if isinstance(self._handle.value, Logic):
            self.value: Logic = copy.deepcopy(self._handle.value)
        elif isinstance(self._handle.value, Logics):
            self.value: Logics = copy.deepcopy(self._handle.value)
        else:
            self.value = copy.deepcopy(self._handle.value)

    def get_handle(self) -> SimHandleBase:
        """
        Returns the simulator object linked to this signal, if one exists.
        """
        return self._handle   

    def __setattr__(self, name, value):
        if name == 'value' and self._handle is not None and self._mode == 'in':
            self._handle.value = value       
        super().__setattr__(name, value)

    def __int__(self) -> int:
        return int(self.value)
    
    def __str__(self) -> str:
        return str(self.value)