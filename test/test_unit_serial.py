# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from io import BytesIO, StringIO

from xhoundpi.serial import StubSerialBinary, StubSerialText

class test_StubSerialBinary(unittest.TestCase):

    def test_read(self):
        rx = BytesIO(b'\x01\x0a\x0b\xff\x0d\x1f')
        tx = BytesIO()
        ss = StubSerialBinary(rx=rx, tx=tx)

        self.assertEqual(b'\x01', ss.read())
        self.assertEqual(b'\x0a', ss.read())
        self.assertEqual(b'\x0b\xff\x0d', ss.read(3))
        self.assertEqual(b'\x1f\x01\x0a\x0b', ss.read(4))
        self.assertEqual(b'\xff\x0d\x1f\x01\x0a\x0b\xff\x0d\x1f\x01\x0a\x0b\xff', ss.read(13))

    def test_write(self):
        rx = BytesIO()
        tx = BytesIO()
        ss = StubSerialBinary(rx=rx, tx=tx)

        self.assertEqual(1, ss.write(bytes.fromhex('01')))
        self.assertEqual(b'\x01', tx.getvalue())

        self.assertEqual(3, ss.write(bytes.fromhex('02 03 04')))
        self.assertEqual(b'\x01\x02\x03\x04', tx.getvalue())

class test_StubSerialText(unittest.TestCase):

    def test_read(self):
        rx = StringIO('010A0BFF0D1F')
        tx = StringIO()
        ss = StubSerialText(rx=rx, tx=tx)

        self.assertEqual('01', ss.read(2))
        self.assertEqual('0A', ss.read(2))
        self.assertEqual('0BFF0D', ss.read(6))
        self.assertEqual('1F010A0B', ss.read(8))
        self.assertEqual('FF0D1F010A0BFF0D1F010A0BFF', ss.read(26))

    def test_write(self):
        rx = StringIO()
        tx = StringIO()
        ss = StubSerialText(rx=rx, tx=tx)

        self.assertEqual(2, ss.write('01'))
        self.assertEqual('01', tx.getvalue())

        self.assertEqual(6, ss.write('020304'))
        self.assertEqual('01020304', tx.getvalue())
