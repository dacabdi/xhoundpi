import unittest
from io import BytesIO

from xhoundpi.proto_class import ProtocolClass
from xhoundpi.proto_reader import StubProtocolReader, StubProtocolReaderProvider, HeaderMismatchError

class test_StubProtocolReader(unittest.TestCase):

    def test_read_with_defaults(self):
        stream = BytesIO(b'\x00\x01\x02\x03')
        parser = StubProtocolReader(message_length=1)

        self.assertEqual(parser.read_frame(b'\x00', stream), b'\x00\x00')
        self.assertEqual(parser.read_frame(b'\x00', stream), b'\x00\x01')
        self.assertEqual(parser.read_frame(b'\x00', stream), b'\x00\x02')
        self.assertEqual(parser.read_frame(b'\x00', stream), b'\x00\x03')

    def test_throws_on_mismatched_header(self):
        stream = BytesIO(b'\x00')
        parser = StubProtocolReader(message_length=1, expected_header=b'\x01')
        with self.assertRaises(HeaderMismatchError) as context:
            parser.read_frame(b'\x00', stream)

        self.assertEqual('Expected header b\'\\x00\' for protocol ProtocolClass.NONE and received b\'\\x01\'', str(context.exception))

    def test_read_with_non_defaults(self):
        stream = BytesIO(b'\x00\x01\x02\x03')
        parser = StubProtocolReader(message_length=2, expected_header=b'\x0b')

        self.assertEqual(parser.read_frame(b'\x0b', stream), b'\x0b\x00\x01')
        self.assertEqual(parser.read_frame(b'\x0b', stream), b'\x0b\x02\x03')

class test_StubProtocolReaderProvider(unittest.TestCase):

    def test_provide(self):
        reader = StubProtocolReader()
        provider = StubProtocolReaderProvider(reader)

        self.assertEqual(provider.get_reader(ProtocolClass.NONE), reader)
