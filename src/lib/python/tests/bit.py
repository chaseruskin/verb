import unittest as ut
from ..src.bit import bit

class Test(ut.TestCase):

    def test_init(self):
        b = bit(0b1100)
        self.assertEqual(b, 0b1100)
        self.assertEqual(bool(b), True)
        self.assertEqual(not b, False)

        b = bit(0b0000)
        self.assertEqual(bool(b), False)
        self.assertEqual(not b, True)
        pass