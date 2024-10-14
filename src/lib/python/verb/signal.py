# Project: Verb
# Module: signal
#
# A Signal carries information.

from enum import Enum as _Enum

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
        '''
        If `weights` is set to None, then it is assumed to to be uniform distribution
        across the defined elements.

        If `partition` is set to true, it will divide up the total sample space `space`
        into evenly paritioned groups summing to the total number of provided weights.
        '''
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
        '''
        Produce a sample from the known distribution.
        '''
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

    def __init__(self, width: int=1, value=0, mode=Mode.INFER, endianness: str='big', name: str=None, signed: bool=False, distribution: Distribution=None):
        '''
        Creates a new Signal to carry the data `value` with a defined `width`.
        '''
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
        # store internal raw value
        self._raw_data = value

        self.value = None

        # set the signal's mode
        self._mode = mode if isinstance(mode, Mode) else Mode.from_str(str(mode))
        self._inferred_mode = None

        # specify the order of the bits (big-endian is MSB first)
        if str(endianness).lower() != 'big' and str(endianness).lower() != 'little':
            raise ValueError("expected endianness to be 'big' or 'little' but got " + str(endianness))
        self._is_big_endian = str(endianness).lower() == 'big'

        self._is_signed = bool(signed)

        # explicitly set the signal's name
        self._name = name

        if distribution != None:
            if isinstance(distribution, Distribution) == False and isinstance(distribution, list) == False:
                raise TypeError('expected distribution to be a Distribution or list but received type ' + str(type(distribution)))
        self._distro = distribution
        if type(self._distro) == list:
            self._distro = Distribution(space=[*self.span()], weights=distribution, partition=True)
            pass

        self.assign(value)
        pass

    def width(self) -> int:
        '''
        Accesses the number of allocated for this Signal.
        '''
        return self._width
    
    def dim(self) -> list:
        '''
        Returns the number of dimensions.
        '''
        return self._dimensions
    
    def set(self, value):
        '''
        Updates the Signal's internal data with `value`.

        The `value` can either be a `str`, `int`, or `list`.
        '''
        self.assign(value)
        pass

    def splice(self, index, value):
        '''
        Updates the current Signal's internal data with `value` at the given
        slice of its vector representation.
        '''
        from .primitives import bits as _bits

        if type(index) == tuple:
            index = [*index]
        if type(index) != tuple and type(index) != list:
            index = [index]
        dims = [*self._dimensions]

        cur_str = self.get(str)
        starting_i = 0
        next_w = self.width()
        for (a, (i, dim)) in enumerate(zip(index, dims)):
            if i < 0 or i >= dim:
                raise IndexError("expected index 'i' to be between 0 and " + str(dim) + ", but got " + str(i))
            next_w = 1 if a+1 >= len(dims) else dims[a+1]
            starting_i += i*next_w
            pass

        # convert this value to a string
        if type(value) == list or type(value) == int:
            value = _bits(value, width=next_w, trunc=True, endianness=self.endianness(), signed=self._is_signed)

        if len(value) > next_w:
            return ValueError("expected value 'value' to be between 1 and " + str(next_w) + " bits, but got " + str(len(value)))
        
        # fix the reversed order
        if self.endianness() == 'big':
            cur_str = cur_str[::-1]
            value = value[::-1]
        # modify here!
        new_val = cur_str[:starting_i] + value + cur_str[starting_i+next_w:]

        # bring the reversed order back
        if self.endianness() == 'big':
            new_val = new_val[::-1]
        # update the internal value
        self.set(new_val)
        pass

    def slice(self, index):
        '''
        Returns a new `Signal` object from the sub-slice of the current vector.
        '''
        if type(index) == tuple:
            index = [*index]
        if type(index) != tuple and type(index) != list:
            index = [index]
        dims = [*self._dimensions]

        sub = Signal(
            width=self.width(), 
            value=self.get(),
            endianness=self.endianness(),
            signed=self.signed(),
        )

        for (a, (i, dim)) in enumerate(zip(index, dims)):
            if i < 0 or i >= dim:
                raise IndexError("expected index 'i' to be between 0 and " + str(dim) + ", but got " + str(i))
            next_w = 1 if a+1 >= len(dims) else dims[a+1]

            sub_str = sub.get(str)
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
                endianness=self.endianness(),
                signed=self.signed(),
            )
            pass

        return sub

    def get(self, dtype=None):
        '''
        Retrieve the Signal's internal data.

        The `dtype` can either be `str`, `int`, or `list`.
        '''
        if dtype == int:
            return self.digits()
        elif dtype == str:
            return self.bits()
        elif dtype == list:
            return [int(b) for b in self.bits()]
        elif dtype == None:
            return self._raw_data
        else:
            raise TypeError

    def mode(self) -> Mode:
        '''
        Returns the port type for this Signal.
        '''
        return self._mode if self._inferred_mode == None else self._inferred_mode

    def min(self) -> int:
        '''
        Returns the minimum possible integer value stored in the allotted bits 
        (inclusive).
        '''
        from .primitives import pow2
        return 0 if self._is_signed == False else -pow2(self._width)
    
    def max(self) -> int:
        '''
        Returns the maximum possible integer value stored in the allotted bits
        (inclusive).
        '''
        from .primitives import pow2m1
        return pow2m1(self._width) if self._is_signed == False else pow2m1(self._width-1)
    
    def span(self) -> range:
        '''
        Returns the enumerated range of possible values for the Signal.
        
        The start is inclusive and the end is exclusive.
        '''
        return range(self.min(), self.max()+1)
    
    def endianness(self) -> str:
        return 'big' if self._is_big_endian == True else 'little'
    
    def signed(self) -> bool:
        '''
        Returns whether or not the Signal interprets its bits as signed or unsigned.
        Signed representations are formatted as two's complement.
        '''
        return self._is_signed
    
    def raw_data(self):
        '''
        Accesses the Signal's internal data in its raw representation.
        '''
        return self._raw_data

    def sample(self):
        '''
        Sets the data to a random value based on its distribution.

        If no distribution was defined for the Signal, it will use a uniform
        distribution across the possible allowed values.
        '''
        import random as _random

        # provide uniform distribution when no distribution is defined for the signal
        if self._distro == None:
            self.assign(_random.randint(self.min(), self.max()))
        else:
            self.assign(self._distro.samples(k=1)[0])
        # return the reference to self
        return self


    def assign(self, value):
        '''
        Updates the Signal's internal data with `value`.

        The `value` can either be a `str`, `int`, or `list`.
        '''
        from .primitives import digits as _digits
        # put into big-endian format for storing
        if (isinstance(value, str) or isinstance(value, list)) and self._is_big_endian == False:
            value = value[::-1]
        # verify the data is within bounds
        temp_int = _digits(value, self._is_signed)
        if temp_int < self.min() or temp_int > self.max():
            raise ValueError("value out of bounds " + str(temp_int) + " must be between " + str(self.min()) + " and " + str(self.max()))
        self._raw_data = value
        return self
    

    def __setattr__(self, name, value):
        if name == "value":
            if value != None:
                self.assign(value)
            if value == None:
                self._raw_data = 0
        else:
            self.__dict__[name] = value

    
    def bits(self) -> str:
        '''
        Accesses the Signal's internal data in its bit representation.
        '''
        from .primitives import bits as _bits
        return _bits(self._raw_data, width=self._width, trunc=True, endianness=self.endianness(), signed=self._is_signed)
        

    def digits(self) -> int:
        '''
        Accesses the Signal's internal data in its integer representation.
        '''
        from .primitives import digits as _digits
        return _digits(self._raw_data, signed=self._is_signed)


    def __getitem__(self, key: int) -> str:
        vec = self.bits()
        # reverse to count from 0 to width-1
        if self._is_big_endian == True:
            vec = vec[::-1]
        return vec[key]
    

    def __setitem__(self, key: int, value):
        new_val: str = '1' if int(value) == 1 else '0'
        vec = self.bits()
        # reverse to count from 0 to width-1
        if self._is_big_endian == True:
            vec = vec[::-1]
        result = ''

        for i, bit in enumerate(vec):
            if key == i:
                result += new_val
            else:
                result += bit
        # reverse back
        if self._is_big_endian == True:
            result = result[::-1]
        # update the raw data
        self.assign(result)
        pass
    

    def __str__(self):
        return self.bits()
    

    def __int__(self):
        return self.digits()
    
    pass