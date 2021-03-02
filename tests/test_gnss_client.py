import unittest
from io import BytesIO

from xhoundpi.serial import StubSerial
from xhoundpi.gnss_client import GnssClient

class test_GnssClient(unittest.TestCase):

    def test_read(self):
        rx = BytesIO(b'\x01\x0a\x0b\xff\x0d\x1f')
        tx = BytesIO()
        ss = StubSerial(rx=rx, tx=tx)
        client = GnssClient(ss)

        self.assertEqual(b'\x01', client.read())
        self.assertEqual(b'\x0a', client.read())
        self.assertEqual(b'\x0b\xff\x0d', client.read(3))
        self.assertEqual(b'\x1f\x01\x0a\x0b', client.read(4))
        self.assertEqual(b'\xff\x0d\x1f\x01\x0a\x0b\xff\x0d\x1f\x01\x0a\x0b\xff', client.read(13))

    def test_write(self):
        rx = BytesIO()
        tx = BytesIO()
        ss = StubSerial(rx=rx, tx=tx)
        client = GnssClient(ss)

        self.assertEqual(1, client.write(bytes.fromhex('01')))
        self.assertEqual(b'\x01', tx.getvalue())

        self.assertEqual(3, client.write(bytes.fromhex('02 03 04')))
        self.assertEqual(b'\x01\x02\x03\x04', tx.getvalue())
