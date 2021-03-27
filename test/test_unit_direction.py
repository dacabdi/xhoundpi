# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
import unittest.mock

from xhoundpi.direction import Direction, CoordAxis

class test_Direction(unittest.TestCase):

    def test_from_symbol_north(self):
        self.assertEqual(Direction.from_symbol('N'), Direction.N)
        self.assertEqual(Direction.from_symbol('n'), Direction.N)
        self.assertEqual(Direction.from_symbol('North'), Direction.N)
        self.assertEqual(Direction.from_symbol('north'), Direction.N)

    def test_from_symbol_south(self):
        self.assertEqual(Direction.from_symbol('S'), Direction.S)
        self.assertEqual(Direction.from_symbol('s'), Direction.S)
        self.assertEqual(Direction.from_symbol('South'), Direction.S)
        self.assertEqual(Direction.from_symbol('south'), Direction.S)

    def test_from_symbol_east(self):
        self.assertEqual(Direction.from_symbol('E'), Direction.E)
        self.assertEqual(Direction.from_symbol('e'), Direction.E)
        self.assertEqual(Direction.from_symbol('East'), Direction.E)
        self.assertEqual(Direction.from_symbol('east'), Direction.E)

    def test_from_symbol_west(self):
        self.assertEqual(Direction.from_symbol('W'), Direction.W)
        self.assertEqual(Direction.from_symbol('w'), Direction.W)
        self.assertEqual(Direction.from_symbol('West'), Direction.W)
        self.assertEqual(Direction.from_symbol('west'), Direction.W)

    def test_from_symbol_error(self):
        with self.assertRaises(ValueError):
            Direction.from_symbol('Wea')
        with self.assertRaises(ValueError):
            Direction.from_symbol('4safda')
        with self.assertRaises(ValueError):
            Direction.from_symbol('')
        with self.assertRaises(ValueError):
            Direction.from_symbol('east1')
        with self.assertRaises(ValueError):
            Direction.from_symbol('Norht')

class test_CoordAxis(unittest.TestCase):

    def test_from_symbol_lat(self):
        self.assertEqual(CoordAxis.from_symbol('lat'), CoordAxis.LAT)
        self.assertEqual(CoordAxis.from_symbol('latitude'), CoordAxis.LAT)
        self.assertEqual(CoordAxis.from_symbol('dir_lat'), CoordAxis.LAT)
        self.assertEqual(CoordAxis.from_symbol(Direction.N), CoordAxis.LAT)
        self.assertEqual(CoordAxis.from_symbol('N'), CoordAxis.LAT)
        self.assertEqual(CoordAxis.from_symbol('n'), CoordAxis.LAT)
        self.assertEqual(CoordAxis.from_symbol('North'), CoordAxis.LAT)
        self.assertEqual(CoordAxis.from_symbol('north'), CoordAxis.LAT)
        self.assertEqual(CoordAxis.from_symbol(Direction.S), CoordAxis.LAT)
        self.assertEqual(CoordAxis.from_symbol('S'), CoordAxis.LAT)
        self.assertEqual(CoordAxis.from_symbol('s'), CoordAxis.LAT)
        self.assertEqual(CoordAxis.from_symbol('South'), CoordAxis.LAT)
        self.assertEqual(CoordAxis.from_symbol('south'), CoordAxis.LAT)

    def test_from_symbol_lon(self):
        self.assertEqual(CoordAxis.from_symbol('lon'), CoordAxis.LON)
        self.assertEqual(CoordAxis.from_symbol('long'), CoordAxis.LON)
        self.assertEqual(CoordAxis.from_symbol('longitude'), CoordAxis.LON)
        self.assertEqual(CoordAxis.from_symbol('dir_lon'), CoordAxis.LON)
        self.assertEqual(CoordAxis.from_symbol(Direction.E), CoordAxis.LON)
        self.assertEqual(CoordAxis.from_symbol('E'), CoordAxis.LON)
        self.assertEqual(CoordAxis.from_symbol('e'), CoordAxis.LON)
        self.assertEqual(CoordAxis.from_symbol('East'), CoordAxis.LON)
        self.assertEqual(CoordAxis.from_symbol('east'), CoordAxis.LON)
        self.assertEqual(CoordAxis.from_symbol(Direction.W), CoordAxis.LON)
        self.assertEqual(CoordAxis.from_symbol('W'), CoordAxis.LON)
        self.assertEqual(CoordAxis.from_symbol('w'), CoordAxis.LON)
        self.assertEqual(CoordAxis.from_symbol('West'), CoordAxis.LON)
        self.assertEqual(CoordAxis.from_symbol('west'), CoordAxis.LON)

    def test_from_symbol_error(self):
        with self.assertRaises(ValueError):
            CoordAxis.from_symbol('Wea')
        with self.assertRaises(ValueError):
            CoordAxis.from_symbol('4safda')
        with self.assertRaises(ValueError):
            CoordAxis.from_symbol('')
        with self.assertRaises(ValueError):
            CoordAxis.from_symbol('east1')
        with self.assertRaises(ValueError):
            CoordAxis.from_symbol('Norht')