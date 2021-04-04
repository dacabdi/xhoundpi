# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest

from xhoundpi.panel.geometry import Geometry

class test_Geometry(unittest.TestCase):

    def test_geometry(self):
        geometry = Geometry(rows=10, cols=20, channels=2, depth=16)
        self.assertEqual(10, geometry.rows)
        self.assertEqual(20, geometry.cols)
        self.assertEqual((10, 20), geometry.row_major)
        self.assertEqual((20, 10), geometry.col_major)
        self.assertEqual(2, geometry.channels)
        self.assertEqual(16, geometry.depth)
        self.assertEqual((10, 20, 2), geometry.shape())

    def test_shape_modes(self):
        g1 = Geometry(rows=10, cols=20, channels=1, depth=8)
        g2 = Geometry(rows=10, cols=20, channels=2, depth=8)
        self.assertEqual((10, 20), g1.shape())
        self.assertEqual((20, 10), g1.shape(use_col_major=True))
        self.assertEqual((10, 20, 2), g2.shape())
        self.assertEqual((20, 10, 2), g2.shape(use_col_major=True))

    def test_equality(self):
        g1 = Geometry(rows=10, cols=20, channels=1, depth=8)
        g2 = Geometry(rows=11, cols=20, channels=1, depth=8)
        g3 = Geometry(rows=10, cols=21, channels=1, depth=8)
        g4 = Geometry(rows=10, cols=20, channels=2, depth=9)
        self.assertNotEqual(g1, g2)
        self.assertNotEqual(g1, g3)
        self.assertNotEqual(g1, g4)
        self.assertNotEqual(g2, g1)
        self.assertNotEqual(g2, g3)
        self.assertNotEqual(g2, g4)
        # ...
        self.assertEqual(g1, Geometry(rows=10, cols=20, channels=1, depth=8))
