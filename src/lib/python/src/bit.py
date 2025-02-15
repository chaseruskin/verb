from typing import Union as _Union
from .model import Signal as _Signal

class bit:
    """
    Represent a value as its bit-level string representation.
    """

    def __init__(self, value: _Union[_Signal, int]):
        """
        Translate a `value` into it's bit-level string representation.
        """
        from .primitives import bits

        if isinstance(value, _Signal):
            self._integer = int(value)
            self._value: str = str(value)
        elif isinstance(value, int):
            self._integer = int(value)
            self._value = bits(value, signed=(value < 0))

    def length(self) -> int:
        """
        Return the number of bits being used to represent the value.
        """
        return len(self._value)

    def __len__(self) -> int:
        return len(self._value)
    
    def __str__(self) -> str:
        return self._value
    
    def __int__(self) -> int:
        return self._integer
    
    def __repr__(self) -> str:
        return self._value
    
    def __eq__(self, rhs) -> bool:
        import builtins
        if isinstance(rhs, str):
            return self._value == rhs
        elif isinstance(rhs, int):
            # handle positive numbers as true binary representations
            if rhs >= 0:
                bits = builtins.bin(rhs)[2:]
                # zero-extend left side
                for i in range(0, len(self._value)-len(bits)):
                    bits = '0' + bits
                return self._value == bits
            # handle negative numbers at their integer value
            else:
                return self._integer == rhs
        elif isinstance(rhs, _Signal):
            return self._value == str(rhs)
        
    def __bool__(self) -> bool:
        return self._integer != 0

    def __not__(self) -> bool:
        return self._integer == 0