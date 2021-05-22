# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from unittest.mock import Mock, PropertyMock

import pyubx2
import pynmea2

from xhoundpi.message import Message
from xhoundpi.message_policy import AlwaysQualifiesPolicy, HasLocationPolicy

class test_AlwaysQualifiesPolicy(unittest.TestCase):

    def test_always_qualifies(self):
        policy = AlwaysQualifiesPolicy()
        self.assertTrue(policy.qualifies(None))

class test_HasLocationPolicy(unittest.TestCase):

    # pylint: disable=no-self-use
    def create_payload(self, with_lat: bool = True, with_lon: bool = True):
        mock = Mock()
        mock.lat = (PropertyMock(return_value=1)
            if with_lat else PropertyMock(side_effect=AttributeError()))
        mock.lon = (PropertyMock(return_value=1)
            if with_lon else PropertyMock(side_effect=AttributeError()))
        return mock

    def test_qualifies_with_mock_both_properties(self):
        msg = Message(None, None, self.create_payload())
        policy = HasLocationPolicy()
        self.assertTrue(policy.qualifies(msg))

    # NOTE Usually we do not do unit testing with the real
    # library types but given that the messages are too complicated
    # to put behind interfaces we use the types directly.
    # Then, we need to test against the real messages
    # to prevent runtime inconsistencies.

    # UBX

    def test_qualifies_with_pyubx2_payload(self):
        msg = Message(None, None, pyubx2.UBXMessage(ubxClass=b'\x01', ubxID=b'\x14', msgmode=0, lat=10, lon=10))
        policy = HasLocationPolicy()
        self.assertTrue(policy.qualifies(msg))

    def test_qualifies_not_with_no_properties_on_pyubx2_payload(self):
        msg1 = Message(None, None, pyubx2.UBXMessage(ubxClass=b'\x01', ubxID=b'\x13', msgmode=0))
        msg2 = Message(None, None, pyubx2.UBXMessage(ubxClass=b'\x01', ubxID=b'\x39', msgmode=0))
        msg3 = Message(None, None, pyubx2.UBXMessage(ubxClass=b'\x01', ubxID=b'\x04', msgmode=0))
        policy = HasLocationPolicy()
        self.assertFalse(policy.qualifies(msg1))
        self.assertFalse(policy.qualifies(msg2))
        self.assertFalse(policy.qualifies(msg3))

    # NMEA

    def test_qualifies_with_pynmea2_payload(self):
        msg = Message(None, None, pynmea2.parse("$GPGGA,184353.07,1929.045,S,02410.506,E,1,04,2.6,100.00,M,-33.9,M,,0000*6D"))
        policy = HasLocationPolicy()
        self.assertTrue(policy.qualifies(msg))

    def test_qualifies_not_with_no_properties_on_pynmea2_payload(self):
        msg = Message(None, None, pynmea2.parse("$GPGSA,A,3,23,29,07,08,09,18,26,28,,,,,1.94,1.18,1.54,1*10"))
        policy = HasLocationPolicy()
        self.assertFalse(policy.qualifies(msg))
