from typing import List as _List


def from_vhdl_bool(s: str) -> bool:
    '''
    Interprets a string `s` encoded as a vhdl boolean datatype and casts it
    to a Python `bool`.
    '''
    return s.lower() == 'true'


def from_vhdl_int(s: str) -> int:
    '''
    Interprets a string `s` encoded as a vhdl integer datatype and casts it
    to a Python `int`.
    '''
    return int(s)


def from_vhdl_str(s: str) -> str:
    '''
    Interprets a string `s` encoded as a vhdl string datatype and casts it
    to a Python `str`.
    '''
    return str(s)


def from_vhdl_ints(s: str) -> _List[int]:
    '''
    Interprets an array of integers from vhdl into a list of `int` in Python.
    '''
    return _from_vhdl_vec(s, fn=from_vhdl_int)


def from_vhdl_bools(s: str) -> _List[bool]:
    '''
    Interprets an array of booleans from vhdl into a list of `bool` in Python.
    '''
    return _from_vhdl_vec(s, fn=from_vhdl_bool)


def from_vhdl_strs(s: str) -> _List[str]:
    '''
    Interprets an array of strings from vhdl into a list of `str` in Python.
    '''
    return _from_vhdl_vec(s, fn=from_vhdl_str)


def _from_vhdl_vec(s: str, fn):
    '''
    Generic implementation for casting a vector of a single datatype from VHDL
    to Python.
    '''
    # remove the leading and closing brackets
    inner = s[1:len(s)-1]
    # split on the comma
    elements = inner.split(',')
    result = [0] * len(elements)
    # cast each element to an int
    for i, x in enumerate(elements):
        # handle positional assignment
        if x.count('=>') > 0:
            sub_x = x.split('=>', 2)
            result[int(sub_x[0])] = fn(sub_x[1])
        else:
            result[i] = int(x)
        pass
    return result 
