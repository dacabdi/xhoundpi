# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
import uuid

import pyubx2
import pynmea2

from xhoundpi.proto_class import ProtocolClass
from xhoundpi.status import Status
from xhoundpi.monkey_patching import add_method
from xhoundpi.message_editor import (NMEAMessageEditor,
                                    UBXMessageEditor)
from xhoundpi.message import Message

# patch NMEASentence to include byte serialization for uniform message API
@add_method(pynmea2.NMEASentence)
def serialize(self):
    return bytearray(self.render(newline=True), 'ascii')

# pylint: disable=protected-access
if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999

class test_UBXMessageEditor(unittest.TestCase):

    common_frame = frame = bytes.fromhex(
            'B5 62 01 14 24 00 00 00 00 00 F8 0D B9 1D 14 4E'
            'E3 CE 09 07 AB 11 7F 45 00 00 E6 BB 00 00 23 29'
            'FE FC 38 99 01 00 59 69 02 00 34 63            ')

    def test_set_one_field(self):
        editor = UBXMessageEditor()
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(self.common_frame))
        self.assertEqual(msg.payload.lon, -823964140)

        status, msg = editor.set_fields(msg, {'lon': -923964140})

        self.assertEqual(status, Status.OK())
        self.assertEqual(msg.message_id, uuid.UUID('{12345678-1234-5678-1234-567812345678}'))
        self.assertEqual(msg.proto, ProtocolClass.UBX)
        self.assertEqual(msg.payload.lon, -923964140)
        self.assertEqual(msg.payload.serialize(), bytes.fromhex(
            'B5 62 01 14 24 00' # header + class + id + length
            '00 00 00 00 F8 0D B9 1D'
            '14 6D ED C8' # lon == -923964140
            '09 07 AB 11' # lat
            '7F 45 00 00' # height
            'E6 BB 00 00' # height
            '23'          # lonHp
            '29'          # latHp
            'FE FC 38 99 01 00 59 69 02 00'
            '57 16')) # checksum also changed

    def test_set_multiple_field(self):
        editor = UBXMessageEditor()
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(self.common_frame))
        self.assertEqual(msg.payload.lon, -823964140)

        status, msg = editor.set_fields(msg, {
            'lon': 15,
            'lonHp': 16,
            'height' : 256,
            'hMSL' : 257
        })

        self.assertEqual(status, Status.OK())
        self.assertEqual(msg.message_id, uuid.UUID('{12345678-1234-5678-1234-567812345678}'))
        self.assertEqual(msg.proto, ProtocolClass.UBX)
        self.assertEqual(msg.payload.lon, 15)
        self.assertEqual(msg.payload.lonHp, 16)
        self.assertEqual(msg.payload.height, 256)
        self.assertEqual(msg.payload.hMSL, 257)
        self.assertEqual(msg.payload.serialize(), bytes.fromhex(
            'B5 62 01 14 24 00' # header + class + id + length
            '00 00 00 00 F8 0D B9 1D'
            '0F 00 00 00' # lon == 15
            '09 07 AB 11' # lat
            '00 01 00 00' # height == 256
            '01 01 00 00' # height (above sea level) == 257
            '10'          # lonHp
            '29'          # latHp
            'FE FC 38 99 01 00 59 69 02 00'
            'BB 5F')) # checksum also changed

    def test_should_fail_if_field_does_not_exist(self):
        editor = UBXMessageEditor()
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(self.common_frame))
        self.assertEqual(msg.payload.lon, -823964140)
        status, msg = editor.set_fields(msg, {'longitud': -923964140})
        self.assertFalse(status.ok)
        self.assertEqual(status, Status(AttributeError(
            "UBX message with class '0x01', id '0x14', "
            "and identity 'NAV-HPPOSLLH', does not contain field 'longitud'")))
        self.assertEqual(msg.payload.lon, -823964140)
        self.assertEqual(msg.payload.serialize(), self.common_frame)

