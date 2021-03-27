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
from xhoundpi.message_editor import UBXMessageEditor
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

    def test_modify_one_field(self):
        editor = UBXMessageEditor()
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(self.common_frame))

        self.assertEqual(msg.payload.lon, -823964140)

        status, msg = editor.set_fields(msg, [('lon', -923964140)])

        self.assertEqual(status, Status.OK())
        self.assertEqual(msg.message_id, uuid.UUID('{12345678-1234-5678-1234-567812345678}'))
        self.assertEqual(msg.proto, ProtocolClass.UBX)
        self.assertEqual(msg.payload.lon, -923964140)
        self.assertEqual(msg.payload.serialize(), bytes.fromhex(
            'B5 62 01 14 24 00' # header + class + id + length
            '00 00 00 00 F8 0D B9 1D'
            '14 6D ED C8' # lon == -923964140
            '09 07 AB 11 7F 45 00 00 E6 BB 00 00 23 29'
            'FE FC 38 99 01 00 59 69 02 00'
            '57 16')) # checksum also changed

    def test_should_fail_if_field_does_not_exist(self):
        editor = UBXMessageEditor()
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(self.common_frame))
        self.assertEqual(msg.payload.lon, -823964140)
        status, msg = editor.set_fields(msg, [('longitud', -923964140)])
        self.assertFalse(status.ok)
        self.assertEqual(status, Status.OK(AttributeError(
            "UBX message with class 'b'\\x01'', id b'\\x14', "
            "and identity NAV-HPPOSLLH, does not contain field 'longitud'")))
        self.assertEqual(msg.payload.lon, -823964140)
        self.assertEqual(msg.payload.serialize(), self.common_frame)
