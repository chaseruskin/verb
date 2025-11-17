from cocotb.types import LogicArray as Logics
from cocotb.types import Logic
from typing import List as _List

class Constant:

    def __init__(self):
        self.__value = 0
        pass

    @property
    def value(self):
        return self.__value

    def set_value(self, val: str, dtype: str):
        """
        Sets the constant's value
        """
        def starts_with_any(s: str, items: list):
            for item in items:
                if s.startswith(item):
                    return True
            return False

        dtype = dtype.lower()
        str_types = ['str', 'string']
        char_types = ['char', 'character']
        bool_types = ['bool', 'boolean']
        logic_types = ['std_logic', 'std_ulogic', 'logic', 'rlogic']

        strs_types = ['strs', 'strings']
        chars_types = ['chars', 'characters']
        bools_types = ['bools', 'booleans']
        logics_types = ['std_logic_vector', 'std_ulogic_vector', 'logics', 'rlogics']
        ints_types = ['i8s', 'i16s', 'i32s', 'u8s', 'u16s', 'u32s', 'p8s', 'p16s', 'p32s', 'isizes', 'usizes', 'psizes', 'ints', 'units', 'pints']
        # convert string
        if dtype in str_types:
            self.__value = from_vhdl_str(val)
        # convert scalar char
        elif dtype in char_types:
            self.__value = from_vhdl_char(val)
        # convert scalar bool
        elif dtype in bool_types:
            self.__value = from_vhdl_bool(val)
        # convert scalar logic
        elif dtype in logic_types:
            self.__value = from_vhdl_logic(val)
        # convert vector string
        elif starts_with_any(dtype, strs_types):
            self.__value = from_vhdl_strs(val)
        # convert vector char
        elif starts_with_any(dtype, chars_types):
            self.__value = from_vhdl_chars(val)
        # convert vector bool
        elif starts_with_any(dtype, bools_types):
            self.__value = from_vhdl_bools(val)
        # convert vector logic
        elif starts_with_any(dtype, logics_types):
            self.__value = from_vhdl_logics(val)
        # convert vector integer
        elif starts_with_any(dtype, ints_types):
            self.__value = from_vhdl_ints(val)
        # convert scalar integer
        else:
            self.__value = from_vhdl_int(val)


def from_vhdl_bool(s: str) -> bool:
    """
    Interprets a string `s` encoded as a vhdl boolean datatype and casts it
    to a Python `bool`.
    """
    return s.lower() == 'true'


def from_vhdl_int(s: str) -> int:
    """
    Interprets a string `s` encoded as a vhdl integer datatype and casts it
    to a Python `int`.
    """
    return int(s)


def from_vhdl_str(s: str) -> str:
    """
    Interprets a string `s` encoded as a vhdl string datatype and casts it
    to a Python `str`.
    """
    return str(s)


def from_vhdl_char(s: str) -> str:
    s = s.strip("'")
    return str(s)


def from_vhdl_logic(s: str) -> Logic:
    s = s.strip("'")
    return Logic(s)


def from_vhdl_logics(s: str) -> Logics:
    s = s.strip('"')
    return Logics(s)


def from_vhdl_ints(s: str) -> _List[int]:
    """
    Interprets an array of integers from vhdl into a list of `int` in Python.
    """
    return _from_vhdl_vec(s, fn=from_vhdl_int)


def from_vhdl_bools(s: str) -> _List[bool]:
    """
    Interprets an array of booleans from vhdl into a list of `bool` in Python.
    """
    return _from_vhdl_vec(s, fn=from_vhdl_bool)


def from_vhdl_strs(s: str) -> _List[str]:
    """
    Interprets an array of strings from vhdl into a list of `str` in Python.
    """
    return _from_vhdl_vec(s, fn=from_vhdl_str)


def from_vhdl_chars(s: str) -> _List[str]:
    return _from_vhdl_vec(s, fn=from_vhdl_char)


def _from_vhdl_vec(s: str, fn):
    """
    Generic implementation for casting a vector of a single datatype from VHDL
    to Python.
    """
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