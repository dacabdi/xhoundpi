import unittest
from xhoundpi import SampleClass

class test_SampleClass(unittest.TestCase):

    def test_get_value_should_return_init_value(self):
        sc = SampleClass(1)
        self.assertEqual(sc.get_value(), 1)

    def test_value_should_increment(self):
        sc = SampleClass(5)
        sc.increment_value()
        self.assertEqual(sc.get_value(), 6)
