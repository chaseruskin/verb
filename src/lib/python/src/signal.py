# Project: Verb
# Module: signal
#
# A Signal carries information.

from enum import Enum as _Enum
from typing import Union as _Union
import copy as _copy
from .bit import bit as _bit
import builtins as _builtins

class Mode(_Enum):
    IN  = 0
    OUT = 1
    INOUT  = 2
    LOCAL  = 3
    # Allows interface data to decide what mode this signal is
    INFER = 4

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


class Distribution:

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
        Produce a sample from the known distribution.
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
    """
    A carrier of information that represents data by taking on, at most, one of a
    finite number of values at any given time.
    """

    def __init__(
            self, 
            width: int=1, 
            value=0, 
            mode=Mode.INFER, 
            signed: bool=False, 
            endian: str='big', 
            dist: Distribution=None, 
            name: str=None
        ):
        """
        Creates a instance of a `Signal` to carry data.

        ### Parameters
        - `width`: number of bits to represent the signal
        - `value`: initial value to assign as the data
        - `mode`: how the signal should be used within a model
        - `endian`: specify if the leftmost bit is MSb ('big') or LSb ('little')
        - `name`: the explicit name of the signal
        - `signed`: decide if to interpret bits in 2's complement
        - `dist`: specify the signal's distribution for random sampling

        If `mode` is set to `INFER`, then the signal has its mode decided based
        on if the the name of the instance is a known port. For matching ports it
        may be `IN`, `OUT`, or `INOUT`. If no matching port is found for this signal,
        then the mode is set to `LOCAL`.

        To override associating the actual variable name of this instance with the name used for port lookup, provide
        a value for the `name` parameter.

        When `dist` is set to `None`, then the signal will take on a uniform distribution
        during random sampling. See `Distribution` class for how to specify a distribution.
        """
        # set the number of bits allowed for the signal
        self._dimensions = (width, )
        if isinstance(width, list) == True or isinstance(width, tuple) == True:
            total = 1
            self._dimensions = tuple(width)
            for d in width:
                if isinstance(d, int) == False:
                    raise TypeError('expected width to be an integer but received type ' + str(type(d)))
                total = total * d
            width = int(total)
            pass
        
        if isinstance(width, int) == False:
            raise TypeError('expected width to be an integer but received type ' + str(type(width)))
        if width < 0:
            raise ValueError('expected width to be a positive number but got ' + str(width))
        
        self._width = int(width)

        # set the signal's mode
        self._mode = mode if isinstance(mode, Mode) else Mode.from_str(str(mode))
        self._inferred_mode = None

        # specify the order of the bits (big-endian is MSB first)
        if str(endian).lower() != 'big' and str(endian).lower() != 'little':
            raise ValueError("expected endianness to be 'big' or 'little' but got " + str(endian))
        self._is_big_endian = str(endian).lower() == 'big'

        self._is_signed = bool(signed)

        # ensure proper sign extension when going into bit if not given as an integer
        if self._is_signed and not isinstance(value, int):
            value = _bit(value, endian=endian).int
        # store the bit-level representation of the data
        self._data = _bit(value, width=self._width, endian=endian)

        # explicitly set the signal's name
        self._name = name

        if dist != None:
            if isinstance(dist, Distribution) == False and isinstance(dist, list) == False:
                raise TypeError('expected distribution to be a Distribution or list but received type ' + str(type(dist)))
        self._distro = dist
        if type(self._distro) == list:
            self._distro = Distribution(space=[*self.span()], weights=dist, partition=True)
            pass
        pass

    def width(self) -> int:
        """
        Return the number of bits required to represent this signal.
        """
        return self._width
    
    def dim(self) -> list:
        """
        Returns the number of dimensions.
        """
        return self._dimensions
    
    def set(self, value):
        """
        Assigns this signal's data with `value`.
        """
        if isinstance(value, Signal):
            if value.width() != self.width():
                raise Exception("cannot assign data from signal of mismatched width")
            if value.endianness() != self.endianness():
                raise Exception("cannot assign data from signal of mismatched endianness")
            value = value._data
        # update the data
        self._data = _bit(value, self.width(), self.endianness())
        pass

    def get(self) -> _bit:
        """
        Return the interal bit-level representation of the data.
        """
        return self._data

    def splice(self, key, value):
        """
        Updates the current Signal's internal data with `value` at the given
        slice of its vector representation.
        """
        if type(key) == tuple:
            key = [*key]
        if type(key) != tuple and type(key) != list:
            key = [key]
        dims = [*self._dimensions]

        cur_str = str(self._data)
        starting_i = 0
        next_w = self.width()
        for (a, (i, dim)) in enumerate(zip(key, dims)):
            if i < 0 or i >= dim:
                raise IndexError("expected index 'i' to be between 0 and " + str(dim) + ", but got " + str(i))
            next_w = 1 if a+1 >= len(dims) else dims[a+1]
            starting_i += i*next_w
            pass

        # convert this value to bit-level
        if type(value) == list or type(value) == int:
            value = str(_bit(value, next_w, endian=self.endianness()))

        if len(value) > next_w:
            return ValueError("expected value 'value' to be between 1 and " + str(next_w) + " bits, but got " + str(len(value)))
        
        # fix the reversed order
        if self._is_big_endian:
            cur_str = cur_str[::-1]
            value = value[::-1]

        # modify here!
        new_val = cur_str[:starting_i] + value + cur_str[starting_i+next_w:]

        # bring the reversed order back
        if self._is_big_endian:
            new_val = new_val[::-1]
        # update the internal value
        self.set(new_val)
        pass

    def slice(self, key) -> _bit:
        """
        Returns a new instance of the bit-level representation that encompasses the
        subset sliced from the original data.
        """
        if type(key) == tuple:
            key = [*key]
        if type(key) != tuple and type(key) != list:
            key = [key]
        dims = [*self._dimensions]

        sub = Signal(
            width=self.width(), 
            value=self.get(),
            endian=self.endianness(),
            signed=self.signed(),
        )

        for (a, (i, dim)) in enumerate(zip(key, dims)):
            if i < 0 or i >= dim:
                raise IndexError("expected index 'i' to be between 0 and " + str(dim) + ", but got " + str(i))
            next_w = 1 if a+1 >= len(dims) else dims[a+1]

            sub_str = str(sub._data)
            next_v = ''
            # get away from the reversed order
            if self.endianness() == 'big':
                sub_str = sub_str[::-1]
            for j in range(0, next_w):
                next_v += sub_str[(i*next_w)+j]
            # flip back to the endianness
            if self.endianness() == 'big':
                next_v = next_v[::-1]

            sub = Signal(
                width=next_w, 
                value=next_v,
                endian=self.endianness(),
                signed=self.signed(),
            )
            pass

        return sub._data

    def get(self) -> _bit:
        """
        Return access to the signal's internal data.
        """
        return self._data
    
    def bits(self) -> str:
        """
        Return the bit-level string representation of the data.
        """
        return str(self._data)

    def mode(self) -> Mode:
        """
        Returns the port type for this signal.
        """
        return self._mode if self._inferred_mode == None else self._inferred_mode

    def min(self) -> _builtins.int:
        """
        Returns the minimum possible integer value stored in the allotted bits 
        (inclusive).
        """
        from . import pow2
        return 0 if self._is_signed == False else -pow2(self._width)
    
    def max(self) -> _builtins.int:
        """
        Returns the maximum possible integer value stored in the allotted bits
        (inclusive).
        """
        from . import pow2m1
        return pow2m1(self._width) if self._is_signed == False else pow2m1(self._width-1)
    
    def span(self) -> range:
        """
        Returns the enumerated range of possible values for the signal.
        
        The start is inclusive and the end is exclusive.
        """
        return range(self.min(), self.max()+1)
    
    def endianness(self) -> str:
        """
        Return the endianness of the signal ("big" or "little").
        """
        return 'big' if self._is_big_endian == True else 'little'
    
    def signed(self) -> _builtins.bool:
        """
        Returns whether or not the signal interprets its bits as signed or unsigned.
        Signed representations are formatted as two's complement.
        """
        return self._is_signed

    def sample(self):
        """
        Sets the data to a random value based on its distribution.

        If no distribution was defined for the Signal, it will use a uniform
        distribution across the possible allowed values.
        """
        import random as _random

        # provide uniform distribution when no distribution is defined for the signal
        if self._distro == None:
            self.set(_random.randint(self.min(), self.max()))
        else:
            self.set(self._distro.samples(k=1)[0])

    def __getitem__(self, key: int) -> str:
        return self._data[key]
    
    def __setitem__(self, key: int, value):
        self._data[key] = value

    def __index__(self) -> int:
        return self._data.uint

    def __str__(self):
        return str(self._data)
    
    def __int__(self):
        if self._is_signed:
            return int(self._data.int)
        else:
            return int(self._data.uint)
        
    def __add__(self, rhs):
        return int(self) + int(rhs)

    def __radd__(self, lhs):
        return int(lhs) + int(self)

    def __iadd__(self, rhs):
        temp = int(self) + int(rhs)
        self.set(temp)
        return self

    def __iter__(self):
        return iter([int(i) for i in str(self._data)])

    def __len__(self):
        return self._width
    
    def __bool__(self):
        return _builtins.bool(self._data)

    def __not__(self):
        return not _builtins.bool(self._data)
    
    def __invert__(self):
        cp = _copy.deepcopy(self)
        cp._data = ~cp._data
        return cp
    
    def __or__(self, rhs):
        cp = _copy.deepcopy(self)
        if isinstance(rhs, Signal):
            rhs = rhs._data
        cp._data = _bit(cp._data | rhs)
        return cp
    
    def __and__(self, rhs):
        cp = _copy.deepcopy(self)
        if isinstance(rhs, Signal):
            rhs = rhs._data
        cp.set(cp._data & rhs)
        return cp
    
    def __xor__(self, rhs):
        cp = _copy.deepcopy(self)
        if isinstance(rhs, Signal):
            rhs = rhs._data
        cp._data = cp._data ^ rhs
        return cp
    
    def __lshift__(self, rhs):
        cp = _copy.deepcopy(self)
        if isinstance(rhs, Signal):
            rhs = rhs._data.uint
        cp._data = cp._data << rhs
        return cp
    
    def __rshift__(self, rhs):
        cp = _copy.deepcopy(self)
        if isinstance(rhs, Signal):
            rhs = rhs._data.uint
        if self._is_signed:
            cp.set(cp._data.int >> rhs)
        else:
            cp.set(cp._data.uint >> rhs)
        return cp
    
    # def assign(self, value):
    #     """
    #     Updates the Signal's internal data with `value`.

    #     The `value` can either be a `Signal`, `bool`, `str`, `int`, or `list`.
    #     """
    #     from .primitives import digits as _digits
    #     from .bit import bit as _bit

    #     # put into big-endian format for storing
    #     if (isinstance(value, str) or isinstance(value, list)) and self._is_big_endian == False:
    #         value = value[::-1]
    #     # convert to int if a boolean
    #     if isinstance(value, bool):
    #         if value:
    #             value = 1
    #         else:
    #             value = 0
    #     # get integer value from signal
    #     if isinstance(value, Signal):
    #         value = int(value)
    #     # verify the data is within bounds
    #     temp_int = _digits(value, self._is_signed)
    #     if temp_int < self.min() or temp_int > self.max():
    #         if temp_int >= 0 and temp_int < 2**self.width():
    #             value = str(_bit(temp_int))
    #         else:
    #             raise ValueError("value out of bounds " + str(temp_int) + " must be between " + str(self.min()) + " and " + str(self.max()))
    #     self._raw_data = value
    #     return self
    
    pass


