# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
import pyubx2
import pynmea2

from xhoundpi.monkey_patching import add_method

# patch NMEASentence to include byte serialization for uniform message API
@add_method(pynmea2.NMEASentence)
def serialize(self):
    return bytearray(self.render(newline=True), 'ascii')

# NOTE we do not own the parser libraries and these tests are a PoC.
# Do not expect exhaustive coverage of the API surface, these libs
# are supposed to be tested and correct on their own.

class test_pyubx2(unittest.TestCase):

    def test_parse(self):
        frame = bytes.fromhex('B5 62 01 03 10 00 10 0A B9 1D 03 DF 02 08 FE 01 00 00 D7 EF 11 00 C6 F1')
        msg = pyubx2.UBXReader.parse(frame)

        # non exhaustive properties check
        self.assertEqual(msg.msg_cls, b'\x01')
        self.assertEqual(msg.msg_id, b'\x03')
        self.assertEqual(msg.length, 16)
        self.assertEqual(msg.gpsFix, 3)
        self.assertEqual(msg.fixStat, b'\x02')
        self.assertEqual(msg.identity, 'NAV-STATUS')

    def test_serialize(self):
        frame = bytes.fromhex('B5 62 01 03 10 00 10 0A B9 1D 03 DF 02 08 FE 01 00 00 D7 EF 11 00 C6 F1')
        msg = pyubx2.UBXReader.parse(frame)
        self.assertEqual(msg.serialize(), bytes.fromhex('B5 62 01 03 10 00 10 0A B9 1D 03 DF 02 08 FE 01 00 00 D7 EF 11 00 C6 F1'))

class test_pynmea2(unittest.TestCase):

    def test_parse(self):
        frame = bytes.fromhex('24 47 50 47 53 56 2C 32 2C 32 2C 30 35 2C 33 30'
                            + '2C 30 36 2C 33 30 34 2C 2C 30 2A 35 32 0D 0A   ')

        sentence = pynmea2.parse(frame.decode())

        self.assertEqual(sentence.sentence_type, 'GSV')
        self.assertEqual(sentence.talker, 'GP')

    def test_parse_supports_vendor_frames(self):
        frame = bytes.fromhex(
              '24 50 55 42 58 2C 30 33 2C 33 32 2C 31 2C 2D 2C'
            + '31 37 32 2C 30 30 2C 2C 30 30 30 2C 33 2C 65 2C'
            + '31 39 38 2C 2D 31 2C 2C 30 30 30 2C 34 2C 55 2C'
            + '31 38 38 2C 35 32 2C 32 31 2C 30 30 30 2C 37 2C'
            + '55 2C 33 31 39 2C 33 37 2C 32 38 2C 30 30 35 2C'
            + '38 2C 55 2C 31 36 31 2C 37 31 2C 32 37 2C 30 30'
            + '38 2C 39 2C 55 2C 32 36 35 2C 36 30 2C 33 30 2C'
            + '30 32 30 2C 31 34 2C 2D 2C 32 35 32 2C 30 31 2C'
            + '2C 30 30 30 2C 31 36 2C 55 2C 30 34 36 2C 32 37'
            + '2C 31 37 2C 30 30 30 2C 32 31 2C 2D 2C 31 35 33'
            + '2C 31 32 2C 2C 30 30 30 2C 32 36 2C 65 2C 30 36'
            + '33 2C 30 36 2C 30 39 2C 30 30 30 2C 32 37 2C 55'
            + '2C 30 35 37 2C 35 35 2C 33 31 2C 30 35 30 2C 33'
            + '30 2C 2D 2C 33 30 34 2C 30 36 2C 2C 30 30 30 2C'
            + '31 33 31 2C 2D 2C 32 33 34 2C 33 39 2C 2C 30 30'
            + '30 2C 31 33 33 2C 55 2C 32 34 35 2C 32 39 2C 32'
            + '39 2C 30 30 30 2C 31 33 38 2C 2D 2C 32 32 33 2C'
            + '34 36 2C 2C 30 30 30 2C 32 31 37 2C 55 2C 31 38'
            + '31 2C 32 37 2C 31 34 2C 30 30 30 2C 32 32 33 2C'
            + '2D 2C 31 35 35 2C 31 39 2C 2C 30 30 30 2C 32 32'
            + '35 2C 2D 2C 31 30 30 2C 33 30 2C 31 33 2C 30 30'
            + '30 2C 32 32 39 2C 2D 2C 33 30 34 2C 33 31 2C 32'
            + '33 2C 30 30 30 2C 32 33 31 2C 55 2C 32 38 39 2C'
            + '33 37 2C 33 30 2C 30 36 34 2C 32 33 37 2C 55 2C'
            + '30 31 30 2C 35 36 2C 31 38 2C 30 30 30 2C 32 34'
            + '30 2C 65 2C 30 36 33 2C 31 38 2C 2C 30 30 30 2C'
            + '34 31 2C 2D 2C 33 30 33 2C 31 33 2C 2C 30 30 30'
            + '2C 34 38 2C 55 2C 32 32 35 2C 32 33 2C 31 37 2C'
            + '30 30 30 2C 34 39 2C 65 2C 31 38 30 2C 30 32 2C'
            + '2C 30 30 30 2C 35 31 2C 2D 2C 32 39 30 2C 30 34'
            + '2C 2C 30 30 30 2C 35 33 2C 55 2C 33 31 38 2C 34'
            + '33 2C 33 33 2C 30 36 34 2C 35 36 2C 55 2C 30 36'
            + '39 2C 34 33 2C 32 37 2C 30 30 33 2C 35 37 2C 2D'
            + '2C 30 33 34 2C 30 32 2C 2C 30 30 30 2C 36 32 2C'
            + '55 2C 31 35 31 2C 34 39 2C 32 32 2C 30 30 30 2C'
            + '37 30 2C 2D 2C 32 31 34 2C 32 34 2C 2C 30 30 30'
            + '2C 37 31 2C 65 2C 32 37 33 2C 33 37 2C 2C 30 30'
            + '30 2A 34 43 0D 0A                              ')

        sentence = pynmea2.parse(frame.decode())

        self.assertEqual(sentence.manufacturer, 'UBX')
        self.assertEqual(sentence.sentence_type, 'UBX03')

    def test_serialize(self):
        frame = bytes.fromhex('24 47 50 47 53 56 2C 32 2C 32 2C 30 35 2C 33 30'
                            + '2C 30 36 2C 33 30 34 2C 2C 30 2A 35 32 0D 0A   ')
        sentence = pynmea2.parse(frame.decode())
        self.assertEqual(sentence.serialize(), bytes.fromhex('24 47 50 47 53 56 2C 32 2C 32 2C 30 35 2C 33 30'
                                                           + '2C 30 36 2C 33 30 34 2C 2C 30 2A 35 32 0D 0A   '))
