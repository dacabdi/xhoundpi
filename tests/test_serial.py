import unittest
from io import BytesIO
from xhoundpi.serial import StubSerial

class test_StubSerial(unittest.TestCase):

    def test_read(self):
        rx = BytesIO(bytes.fromhex('01 0A 0B FF 0D 1F'))
        tx = BytesIO()
        ss = StubSerial(rx=rx, tx=tx)

        self.assertSequenceEqual([0x01], ss.read())
        self.assertSequenceEqual([0x0A], ss.read())
        self.assertSequenceEqual([0x0B, 0xFF, 0x0D], ss.read(3))
        self.assertSequenceEqual([0x1F, 0x01, 0x0A, 0x0B], ss.read(4))
        self.assertSequenceEqual([0xFF, 0x0D, 0x1F, 0x01, 0x0A, 0x0B, 0xFF, 0x0D, 0x1F, 0x01, 0x0A, 0x0B, 0xFF], ss.read(13))

    def test_write(self):
        rx = BytesIO()
        tx = BytesIO()
        ss = StubSerial(rx=rx, tx=tx)

        self.assertEqual(1, ss.write(bytes.fromhex('01')))
        self.assertSequenceEqual([0x1], tx.getvalue())

        self.assertEqual(3, ss.write(bytes.fromhex('02 03 04')))
        self.assertSequenceEqual([0x1, 0x2, 0x3, 0x4], tx.getvalue())