# Project: Verb
# Test: signal.py
#
# Verifies behavior for the Signal class.

import unittest as ut
from ..src.signal import *
from ..src.bit import bit

class Test(ut.TestCase):

    def test_signal_internal_data(self):
        d0 = Signal(4, signed=True)
        d0.set(5)
        self.assertEqual(d0._width, 4)
        self.assertEqual(d0.bits(), '0101')
        self.assertEqual(int(d0), 5)
        d0[1] = 1
        self.assertEqual(int(d0), 7)
        self.assertEqual(d0.bits(), '0111')
        pass


    def test_signal_get_set(self):
        d = Signal(4)
        d.set(2)
        self.assertEqual(d.get(), 2)
        self.assertEqual(d.get(), bit('0010'))
        self.assertEqual(list(d), [0, 0, 1, 0])
        self.assertEqual(int(d), 2)

        d.set('1101')
        self.assertEqual(d.get(), 0b1101)
        self.assertEqual(str(d), '1101')
        self.assertEqual(list(d), [1, 1, 0, 1])
        self.assertEqual(int(d), 13)
        self.assertEqual(d.dim(), (4,))
        self.assertEqual(d.dim()[0], 4)
        pass


    def test_2d_signal_get(self):
        d = Signal((4, 2), value='11100100')
        self.assertEqual(d.width(), 8)
        self.assertEqual(d.dim(), (4, 2))
        self.assertEqual(d.slice(1), bit('01'))
        self.assertEqual(d.slice(2), bit('10'))
        self.assertEqual(d.slice((2, 1)), bit('1'))
        self.assertEqual(d.slice((2, 0)), bit('0'))
        pass


    def test_2d_signal_set(self):
        d = Signal((4, 2), value='00000000')
        self.assertEqual(d.width(), 8)
        self.assertEqual(d.dim(), (4, 2))

        d.splice(1, '01')
        self.assertEqual(d.get(), bit('00000100'))
        d.splice(2, '10')
        self.assertEqual(d.get(), bit('00100100'))
        d.splice(3, '11')
        self.assertEqual(d.get(), bit('11100100'))
        d.splice(0, '00')
        self.assertEqual(d.get(), bit('11100100'))

        d.splice((2, 1), '0')
        self.assertEqual(d.get(), bit('11000100'))
        d.splice((2, 0), 1)
        self.assertEqual(d.get(), bit('11010100'))
        pass

    
    def test_operators(self):
        # negation
        d = Signal(4, 0b0110)
        e = ~d
        self.assertEqual(e.get(), bit('0b1001'))
        self.assertEqual(d.get(), bit('0b0110'))
        # or 
        f = d | 0b1001
        self.assertEqual(int(f), 0b1111)
        self.assertEqual(int(d), 0b0110)
        # and
        g = d & e
        self.assertEqual(int(g), 0b0000)
        self.assertEqual(int(d), 0b0110)

        # left shift
        h = Signal(8, 0b0010_1000)
        i = h << 2
        self.assertEqual(int(i), 0b1010_0000)
        i = h << 3
        self.assertEqual(int(i), 0b010_00000)

        # right shift (take sign into account)
        h = Signal(4, 0b0110)
        i = h >> 2
        self.assertEqual(int(i), 0b0001)
        h = Signal(4, 0b1100, signed=0)
        i = h >> 2
        self.assertEqual(bit(i), 0b0011)

        h = Signal(4, 0b1100, signed=1)
        i = h >> 2
        self.assertEqual(bit(i), 0b1111)


    def test_value_assignment(self):
        g = Signal(4)
        g.set(0b011)
        # g.value = 0b011
        self.assertEqual(int(g), 3)

    pass