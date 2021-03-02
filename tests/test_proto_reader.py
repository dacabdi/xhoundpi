import unittest
from unittest.mock import Mock
from io import BytesIO

from xhoundpi.proto_class import ProtocolClass
from xhoundpi.proto_reader import ProtocolReaderProvider, StubProtocolReader,\
                                  UBXProtocolReader,\
                                  NMEAProtocolReader,\
                                  StubProtocolReaderProvider,\
                                  HeaderMismatchError,\
                                  MalformedFrameError

class test_StubProtocolReader(unittest.TestCase):

    def test_read_with_defaults(self):
        stream = BytesIO(b'\x00\x01\x02\x03')
        reader = StubProtocolReader(message_length=1)

        self.assertEqual(reader.read_frame(b'\x00', stream), b'\x00\x00')
        self.assertEqual(reader.read_frame(b'\x00', stream), b'\x00\x01')
        self.assertEqual(reader.read_frame(b'\x00', stream), b'\x00\x02')
        self.assertEqual(reader.read_frame(b'\x00', stream), b'\x00\x03')

    def test_throws_on_mismatched_header(self):
        stream = BytesIO(b'\x00')
        reader = StubProtocolReader(message_length=1, expected_header=b'\x01')
        with self.assertRaises(HeaderMismatchError) as context:
            reader.read_frame(b'\x00', stream)

        self.assertEqual("Received header '0x00' is not in the list of acceptable headers ['0x01'] for ProtocolClass.NONE.", str(context.exception))

    def test_read_with_non_defaults(self):
        stream = BytesIO(b'\x00\x01\x02\x03')
        reader = StubProtocolReader(message_length=2, expected_header=b'\x0b')

        self.assertEqual(reader.read_frame(b'\x0b', stream), b'\x0b\x00\x01')
        self.assertEqual(reader.read_frame(b'\x0b', stream), b'\x0b\x02\x03')

