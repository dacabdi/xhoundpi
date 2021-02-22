import unittest
from xhoundpi.serial import StubSerial

class test_StubSerial(unittest.TestCase):

    def test_read(self):
        rx = [0x0, 0x1, 0x2, 0x3, 0x4, 0x5]
        ss = StubSerial(rx=rx)

        self.assertSequenceEqual([0x0], ss.read())
        self.assertSequenceEqual([0x1], ss.read())
        self.assertSequenceEqual([0x2, 0x3], ss.read(2))
        self.assertSequenceEqual([0x4, 0x5, 0x0, 0x1], ss.read(4))

    def test_write(self):
        tx = []
        ss = StubSerial(tx=tx)

        self.assertEqual(1, ss.write([0x1]))
        self.assertSequenceEqual([0x1], tx)

        self.assertEqual(3, ss.write([0x2, 0x3, 0x4]))
        self.assertSequenceEqual([0x1, 0x2, 0x3, 0x4], tx)