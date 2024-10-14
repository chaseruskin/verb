# Project: Verb
# Test: signal.py
#
# Verifies behavior for the Signal class.

import unittest as ut
from ..verb.signal import *

class Test(ut.TestCase):

    def test_signal_internal_data(self):
        d0 = Signal(4, signed=True)
        d0.assign(5)
        self.assertEqual(d0._width, 4)
        self.assertEqual(d0.bits(), '0101')
        self.assertEqual(d0.digits(), 5)
        self.assertEqual(d0.raw_data(), 5)
        d0[1] = 1
        self.assertEqual(d0.digits(), 7)
        self.assertEqual(d0.bits(), '0111')
        pass


    def test_signal_get_set(self):
        d = Signal(4)
        d.set(2)
        self.assertEqual(d.get(), 2)
        self.assertEqual(d.get(str), '0010')
        self.assertEqual(d.get(list), [0, 0, 1, 0])
        self.assertEqual(d.get(int), 2)

        d.set('1101')
        self.assertEqual(d.get(), '1101')
        self.assertEqual(d.get(str), '1101')
        self.assertEqual(d.get(list), [1, 1, 0, 1])
        self.assertEqual(d.get(int), 13)
        self.assertEqual(d.dim(), (4,))
        self.assertEqual(d.dim()[0], 4)
        pass


    def test_2d_signal_get(self):
        d = Signal((4, 2), value='11100100')
        self.assertEqual(d.width(), 8)
        self.assertEqual(d.dim(), (4, 2))
        self.assertEqual(d.slice(1).get(str), '01')
        self.assertEqual(d.slice(2).get(str), '10')
        self.assertEqual(d.slice((2, 1)).get(str), '1')
        self.assertEqual(d.slice((2, 0)).get(str), '0')
        pass


    def test_2d_signal_set(self):
        d = Signal((4, 2), value='00000000')
        self.assertEqual(d.width(), 8)
        self.assertEqual(d.dim(), (4, 2))

        d.splice(1, '01')
        self.assertEqual(d.get(str), '00000100')
        d.splice(2, '10')
        self.assertEqual(d.get(str), '00100100')
        d.splice(3, '11')
        self.assertEqual(d.get(str), '11100100')
        d.splice(0, '00')
        self.assertEqual(d.get(str), '11100100')

        d.splice((2, 1), '0')
        self.assertEqual(d.get(str), '11000100')
        d.splice((2, 0), 1)
        self.assertEqual(d.get(str), '11010100')
        pass

    pass