class test_UBXProtocolReader(unittest.TestCase):

    def test_read_frame(self):
        reader = UBXProtocolReader()
        # the reader assumes the header has already been consumed
        stream = BytesIO(bytes.fromhex(
              '01 03 10 00 10 0A B9 1D 03 DF 02 08 FE 01 00 00 D7 EF 11 00 C6 F1'
            + '01 25 14 00 10 0A B9 1D EA 9B 07 00 79 2E 06 00 62 04 12 07 27 00 00 00 09 60'
            + '01 22 14 00 10 0A B9 1D F5 13 09 00 CD 00 00 00 25 00 00 00 01 06 00 00 31 90'
            # long message
            '      0A 37 E2 00 00 22 01 30 30 31 39 30 30 30'
          + '30 00 00 07 EE 7A 0E 5A 00 00 00 00 00 00 21 01'
          + 'FF 00 00 01 60 01 00 00 00 02 60 00 01 00 00 03'
          + '60 01 03 00 00 04 60 01 02 00 00 05 40 00 10 00'
          + '00 06 21 01 FF 00 00 07 61 01 12 00 00 08 61 01'
          + '13 00 00 09 40 01 14 00 00 0A 60 00 15 00 00 0B'
          + '40 01 0E 00 00 0C 40 01 0A 00 00 0D 60 01 0B 00'
          + '00 0E 60 01 0F 00 00 0F 51 00 44 00 00 10 44 00'
          + '16 00 01 00 21 01 FF 00 01 01 60 01 00 00 01 02'
          + '60 00 01 00 01 03 21 01 FF 00 01 04 71 00 46 00'
          + '01 05 21 01 FF 00 01 06 21 01 FF 00 01 07 41 01'
          + '12 00 01 08 61 01 13 00 01 09 60 01 14 00 01 0A'
          + '60 00 15 00 01 0B 21 01 FF 00 01 0C 21 01 FF 00'
          + '01 0D 21 01 FF 00 01 0E 21 01 FF 00 01 0F 21 01'
          + 'FF 00 01 10 21 01 FF 00 71 C3                  '))

        self.assertEqual(reader.read_frame(b'\xb5\x62', stream),
            bytes.fromhex('B5 62 01 03 10 00 10 0A B9 1D 03 DF 02 08 FE 01 00 00 D7 EF 11 00 C6 F1'))
        self.assertEqual(reader.read_frame(b'\xb5\x62', stream),
            bytes.fromhex('B5 62 01 25 14 00 10 0A B9 1D EA 9B 07 00 79 2E 06 00 62 04 12 07 27 00 00 00 09 60'))
        self.assertEqual(reader.read_frame(b'\xb5\x62', stream),
            bytes.fromhex('B5 62 01 22 14 00 10 0A B9 1D F5 13 09 00 CD 00 00 00 25 00 00 00 01 06 00 00 31 90'))
        self.assertEqual(reader.read_frame(b'\xb5\x62', stream),
            bytes.fromhex('B5 62 0A 37 E2 00 00 22 01 30 30 31 39 30 30 30'
                        + '30 00 00 07 EE 7A 0E 5A 00 00 00 00 00 00 21 01'
                        + 'FF 00 00 01 60 01 00 00 00 02 60 00 01 00 00 03'
                        + '60 01 03 00 00 04 60 01 02 00 00 05 40 00 10 00'
                        + '00 06 21 01 FF 00 00 07 61 01 12 00 00 08 61 01'
                        + '13 00 00 09 40 01 14 00 00 0A 60 00 15 00 00 0B'
                        + '40 01 0E 00 00 0C 40 01 0A 00 00 0D 60 01 0B 00'
                        + '00 0E 60 01 0F 00 00 0F 51 00 44 00 00 10 44 00'
                        + '16 00 01 00 21 01 FF 00 01 01 60 01 00 00 01 02'
                        + '60 00 01 00 01 03 21 01 FF 00 01 04 71 00 46 00'
                        + '01 05 21 01 FF 00 01 06 21 01 FF 00 01 07 41 01'
                        + '12 00 01 08 61 01 13 00 01 09 60 01 14 00 01 0A'
                        + '60 00 15 00 01 0B 21 01 FF 00 01 0C 21 01 FF 00'
                        + '01 0D 21 01 FF 00 01 0E 21 01 FF 00 01 0F 21 01'
                        + 'FF 00 01 10 21 01 FF 00 71 C3'))

    def test_throws_on_mismatched_header(self):
        reader = UBXProtocolReader()
        # the reader assumes the header has already been consumed
        stream = BytesIO(bytes.fromhex('01 03 10 00 10 0A B9 1D 03 DF 02 08 FE 01 00 00 D7 EF 11 00 C6 F1'))
        with self.assertRaises(HeaderMismatchError) as context:
            reader.read_frame(b'\x00', stream)

        self.assertEqual("Received header '0x00' is not in the list of acceptable headers ['0xB562'] for ProtocolClass.UBX.", str(context.exception))
        self.assertEqual(context.exception.protocol, ProtocolClass.UBX)

    def test_throws_on_malformed_preamble(self):
        reader = UBXProtocolReader()
        # the reader assumes the header has already been consumed
        stream = BytesIO(bytes.fromhex('01 03 10'))
        with self.assertRaises(MalformedFrameError) as context:
            reader.read_frame(b'\xb5\x62', stream)

        self.assertEqual('Error reading ProtocolClass.UBX frame: Found EOF attempting to read frame preamble. Read 3 bytes out of 4 expected.', str(context.exception))
        self.assertEqual(context.exception.details, bytes.fromhex('01 03 10'))
        self.assertEqual(context.exception.protocol, ProtocolClass.UBX)

    def test_throws_on_malformed_body(self):
        reader = UBXProtocolReader()
        # the reader assumes the header has already been consumed
        stream = BytesIO(bytes.fromhex('01 03 10 00 10 0A B9 1D 03 DF 02 08 FE 01 00 00 D7 EF 11'))
        with self.assertRaises(MalformedFrameError) as context:
            reader.read_frame(b'\xb5\x62', stream)

        self.assertEqual('Error reading ProtocolClass.UBX frame: Found EOF attempting to read frame body. Read 15 bytes out of 16 expected.', str(context.exception))
        self.assertEqual(context.exception.details, bytes.fromhex('10 0A B9 1D 03 DF 02 08 FE 01 00 00 D7 EF 11'))
        self.assertEqual(context.exception.protocol, ProtocolClass.UBX)

    def test_throws_on_malformed_checksum_0(self):
        reader = UBXProtocolReader()
        # the reader assumes the header has already been consumed
        stream = BytesIO(bytes.fromhex('01 03 10 00 10 0A B9 1D 03 DF 02 08 FE 01 00 00 D7 EF 11 00'))
        with self.assertRaises(MalformedFrameError) as context:
            reader.read_frame(b'\xb5\x62', stream)

        self.assertEqual('Error reading ProtocolClass.UBX frame: Found EOF attempting to read frame checksum. Read 0 bytes out of 2 expected.', str(context.exception))
        self.assertEqual(context.exception.details, bytes.fromhex(''))
        self.assertEqual(context.exception.protocol, ProtocolClass.UBX)

    def test_throws_on_malformed_checksum_1(self):
        reader = UBXProtocolReader()
        # the reader assumes the header has already been consumed
        stream = BytesIO(bytes.fromhex('01 03 10 00 10 0A B9 1D 03 DF 02 08 FE 01 00 00 D7 EF 11 00 C6'))
        with self.assertRaises(MalformedFrameError) as context:
            reader.read_frame(b'\xb5\x62', stream)

        self.assertEqual('Error reading ProtocolClass.UBX frame: Found EOF attempting to read frame checksum. Read 1 bytes out of 2 expected.', str(context.exception))
        self.assertEqual(context.exception.details, bytes.fromhex('C6'))
        self.assertEqual(context.exception.protocol, ProtocolClass.UBX)

