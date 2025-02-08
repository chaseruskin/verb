import unittest as ut
from ..src.coverage import *

class Test(ut.TestCase):

    def test_cross_flatten_2d(self):
        cross = CoverCross(
            name='test',
            nets=[
                CoverRange(name='a', span=range(0, 4)), 
                CoverRange(name='b', span=range(0, 4)),
            ]
        )
        self.assertEqual(0, cross._flatten((0, 0)))
        self.assertEqual(3, cross._flatten((3, 0)))
        self.assertEqual(4, cross._flatten((0, 1)))
        self.assertEqual(5, cross._flatten((1, 1)))
        self.assertEqual(15, cross._flatten((3, 3)))
        pass

    def test_cross_flatten_3d(self):
        cross = CoverCross(
            name='test',
            nets=[
                CoverRange(name='a', span=range(0, 2)), 
                CoverRange(name='b', span=range(0, 3)),
                CoverRange(name='b', span=range(0, 4)),
            ]
        )
        self.assertEqual(0, cross._flatten((0, 0, 0)))
        self.assertEqual(1, cross._flatten((1, 0, 0)))
        self.assertEqual(2*1, cross._flatten((0, 1, 0)))
        self.assertEqual(2*2, cross._flatten((0, 2, 0)))
        self.assertEqual(6, cross._flatten((0, 0, 1)))
        self.assertEqual(1 + 2 + 6, cross._flatten((1, 1, 1)))
        self.assertEqual(1 + 2*2 + 3*6, cross._flatten((1, 2, 3)))
        pass

    pass