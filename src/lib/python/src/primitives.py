import math as _math
from typing import Union as _Union
from .model import Signal as _Signal


def pow(base: int, exp: int):
    """
    Computes the followng formula: `base^exp`.
    """
    return base**exp


def pow2(width: int):
    """
    Computes the following formula: `2^(width)`.
    """
    return 2**width


def pow2m1(width: int):
    """
    Computes the following formula: `2^(width)-1`. 
    """
    return (2**width)-1


def is_pow2(n: int) -> bool:
    """
    Checks if `n` is a power of 2.
    """
    return _math.log2(n).is_integer()


def clog2(n: int) -> int:
    """
    Computes the following formula: `ceil(log2(n))`.
    """
    return int(_math.ceil(_math.log2(n)))


def flog2p1(n: int) -> int:
    """
    Computes the following formula: `floor(log2(n)+1))`.
    """
    return int(_math.floor(_math.log2(n) + 1))


def bits(data, width: int=None, trunc: bool=True, endianness: str='big', signed: bool=False) -> str:
    """
    Formats the `data` to its bit representation as a string.

    ### Parameters
    - `data`: integer number or list of 1s and 0s to transform
    - `width`: specify the number of bits (never truncates) 
    - `trunc`: force data into width bits even when data exceeds limit
    - `endianness`: 'big' stores MSB first (LHS) in the sequence, while 'little' stores LSB first
    - `signed`: set to `True` for 2's complement representation

    ### Returns
    - `str` of 1's and 0's
    """
    if str(endianness).lower() != 'big' and str(endianness).lower() != 'little':
        raise ValueError("expected endianness to be 'big' or 'little' but got " + str(endianness))
    is_big_endian = str(endianness).lower() == 'big'

    logic_vec = ''
    # handle vector of ints (1s and 0s)
    if isinstance(data, list) == True:
        for bit in data:
            if bool(bit) == True:
                logic_vec += '1'
            else:
                logic_vec += '0'
            pass
        if width is None:
            width = len(data)
    # handle pure integer values
    elif isinstance(data, int) == True:
        bin_str = bin(data)
        is_negative = bin_str[0] == '-'
        # auto-define a width
        if width == None:
            width = 1 if data == 0 else _math.ceil(_math.log(abs(data) + 0.5, 2))
            # extend to use negative MSB
            if is_negative == True:
                width += 1
        # compute 2's complement representation
        if is_negative == True:
            bin_str = bin(2**width + data)
        # assign to outer variable
        logic_vec = bin_str[2:]
        pass
    elif isinstance(data, str) == True:
        logic_vec = data
    else:
        raise TypeError("unable to handle converting type " + str(type(data)) + " into bit representation")
    
    # fill with zeros on the left depending on 'width' (never truncates)
    logic_vec = logic_vec.zfill(width)

    # truncate upper bits
    if trunc == True and width < len(logic_vec):
        logic_vec = logic_vec[len(logic_vec)-width:]

    # flip based on endianness
    if is_big_endian == False:
        logic_vec = logic_vec[::-1]

    return logic_vec


def digits(data, signed: bool=False) -> int:
    """
    Formats the `data` into its integer decimal representation.

    This function assumes the input to be in big-endian format (MSB is first in
    the sequence).
    
    ### Parameters
    - `data`: binary string to convert (example: '011101')
    - `signed`: apply two's complement when MSB = '1' during conversion

    ### Returns
    - `data` as integer form (decimal)
    """
    bits = ''
    if isinstance(data, int) == True:
        return data
    elif isinstance(data, list) == True:
        for b in data:
            if bool(b) == True:
                bits += '1'
            else:
                bits += '0'
            pass
    elif isinstance(data, str) == True:
        bits = data

    result = 0
    if signed == True and bits[0] == '1':
        # flip all bits
        flipped = ''
        for b in bits: flipped += str(int(b, base=2) ^ 1)
        result = (int('0b'+flipped, base=2)+1) * -1
    else:
        result = int('0b'+bits, base=2)

    return result


def bin(s: _Union[_Signal, int]):
    """
    Return the binary representation of an integer.

    This function will return the binary representation of a `Signal` if `s`
    is the corresponding type, otherwise it will call the builtin `bin()`
    function.
    """
    import builtins
    if isinstance(s, _Signal):
        return '0b' + s.bits()
    else:
        return builtins.bin(s)
    

