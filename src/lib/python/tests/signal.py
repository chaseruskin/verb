# Project: Verb
# Test: signal.py
#
# Verifies behavior for the Signal class.

import unittest as ut
from ..verb.signal import *

class Test(ut.TestCase):

    def test_signal_internal_data(self):
        d0 = Signal(4, signed=True)
        d0.store(5)
        self.assertEqual(d0._width, 4)
        self.assertEqual(d0.bits(), '0101')
        self.assertEqual(d0.digits(), 5)
        self.assertEqual(d0.raw_data(), 5)
        d0[1] = 1
        self.assertEqual(d0.digits(), 7)
        self.assertEqual(d0.bits(), '0111')

        pass

    pass