class test_NMEAProtocolReader(unittest.TestCase):

    def test_read_frame(self):
        reader = NMEAProtocolReader()
        # the reader assumes the header has already been consumed
        stream = BytesIO(bytes.fromhex(
            #msg1
              '   47 50 47 53 56 2C 32 2C 32 2C 30 35 2C 33 30'
            + '2C 30 36 2C 33 30 34 2C 2C 30 2A 35 32 0D 0A   '
            #msg2
            + '   47 4C 47 53 56 2C 31 2C 31 2C 30 32 2C 37 31'
            + '2C 33 37 2C 32 37 33 2C 33 37 2C 37 33 2C 34 33'
            + '2C 33 34 30 2C 31 36 2C 31 2A 37 39 0D 0A      '
            #msg3 (special, vendor extensions)
            + '   50 55 42 58 2C 30 33 2C 33 32 2C 31 2C 2D 2C'
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
            + '30 2A 34 43 0D 0A                              '))

        self.assertEqual(reader.read_frame(b'\x24', stream),
            bytes.fromhex('24 47 50 47 53 56 2C 32 2C 32 2C 30 35 2C 33 30'
                        + '2C 30 36 2C 33 30 34 2C 2C 30 2A 35 32 0D 0A   '))
        self.assertEqual(reader.read_frame(b'\x24', stream),
            bytes.fromhex('24 47 4C 47 53 56 2C 31 2C 31 2C 30 32 2C 37 31'
                        + '2C 33 37 2C 32 37 33 2C 33 37 2C 37 33 2C 34 33'
                        + '2C 33 34 30 2C 31 36 2C 31 2A 37 39 0D 0A      '))
        self.assertEqual(reader.read_frame(b'\x24', stream),
            bytes.fromhex('24 50 55 42 58 2C 30 33 2C 33 32 2C 31 2C 2D 2C'
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
                        + '30 2A 34 43 0D 0A                              '))

    def test_throws_on_mismatched_header(self):
        reader = NMEAProtocolReader()
        # the reader assumes the header has already been consumed
        stream = BytesIO()
        with self.assertRaises(HeaderMismatchError) as context:
            reader.read_frame(b'\x00', stream)

        self.assertEqual("Received header '0x00' is not in the list of acceptable headers ['0x24','0x21'] for ProtocolClass.NMEA.", str(context.exception))
        self.assertEqual(context.exception.protocol, ProtocolClass.NMEA)

    def test_throws_on_non_vendor_frame_too_long(self):
        reader = NMEAProtocolReader()
        # the reader assumes the header has already been consumed
        stream_ok = BytesIO(bytes.fromhex(
              '   47 50 47 53 56 2C 32 2C 32 2C 30 35 2C 33 30'
            + '2C 30 36 2C 33 30 34 2C 2C 30 2A 35 00 00 00 00'
            + '2C 30 36 2C 33 30 34 2C 2C 30 2A 35 00 00 00 00'
            + '2C 30 36 2C 33 30 34 2C 2C 30 2A 35 00 00 00 00'
            + '2C 30 36 2C 33 30 34 2C 2C 30 2A 35 00 00 00 00' # 79 + 1 assumed by the header
            + '0D 0A')) # 82
        stream_too_long = BytesIO(bytes.fromhex(
              '   47 50 47 53 56 2C 32 2C 32 2C 30 35 2C 33 30'
            + '2C 30 36 2C 33 30 34 2C 2C 30 2A 35 00 00 00 00'
            + '2C 30 36 2C 33 30 34 2C 2C 30 2A 35 00 00 00 00'
            + '2C 30 36 2C 33 30 34 2C 2C 30 2A 35 00 00 00 00'
            + '2C 30 36 2C 33 30 34 2C 2C 30 2A 35 00 00 00 00' # 79 + 1 assumed by the header
            + '00 0D 0A')) # 83

        try:
            reader.read_frame(b'\x24', stream_ok)
        except MalformedFrameError:
            self.fail("reader raised an unexpected exception")

        with self.assertRaises(MalformedFrameError) as context:
            reader.read_frame(b'\x24', stream_too_long)

        self.assertEqual("Error reading ProtocolClass.NMEA frame: Failed to find the frame's end marker of non-special message before the max expected size (82 bytes).", str(context.exception))
        self.assertEqual(context.exception.protocol, ProtocolClass.NMEA)

class test_StubProtocolReaderProvider(unittest.TestCase):

    def test_provide(self):
        reader = StubProtocolReader()
        provider = StubProtocolReaderProvider(reader)

        self.assertEqual(provider.get_reader(ProtocolClass.NONE), reader)

class test_ProtocolReaderProvider(unittest.TestCase):

    def test_provide(self):
        none_reader = Mock()
        none_reader.read_frame.return_value = "none reader"

        ubx_reader = Mock()
        ubx_reader.read_frame.return_value = "ubx reader"

        nmea_reader = Mock()
        nmea_reader.read_frame.return_value = "nmea reader"

        readers = {
            ProtocolClass.NONE : none_reader,
            ProtocolClass.UBX : ubx_reader,
            ProtocolClass.NMEA : nmea_reader,
        }

        provider = ProtocolReaderProvider(readers)

        self.assertEqual(provider.get_reader(ProtocolClass.NONE).read_frame(), "none reader")
        self.assertEqual(provider.get_reader(ProtocolClass.UBX).read_frame(), "ubx reader")
        self.assertEqual(provider.get_reader(ProtocolClass.NMEA).read_frame(), "nmea reader")
