class bit:
    """
    Represent a value as its bit-level string representation.
    """

    def __init__(self, value, width: int=None, endian: str='big'):
        """
        Translate a `value` into it's bit-level string representation.
        """
        from .model import Signal as _Signal

        if isinstance(value, _Signal):
            value = value._data

        if isinstance(value, bit):
            self.uint = value.uint
            self.int = value.int
            self.bin = value.bin
            self.width = value.width
            self.endian = value.endian
            value = self.bin
        
        self.uint = None
        self.int = None
        self.bin = None
        self.width = width
        self.endian = endian.lower()


        # convert list into str
        if isinstance(value, list):
            value = "".join([str(x) for x in value])

        # convert bool into an int
        if isinstance(value, bool):
            value = int(value)

        # handle integer types
        if isinstance(value, int):
            # store the integer value (with sign)
            self.int = value

            if value < 0 and width == None:
                raise Exception("a width is required for negative integers")
            
            if value < 0:
                # get magnitude
                mag = abs(value)
                # invert all bits
                bits = bin(mag)[2:].replace('1', 'x').replace('0', '1').replace('x', '0')
                # sign extend to fit width
                bits = "".join(['1' * (width-len(bits))]) + bits
                # turn into unsigned number (+1) for 2's comp form
                self.uint = int('0b'+bits, base=2) + 1
            else:
                # take as unsigned number
                self.uint = value
                # determine (signed) integer representation

            self.bin = bin(self.uint)
 
            # auto-determine the width
            if self.width == None:
                self.width = len(self.bin[2:])

        # handle string types (hex, oct, bin)
        elif isinstance(value, str):
            # don't allow - prefix
            if value.startswith('-'):
                raise Exception("negative values is not supported for string representations")
            # assume binary if no prefix found
            if not value.lower().startswith('0b') and not value.lower().startswith('0x') and not value.lower().startswith('0o'):
                value = '0b' + value
            # make sure width is not explicitly set
            if self.width == None:
                if value.lower().startswith('0b'):
                    self.width = len(value[2:])
                if value.lower().startswith('0x'):
                    self.width = len(value[2:]) * 4
                if value.lower().startswith('0o'):
                    self.width = len(value[2:]) * 3
            # interpret from the prefix
            self.bin = bin(int(value, base=0))
            pass

        # fit to the width
        self.bin = '0b' + self.bin[2:].zfill(self.width)
        if len(self.bin[2:]) > self.width:
            self.bin = '0b' + self.bin[::-1][:self.width][::-1]

        # reverse the binary string if storing in little endian
        if self.endian == 'little':
            self.bin = '0b' + self.bin[2:][::-1]

        # sync with correct int and uint values
        self.update(self.bin)


    def update(self, bits: str):
        """
        Internally updates the integer values from the binary representation.

        Assumes that `bits` uses the '0b' prefix.
        """
        binary = bits[2:]
        if self.endian == 'little':
            binary = binary[::-1]

        if bits.lower().startswith('0b') == False:
            raise Exception('input must start with the \'0b\' prefix')
        
        if len(bits[2:]) != self.width:
            raise Exception('input must have same width as already defined')

        self.bin = bits
        
        # get new unit
        self.uint = int(binary, base=2)

        # compute the 2's complement
        self.int = (-1) * 2**(self.width-1) * int(binary[0])
        for (i, b) in enumerate(binary[1:]):
            self.int += 2**(self.width-2-i) * int(b)
    
    def length(self) -> int:
        """
        Return the number of bits being used to represent the value.
        """
        return len(self.width)

    def __len__(self) -> int:
        return self.width
    
    def __str__(self) -> str:
        return self.bin[2:]
        
    def __bool__(self) -> bool:
        return self.uint != 0

    def __not__(self) -> bool:
        return self.uint == 0
    
    def __index__(self) -> int:
        return self.uint
    
    def __eq__(self, rhs) -> bool:
        if not isinstance(rhs, bit):
            rhs = bit(rhs, self.width)
        return self.bin == rhs.bin

    def __getitem__(self, key: int) -> str:
        # if little, go from left to right
        bits = self.bin[2:]
        if self.endian == 'big':
            bits = self.bin[2:][::-1]
        return str(bits[key])
    
    def __setitem__(self, key: int, value):
        value = int(value)
        if value != 1 and value != 0:
            raise Exception('\'bit\' object only supports 1 or 0 for item assignment')
        bits = self.bin[2:]
        if self.endian == 'big':
            bits = self.bin[2:][::-1]
        bits = bits[:key] + str(value) + bits[key+1:]
        # reverse back to correct form
        if self.endian == 'big':
            bits = bits[::-1]
        # update bin and other values
        self.bin = '0b' + bits
        self.update(self.bin)

    def __invert__(self):
        from copy import copy as _copy
        cp = _copy(self)
        bits = str(cp)
        inv = ''
        for b in bits:
            if b == '1': inv += '0'
            if b == '0': inv += '1'
        cp.update('0b'+inv)
        return cp
    
    def __or__(self, rhs):
        from copy import copy as _copy
        if isinstance(rhs, bit) and rhs.width != self.width:
            raise Exception('bitwise operation requires matching widths')
        else:
            if bit(rhs).width > self.width:
                raise Exception('right-hand-side value requires a width larger than left-hand-side')
            rhs = bit(rhs, self.width, self.endian)
        cp = _copy(self)
        uint = cp.uint | rhs.uint
        bits = '0b' + bin(uint)[2:].zfill(self.width)
        cp.update(bits)
        return cp
    
    def __and__(self, rhs):
        from copy import copy as _copy
        if isinstance(rhs, bit) and rhs.width != self.width:
            raise Exception('bitwise operation requires matching widths')
        else:
            if bit(rhs).width > self.width:
                raise Exception('right-hand-side value requires a width larger than left-hand-side')
            rhs = bit(rhs, self.width, self.endian)
        cp = _copy(self)
        uint = cp.uint & rhs.uint
        bits = '0b' + bin(uint)[2:].zfill(self.width)
        cp.update(bits)
        return cp
    
    def __xor__(self, rhs):
        from copy import copy as _copy
        if isinstance(rhs, bit) and rhs.width != self.width:
            raise Exception('bitwise operation requires matching widths')
        else:
            if bit(rhs).width > self.width:
                raise Exception('right-hand-side value requires a width larger than left-hand-side')
            rhs = bit(rhs, self.width, self.endian)
        cp = _copy(self)
        uint = cp.uint ^ rhs.uint
        bits = '0b' + bin(uint)[2:].zfill(self.width)
        cp.update(bits)
        return cp
    
    def __lshift__(self, rhs):
        from copy import copy as _copy
        cp = _copy(self)
        rhs = bit(rhs)
        uint = cp.uint << rhs.uint
        bits = bin(uint)[2:]
        bits = bits[len(bits)-self.width:]
        bits = '0b' + bits.zfill(self.width)
        cp.update(bits)
        return cp
    
    def __rshift__(self, rhs):
        from copy import copy as _copy
        cp = _copy(self)
        rhs = bit(rhs)
        uint = cp.uint >> rhs.uint
        bits = '0b' + bin(uint)[2:].zfill(self.width)
        cp.update(bits)
        return cp
