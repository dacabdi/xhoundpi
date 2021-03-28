# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
import uuid
from typing import Protocol

import pyubx2
import pynmea2

from xhoundpi.async_ext import run_sync
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.message import Message
from xhoundpi.data_formatter import NMEADataFormatter, UBXDataFormatter
from xhoundpi.message_editor import NMEAMessageEditor, UBXMessageEditor
from xhoundpi.operator import NMEAOffsetOperator, UBXHiResOffsetOperator, UBXOffsetOperator
from xhoundpi.operator_provider import CoordinateOperationProvider
from xhoundpi.message_policy import HasLocationPolicy
from xhoundpi.message_policy_provider import OnePolicyProvider
from xhoundpi.processor import GenericProcessor

class test_Functional_OffsetProcessor(unittest.TestCase):

    def setup_processor(self, lat_off, long_off):
        return GenericProcessor(
            policy_provider=OnePolicyProvider(HasLocationPolicy()),
            operator_provider=CoordinateOperationProvider(
                nmea_operator=NMEAOffsetOperator(
                    msg_editor=NMEAMessageEditor(),
                    data_formatter=NMEADataFormatter(pynmea2.nmea_utils.dm_to_sd),
                    lat_offset=lat_off,
                    lon_offset=long_off),
                ubx_operator=UBXOffsetOperator(
                    msg_editor=UBXMessageEditor(),
                    data_formatter=UBXDataFormatter(),
                    lat_offset=lat_off,
                    lon_offset=long_off),
                ubx_hires_operator=UBXHiResOffsetOperator(
                    msg_editor=UBXMessageEditor(),
                    data_formatter=UBXDataFormatter(),
                    lat_offset=lat_off,
                    lon_offset=long_off)))

    # TODO continue testing functionally

    def test_ubx_hires_zero_offset(self):
        self.maxDiff = None
        frame = bytes.fromhex(
            '                  B5 62 01 14 24 00 00 00 00 00'
            'B0 19 B9 1D A5 4D E3 CE 34 07 AB 11 42 4D 00 00'
            'A8 C3 00 00 E5 18 FB 03 B2 9A 01 00 35 72 02 00'
            '5D EC                                          ')
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(frame))
        processor = self.setup_processor(0, 0)
        result = run_sync(processor.process(msg))
        self.assertEqual(result[1].payload.serialize().hex(' ').upper(), bytes.fromhex(
            'B5 62 01 14 24 00' # header + class + id + length
            '00 00 00 00 B0 19 B9 1D'
            'A5 4D E3 CE' # lon
            '34 07 AB 11' # lat
            '42 4D 00 00' # h
            'A8 C3 00 00' # h sea level
            'E5 18' # lonHp / latHp
            'FB 03 B2 9A 01 00 35 72 02 00'
            '5D EC').hex(' ').upper()) # checksum

    def test_ubx_zero_offset(self):
        # lon -823964140
        # lat 296421129
        frame = bytes.fromhex(
            '                                     B5 62 01 07'
            '5C 00 F8 0D B9 1D E5 07  02 1A 12 1E 31 37 3B 00'
            '00 00 A7 2D 06 00 03 03  EB 0C 14 4E E3 CE 09 07'
            'AB 11 7F 45 00 00 E6 BB  00 00 EC 28 00 00 BC 3D'
            '00 00 B0 00 00 00 D6 FF  FF FF E7 FE FF FF B5 00'
            '00 00 F8 A2 96 01 EA 01  00 00 80 A8 12 01 B0 00'
            '00 00 6C 18 42 3E 00 00  00 00 00 00 00 00 68 66')
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(frame))
        processor = self.setup_processor(0, 0)
        result = run_sync(processor.process(msg))
        self.assertEqual(result[1].payload.serialize().hex(' ').upper(), bytes.fromhex(
            'B5 62 01 07' # header + class + id
            '5C 00' # length
            'F8 0D B9 1D' # iTOW
            'E5 07 02 1A' # year/month/day
            '12 1E 31 37' # h/m/s
            '3B 00 00 00' # tAcc
            'A7 2D 06 00' # nano
            '03' # fixType
            '03' # flags
            'EB' # flags2
            '0C' # numSV
            '14 4E E3 CE' # lon
            '09 07 AB 11' # lat
            '7F 45 00 00 E6 BB  00 00 EC 28 00 00 BC 3D'
            '00 00 B0 00 00 00 D6 FF  FF FF E7 FE FF FF B5 00'
            '00 00 F8 A2 96 01 EA 01  00 00 80 A8 12 01 B0 00'
            '00 00 6C 18 42 3E 00 00  00 00 00 00 00 00 68 66').hex(' ').upper()) # checksum

#                                                                                        - offset 45
#B5 62 01 07 5C 00 F8 0D B9 1D E5 07 02 1A 12 1E 31 37 3B 00 00 00 A7 2D 06 00 03 03 EB 0C 15 4E E3 CE 09 07 AB 11 7F 45 00 00 E6 BB 00 00 EC 28 00 00 BC 3D 00 00 B0 00 00 00 D6 FF FF FF E7 FE FF FF B5 00 00 00 F8 A2 96 01 EA 01 00 00 80 A8 12 01 B0 00 00 00 6C 18 42 3E 00 00 00 00 00 00 00 00 69 AA
#B5 62 01 07 5C 00 F8 0D B9 1D E5 07 02 1A 12 1E 31 37 3B 00 00 00 A7 2D 06 00 03 03 EB 0C 14 4E E3 CE 09 07 AB 11 7F 45 00 00 E6 BB 00 00 EC 28 00 00 BC 3D 00 00 B0 00 00 00 D6 FF FF FF E7 FE FF FF B5 00 00 00 F8 A2 96 01 EA 01 00 00 80 A8 12 01 B0 00 00 00 6C 18 42 3E 00 00 00 00 00 00 00 00 68 66