class test_NMEAMessageEditor(unittest.TestCase):

    common_frame = frame = bytes.fromhex(
            '                               24 50 55 42 58 2C'
            '30 30 2C 31 38 33 32 34  36 2E 30 30 2C 32 39 33'
            '38 2E 35 32 35 37 31 2C  4E 2C 30 38 32 32 33 2E'
            '37 37 39 31 32 2C 57 2C  2D 33 2E 30 37 38 2C 44'
            '33 2C 35 2E 37 2C 31 35  2C 30 2E 31 39 39 2C 32'
            '36 36 2E 34 39 2C 30 2E  30 30 37 2C 2C 30 2E 38'
            '38 2C 32 2E 30 36 2C 31  2E 35 31 2C 31 35 2C 30'
            '2C 30 2A 34 42 0D 0A                            ')

    def test_set_one_field(self):
        self.maxDiff = None
        editor = NMEAMessageEditor()
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.NMEA,
            payload=pynmea2.NMEASentence.parse(self.common_frame.decode()))

        status, msg = editor.set_fields(msg, {'lon': '09223.77912'})

        self.assertEqual(status, Status.OK())
        self.assertEqual(msg.message_id, uuid.UUID('{12345678-1234-5678-1234-567812345678}'))
        self.assertEqual(msg.proto, ProtocolClass.NMEA)
        self.assertEqual(msg.payload.lon, '09223.77912')

        self.assertEqual(msg.payload.serialize(), bytes.fromhex(
            '                               24 50 55 42 58 2C'
            '30 30 2C 31 38 33 32 34  36 2E 30 30 2C 32 39 33'
            '38 2E 35 32 35 37 31 2C  4E 2C 30 39 32 32 33 2E'
            '37 37 39 31 32 2C 57 2C  2D 33 2E 30 37 38 2C 44'
            '33 2C 35 2E 37 2C 31 35  2C 30 2E 31 39 39 2C 32'
            '36 36 2E 34 39 2C 30 2E  30 30 37 2C 2C 30 2E 38'
            '38 2C 32 2E 30 36 2C 31  2E 35 31 2C 31 35 2C 30'
            '2C 30 2A 34 41 0D 0A                            '))

    def test_set_multiple_fields(self):
        self.maxDiff = None
        editor = NMEAMessageEditor()
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.NMEA,
            payload=pynmea2.NMEASentence.parse(self.common_frame.decode()))

        status, msg = editor.set_fields(msg, {
            'lon': '01000.00000',
            'lon_dir': 'E',
            'lat': '0010.00000',
            'lat_dir': 'S'
        })

        self.assertEqual(status, Status.OK())
        self.assertEqual(msg.message_id, uuid.UUID('{12345678-1234-5678-1234-567812345678}'))
        self.assertEqual(msg.proto, ProtocolClass.NMEA)
        self.assertEqual(msg.payload.lon, '01000.00000')
        self.assertEqual(msg.payload.lon_dir, 'E')
        self.assertEqual(msg.payload.lat, '0010.00000')
        self.assertEqual(msg.payload.lat_dir, 'S')
        self.assertEqual(msg.payload.serialize(), bytes.fromhex(
            '                               24 50 55 42 58 2C'
            '30 30 2C 31 38 33 32 34  36 2E 30 30 2C'
            '30 30 31 30 2E 30 30 30 30 30' # lat
            '2C 53 2C' # lat_dir
            '30 31 30 30 30 2E 30 30 30 30 30' # long
            '2C 45 2C' # long_dir
            '2D 33 2E 30 37 38 2C 44'
            '33 2C 35 2E 37 2C 31 35  2C 30 2E 31 39 39 2C 32'
            '36 36 2E 34 39 2C 30 2E  30 30 37 2C 2C 30 2E 38'
            '38 2C 32 2E 30 36 2C 31  2E 35 31 2C 31 35 2C 30'
            '2C 30 2A 34 31 0D 0A                            '))
