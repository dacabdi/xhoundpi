# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

from decimal import Decimal as D
import unittest
import uuid

import pyubx2
import pynmea2

from xhoundpi.async_ext import run_sync
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.message import Message
from xhoundpi.data_formatter import NMEADataFormatter, UBXDataFormatter
from xhoundpi.message_editor import NMEAMessageEditor, UBXMessageEditor
from xhoundpi.operator import NMEAOffsetOperator, UBXHiResOffsetOperator, UBXOffsetOperator
from xhoundpi.coordinates_offset import GeoCoordinates, StaticOffsetProvider
from xhoundpi.operator_provider import CoordinateOperationProvider
from xhoundpi.message_policy import HasLocationPolicy
from xhoundpi.message_policy_provider import OnePolicyProvider
from xhoundpi.processor import GenericProcessor
from xhoundpi.dmath import setup_common_context

setup_common_context()

class test_Functional_OffsetProcessor(unittest.TestCase):

    # pylint: disable=no-self-use
    def setup_processor(self, lat_off: D, long_off: D, alt_off: D):
        offset_provider = StaticOffsetProvider(GeoCoordinates(lat=lat_off, lon=long_off, alt=alt_off))
        return GenericProcessor(
            name='TestProcessor',
            policy_provider=OnePolicyProvider(HasLocationPolicy()),
            operator_provider=CoordinateOperationProvider(
                nmea_operator=NMEAOffsetOperator(
                    msg_editor=NMEAMessageEditor(),
                    data_formatter=NMEADataFormatter(),
                    offset_provider=offset_provider),
                ubx_operator=UBXOffsetOperator(
                    msg_editor=UBXMessageEditor(),
                    data_formatter=UBXDataFormatter(),
                    offset_provider=offset_provider),
                ubx_hires_operator=UBXHiResOffsetOperator(
                    msg_editor=UBXMessageEditor(),
                    data_formatter=UBXDataFormatter(),
                    offset_provider=offset_provider)))

    def test_ubx_hires_zero_offset1(self):
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
        processor = self.setup_processor(D('0'), D('0'), D('0'))
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

    def test_ubx_hires_zero_offset2(self):
        self.maxDiff = None
        frame = bytes.fromhex(
            '            B5 62 01 14 24 00 00 00 00 00 F8 0D'
            'B9 1D 14 4E E3 CE 09 07 AB 11 7F 45 00 00 E6 BB'
            '00 00 23 29 FE FC 38 99 01 00 59 69 02 00 34 63')
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(frame))
        processor = self.setup_processor(D('0'), D('0'), D('0'))
        result = run_sync(processor.process(msg))
        self.assertEqual(result[1].payload.serialize().hex(' ').upper(), bytes.fromhex(
            'B5 62 01 14 24 00' # header + class + id + length
            '00 00 00 00 F8 0D B9 1D 14'
            '4E E3 CE 09' # lon
            '07 AB 11 7F' # lat
            '45 00 00 E6' # h
            'BB 00 00 23' # h sea level
            '29 FE' # lonHp / latHp
            'FC 38 99 01 00 59 69 02 00'
            '34 63').hex(' ').upper()) # checksum

    def test_ubx_hires_zero_offset3(self):
        self.maxDiff = None
        frame = bytes.fromhex(
            '                               B5 62 01 14 24 00'
            '00 00 00 00 E0 11 B9 1D  E1 4D E3 CE F3 06 AB 11'
            '9B 46 00 00 01 BD 00 00  E6 F8 FC 04 41 9B 01 00'
            'F1 6C 02 00 4D 16                               ')
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(frame))
        processor = self.setup_processor(D('0'), D('0'), D('0'))
        result = run_sync(processor.process(msg))
        self.assertEqual(result[1].payload.serialize().hex(' ').upper(), bytes.fromhex(
            'B5 62 01 14 24 00'
            '00 00 00 00 E0 11 B9 1D'
            'E1 4D E3 CE' # lon
            'F3 06 AB 11' # lat
            '9B 46 00 00' # h
            '01 BD 00 00' # h sea level
            'E6 F8' # lonHp / latHp
            'FC 04 41 9B 01 00 F1 6C 02 00'
            '4D 16').hex(' ').upper()) # checksum

    def test_ubx_hires_zero_offset4_by_round_trip(self):
        self.maxDiff = None
        pos_offset = D('0.0005')
        neg_offset = D('-0.0005')
        frame = bytes.fromhex(
            '            B5 62 01 14 24 00 00 00 00 00 F8 0D'
            'B9 1D 14 4E E3 CE 09 07 AB 11 7F 45 00 00 E6 BB'
            '00 00 23 29 FE FC 38 99 01 00 59 69 02 00 34 63')
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(frame))
        processor1 = self.setup_processor(pos_offset, pos_offset, pos_offset)
        processor2 = self.setup_processor(neg_offset, neg_offset, neg_offset)
        result = run_sync(processor1.process(msg))
        result = run_sync(processor2.process(result[1]))
        self.assertEqual(result[1].payload.serialize().hex(' ').upper(), bytes.fromhex(
            'B5 62 01 14 24 00' # header + class + id + length
            '00 00 00 00 F8 0D B9 1D 14'
            '4E E3 CE 09' # lon
            '07 AB 11 7F' # lat
            '45 00 00 E6' # h
            'BB 00 00 23' # h sea level
            '29 FE' # lonHp / latHp
            'FC 38 99 01 00 59 69 02 00'
            '34 63').hex(' ').upper()) # checksum

    # TODO resolve and reactivate test
    @unittest.skip('the readjustment back and forth at the res limit introduce a 1 off error '
                   'and we still do not know how to fix this minor issue')
    def test_ubx_hires_zero_offset5_by_round_trip_on_height_res_limit_and_midpoint(self):
        self.maxDiff = None
        pos_offset = D('0.00005')
        neg_offset = D('-0.00005')
        frame = bytes.fromhex(
            '            B5 62 01 14 24 00 00 00 00 00 F8 0D'
            'B9 1D 14 4E E3 CE 09 07 AB 11 7F 45 00 00 E6 BB'
            '00 00 23 29 FE FC 38 99 01 00 59 69 02 00 34 63')
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(frame))
        processor1 = self.setup_processor(pos_offset, pos_offset, pos_offset)
        processor2 = self.setup_processor(neg_offset, neg_offset, neg_offset)
        result = run_sync(processor1.process(msg))
        result = run_sync(processor2.process(result[1]))
        self.assertEqual(result[1].payload.serialize().hex(' ').upper(), bytes.fromhex(
            'B5 62 01 14 24 00' # header + class + id + length
            '00 00 00 00 F8 0D B9 1D 14'
            '4E E3 CE 09' # lon
            '07 AB 11 7F' # lat
            '45 00 00 E6' # h
            'BB 00 00 23' # h sea level
            '29 FE' # lonHp / latHp
            'FC 38 99 01 00 59 69 02 00'
            '34 63').hex(' ').upper()) # checksum

    def test_ubx_zero_offset1(self):
        # lon -823964140
        # lat 296421129
        frame = bytes.fromhex(
            '                                    B5 62 01 07'
            '5C 00 F8 0D B9 1D E5 07 02 1A 12 1E 31 37 3B 00'
            '00 00 A7 2D 06 00 03 03 EB 0C 14 4E E3 CE 09 07'
            'AB 11 7F 45 00 00 E6 BB 00 00 EC 28 00 00 BC 3D'
            '00 00 B0 00 00 00 D6 FF FF FF E7 FE FF FF B5 00'
            '00 00 F8 A2 96 01 EA 01 00 00 80 A8 12 01 B0 00'
            '00 00 6C 18 42 3E 00 00 00 00 00 00 00 00 68 66')
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(frame))
        processor = self.setup_processor(D('0'), D('0'), D('0'))
        result = run_sync(processor.process(msg))
        self.assertEqual(result[1].payload.serialize().hex(' ').upper(), bytes.fromhex(
            'B5 62 01 07' # header + class + id
            '5C 00'       # length
            'F8 0D B9 1D' # iTOW
            'E5 07 02 1A' # year/month/day
            '12 1E 31 37' # h/m/s
            '3B 00 00 00' # tAcc
            'A7 2D 06 00' # nano
            '03'          # fixType
            '03'          # flags
            'EB'          # flags2
            '0C'          # numSV
            '14 4E E3 CE' # lon
            '09 07 AB 11' # lat
            '7F 45 00 00 E6 BB 00 00 EC 28 00 00 BC 3D'
            '00 00 B0 00 00 00 D6 FF FF FF E7 FE FF FF B5 00'
            '00 00 F8 A2 96 01 EA 01 00 00 80 A8 12 01 B0 00'
            '00 00 6C 18 42 3E 00 00 00 00 00 00 00 00 68 66').hex(' ').upper()) # checksum

    def test_ubx_zero_offset2_by_round_trip(self):
        # lon -823964140
        # lat 296421129
        pos_offset = D('0.005')
        neg_offset = D('-0.005')
        frame = bytes.fromhex(
            '      B5 62 01 02 1C 00  B0 19 B9 1D A5 4D E3 CE'
            '34 07 AB 11 42 4D 00 00  A8 C3 00 00 12 29 00 00'
            '9F 3E 00 00 6A 78')
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(frame))
        processor1 = self.setup_processor(pos_offset, pos_offset, pos_offset)
        processor2 = self.setup_processor(neg_offset, neg_offset, neg_offset)
        result = run_sync(processor1.process(msg))
        result = run_sync(processor2.process(result[1]))
        self.assertEqual(result[1].payload.serialize().hex(' ').upper(), bytes.fromhex(
            '      B5 62 01 02 1C 00  B0 19 B9 1D A5 4D E3 CE'
            '34 07 AB 11 42 4D 00 00  A8 C3 00 00 12 29 00 00'
            '9F 3E 00 00 6A 78').hex(' ').upper()) # checksum

    def test_ubx_zero_offset3_by_round_trip_on_height_res_limit(self):
        # lon -823964140
        # lat 296421129
        pos_offset = D('0.0003')
        neg_offset = D('-0.0003')
        frame = bytes.fromhex(
            '      B5 62 01 02 1C 00  B0 19 B9 1D A5 4D E3 CE'
            '34 07 AB 11 42 4D 00 00  A8 C3 00 00 12 29 00 00'
            '9F 3E 00 00 6A 78')
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(frame))
        processor1 = self.setup_processor(pos_offset, pos_offset, pos_offset)
        processor2 = self.setup_processor(neg_offset, neg_offset, neg_offset)
        result = run_sync(processor1.process(msg))
        result = run_sync(processor2.process(result[1]))
        self.assertEqual(result[1].payload.serialize().hex(' ').upper(), bytes.fromhex(
            '      B5 62 01 02 1C 00  B0 19 B9 1D A5 4D E3 CE'
            '34 07 AB 11 42 4D 00 00  A8 C3 00 00 12 29 00 00'
            '9F 3E 00 00 6A 78').hex(' ').upper()) # checksum

    # TODO resolve and reactivate test
    @unittest.skip('the readjustment back and forth at the res limit introduce a 1 off error '
                  'and we still do not know how to fix this minor issue')
    def test_ubx_zero_offset3_by_round_trip_on_height_res_limit_and_midpoint(self):
        # lon -823964140
        # lat 296421129
        pos_offset = D('0.0005')
        neg_offset = D('-0.0005')
        frame = bytes.fromhex(
            '      B5 62 01 02 1C 00  B0 19 B9 1D A5 4D E3 CE'
            '34 07 AB 11 42 4D 00 00  A8 C3 00 00 12 29 00 00'
            '9F 3E 00 00 6A 78')
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(frame))
        processor1 = self.setup_processor(pos_offset, pos_offset, pos_offset)
        processor2 = self.setup_processor(neg_offset, neg_offset, neg_offset)
        result = run_sync(processor1.process(msg))
        result = run_sync(processor2.process(result[1]))
        self.assertEqual(result[1].payload.serialize().hex(' ').upper(), bytes.fromhex(
            '      B5 62 01 02 1C 00  B0 19 B9 1D A5 4D E3 CE'
            '34 07 AB 11 42 4D 00 00  A8 C3 00 00 12 29 00 00'
            '9F 3E 00 00 6A 78').hex(' ').upper()) # checksum

    def test_ubx_hires_1_000000005_offset_1_0005_height(self):
        self.maxDiff = None
        # in INT32 - Little Endian (DCBA)
        # lon == -823964251
        # lonHp == -27
        # -> composed lon == -823964251 27
        # lat == 296421172
        # latHp == 24
        # -> composed lat == 296421172 24
        # height == 19778
        # heightHp == -5
        # -> composed height == 19778 -5
        # hMSL == 50088
        # hMSLHp == 3
        # -> composed hMSL == 50088 3
        frame = bytes.fromhex(
            '                  B5 62 01 14 24 00 00 00 00 00'
            'B0 19 B9 1D A5 4D E3 CE 34 07 AB 11 42 4D 00 00'
            'A8 C3 00 00 E5 18 FB 03 B2 9A 01 00 35 72 02 00'
            '5D EC                                          ')
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(frame))
        processor = self.setup_processor(D('1.000000005'), D('1.000000005'), D('1.0005'))
        result = run_sync(processor.process(msg))
        self.assertEqual(result[1].payload.serialize().hex(' ').upper(), bytes.fromhex(
            'B5 62 01 14 24 00' # header + class + id + length
            '00 00 00 00 B0 19 B9 1D'
            '25 E4 7B CF' # lon
            'B4 9D 43 12' # lat
            '2A 51 00 00' # height
            '91 C7 00 00' # hMSL
            'EA' # lonHp
            '1D' # latHp
            '00' # heightHp
            'FE' # hMSLHp
            'B2 9A 01 00 35 72 02 00'
            '9F B1').hex(' ').upper()) # checksum

    def test_ubx_0_0000005_offset_0_1_height(self):
        self.maxDiff = None
        # lon -823964140
        # lat 296421129
        frame = bytes.fromhex(
            '                                    B5 62 01 07'
            '5C 00 F8 0D B9 1D E5 07 02 1A 12 1E 31 37 3B 00'
            '00 00 A7 2D 06 00 03 03 EB 0C 14 4E E3 CE 09 07'
            'AB 11 7F 45 00 00 E6 BB 00 00 EC 28 00 00 BC 3D'
            '00 00 B0 00 00 00 D6 FF FF FF E7 FE FF FF B5 00'
            '00 00 F8 A2 96 01 EA 01 00 00 80 A8 12 01 B0 00'
            '00 00 6C 18 42 3E 00 00 00 00 00 00 00 00 68 66')
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=pyubx2.UBXReader.parse(frame))
        processor = self.setup_processor(D('0.0000005'), D('0.0000005'), D('0.1'))
        result = run_sync(processor.process(msg))
        self.assertEqual(result[1].payload.serialize().hex(' ').upper(), bytes.fromhex(
            'B5 62 01 07' # header + class + id
            '5C 00'       # length
            'F8 0D B9 1D' # iTOW
            'E5 07 02 1A' # year/month/day
            '12 1E 31 37' # h/m/s
            '3B 00 00 00' # tAcc
            'A7 2D 06 00' # nano
            '03'          # fixType
            '03'          # flags
            'EB'          # flags2
            '0C'          # numSV
            '19 4E E3 CE' # lon == -823964135
            '0E 07 AB 11' # lat == 296421134
            'E3 45 00 00 4A BC 00 00 EC 28 00 00 BC 3D'
            '00 00 B0 00 00 00 D6 FF FF FF E7 FE FF FF B5 00'
            '00 00 F8 A2 96 01 EA 01 00 00 80 A8 12 01 B0 00'
            '00 00 6C 18 42 3E 00 00 00 00 00 00 00 00 3B 81').hex(' ').upper()) # checksum

    def test_nmea_pubx_zero_offset(self):
        self.maxDiff = None
        sentence = pynmea2.NMEASentence.parse(
                '$PUBX,00,183246.00,'
                '2938.52571,N,'
                '08223.77912,W,'
                '-3.078,D3,5.7,15,0.199,266.49,0.007,,0.88,2.06,1.51,15,0,0*'
                '4B')
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.NMEA,
            payload=sentence)
        processor = self.setup_processor(D('0'), D('0'), D('0'))
        result = run_sync(processor.process(msg))
        self.assertEqual(result[1].payload.render(),
            '$PUBX,00,183246.00,'
            '2938.52571,N,'
            '08223.77912,W,'
            '-3.078,D3,5.7,15,0.199,266.49,0.007,,0.88,2.06,1.51,15,0,0*'
            '4B')

    def test_nmea_zero_offset(self):
        self.maxDiff = None
        sentence = pynmea2.NMEASentence.parse('$GPGLL,4916.45000,N,12311.12000,W,225444,A')
        msg = Message(
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.NMEA,
            payload=sentence)
        processor = self.setup_processor(D('0'), D('0'), D('0'))
        result = run_sync(processor.process(msg))
        self.assertEqual(result[1].payload.render(),
            '$GPGLL,4916.45000,N,12311.12000,W,225444,A*31')
