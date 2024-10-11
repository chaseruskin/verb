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
        pass

    pass