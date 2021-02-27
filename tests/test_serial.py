import unittest
from io import BytesIO
from xhoundpi.serial import StubSerial

class test_StubSerial(unittest.TestCase):

    def test_read(self):
        rx = BytesIO(b'\x01\x0a\x0b\xff\x0d\x1f')
        tx = BytesIO()
        ss = StubSerial(rx=rx, tx=tx)

        self.assertEqual(b'\x01', ss.read())
        self.assertEqual(b'\x0a', ss.read())
        self.assertEqual(b'\x0b\xff\x0d', ss.read(3))
        self.assertEqual(b'\x1f\x01\x0a\x0b', ss.read(4))
        self.assertEqual(b'\xff\x0d\x1f\x01\x0a\x0b\xff\x0d\x1f\x01\x0a\x0b\xff', ss.read(13))

    def test_write(self):
        rx = BytesIO()
        tx = BytesIO()
        ss = StubSerial(rx=rx, tx=tx)

        self.assertEqual(1, ss.write(bytes.fromhex('01')))
        self.assertEqual(b'\x01', tx.getvalue())

        self.assertEqual(3, ss.write(bytes.fromhex('02 03 04')))
        self.assertEqual(b'\x01\x02\x03\x04', tx.getvalue())
