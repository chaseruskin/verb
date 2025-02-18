import unittest as ut
from ..src.bit import bit

class Test(ut.TestCase):

    def test_basic(self):
        b = bit(-1, 4)
        self.assertEqual(b.bin, '0b1111')
        self.assertEqual(b.uint, 15)
        self.assertEqual(b.int, -1)
        self.assertEqual(b.width, 4)

        b = bit(0b101, 3)
        self.assertEqual(b.bin, '0b101')
        self.assertEqual(b.uint, 5)
        self.assertEqual(b.int, -3)
        self.assertEqual(b.width, 3)

        b = bit('0b1001', 4)
        self.assertEqual(b.uint, 9)
        self.assertEqual(b.width, 4)
        self.assertEqual(b.bin, '0b1001')
        self.assertEqual(b.int, -7)

        b = bit('0x4', 4)
        self.assertEqual(b.uint, 4)
        self.assertEqual(b.width, 4)
        self.assertEqual(b.bin, '0b0100')
        self.assertEqual(b.int, 4)

        b = bit('0b01011', 3)
        self.assertEqual(b.uint, 3)
        self.assertEqual(b.width, 3)
        self.assertEqual(b.bin, '0b011')
        self.assertEqual(b.int, 3)

        b = bit(0b101, 4)
        self.assertEqual(b.bin, '0b0101')
        self.assertEqual(b.uint, 5)
        self.assertEqual(b.int, 5)
        self.assertEqual(b.width, 4)
        self.assertEqual(b[0], '1')
        self.assertEqual(b[1], '0')

        b[0] = '0'
        self.assertEqual(b[0], '0')
        self.assertEqual(b.int, 4)
        self.assertEqual(b.uint, 4)
        self.assertEqual(b.bin, '0b0100')\

        self.assertEqual(b[:][::-1], '0100')
        self.assertEqual(b[:2], '00')
        self.assertEqual(b[:3][::-1], '100')

        b = bit('0110')
        self.assertEqual(b.bin, '0b0110')
        self.assertEqual(b.width, 4)
        self.assertEqual(b.int, 6)
        self.assertEqual(b.uint, 6)


        c = bit(b)
        self.assertEqual(c.int, b.int)

        c = bit(True, 4)
        self.assertEqual(c.int, 1)
        self.assertEqual(c.bin, '0b0001')

        c = bit(True)
        self.assertEqual(c.uint, 1)
        self.assertEqual(c.bin, '0b1')
        pass

    def test_ops(self):
        a = bit('1010')
        a |= 0b1111
        self.assertEqual(a, bit('1111'))

        a = bit('1010')
        a &= 0b0010
        self.assertEqual(a, bit('0010'))

        a = bit('1010')
        a = a >> 2
        self.assertEqual(a, 0b0010)

        a = bit('0011')
        a = a << 3
        self.assertEqual(a, 0b1000)

        a = bit('0101')
        a = a << 1
        self.assertEqual(a, 0b1010)

    def test_bin(self):
        a = bit('1010')
        self.assertEqual(bin(a), '0b1010')

        b = bit(-2, 6)
        self.assertEqual(bin(b), '0b111110')

    def test_iter(self):
        # iterating goes from LSB (index 0) to MSB (greatest index)
        a = bit('00101', endian='big')
        self.assertEqual(list(a), [1, 0, 1, 0, 0])

        a = bit('00101', endian='little')
        self.assertEqual(list(a), [0, 0, 1, 0, 1])

        a = bit(1, width=4, endian='little')
        self.assertEqual(a.bin, '0b1000')
        self.assertEqual(list(a), [1, 0, 0, 0])

        result = [1, 0, 0, 0]
        for (i, b) in enumerate(a):
            self.assertEqual(b, result[i])

