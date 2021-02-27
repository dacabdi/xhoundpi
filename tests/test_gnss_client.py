import unittest
from io import BytesIO

from xhoundpi.serial import StubSerial
from xhoundpi.gnss_client import GnssClient

class test_GnssClient(unittest.TestCase):

    def test_read(self):
        rx = BytesIO(bytes.fromhex('01 0A 0B FF 0D 1F'))
        tx = BytesIO()
        ss = StubSerial(rx=rx, tx=tx)
        client = GnssClient(ss)

        self.assertSequenceEqual([0x01], client.read())
        self.assertSequenceEqual([0x0A], client.read())
        self.assertSequenceEqual([0x0B, 0xFF, 0x0D], client.read(3))
        self.assertSequenceEqual([0x1F, 0x01, 0x0A, 0x0B], client.read(4))
        self.assertSequenceEqual([0xFF, 0x0D, 0x1F, 0x01, 0x0A, 0x0B, 0xFF, 0x0D, 0x1F, 0x01, 0x0A, 0x0B, 0xFF], client.read(13))

    def test_write(self):
        rx = BytesIO()
        tx = BytesIO()
        ss = StubSerial(rx=rx, tx=tx)
        client = GnssClient(ss)

        self.assertEqual(1, client.write(bytes.fromhex('01')))
        self.assertSequenceEqual([0x1], tx.getvalue())

        self.assertEqual(3, client.write(bytes.fromhex('02 03 04')))
        self.assertSequenceEqual([0x1, 0x2, 0x3, 0x4], tx.getvalue())