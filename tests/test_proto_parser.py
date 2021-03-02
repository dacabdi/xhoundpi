import unittest
from unittest.mock import MagicMock, Mock
from io import BytesIO

from xhoundpi.proto_class import ProtocolClass
from xhoundpi.proto_classifier import StubProtocolClassifier
from xhoundpi.proto_parser import ProtocolParserProvider,\
                                  StubParserProvider, \
                                  StubProtocolParser, \
                                  UBXProtocolParser, \
                                  NMEAProtocolParser

class test_StubProtocolClassifier(unittest.TestCase):

    def test_classify(self):
        header_source = BytesIO(b'H')
        classifier = StubProtocolClassifier(ProtocolClass.UBX)

        self.assertEqual(classifier.classify(header_source), (b'H', ProtocolClass.UBX))

class test_StubProtocolParser(unittest.TestCase):

    def test_parse(self):
        data_source = b'\x01\x02'
        parser = StubProtocolParser()

        self.assertEqual(parser.parse(data_source), b'\x01\x02')

class test_UBXProtocolParser(unittest.TestCase):

    def test_parse(self):
        parser_lib_entry_point = MagicMock(return_value='parsed message')
        parser = UBXProtocolParser(parser_lib_entry_point)
        self.assertEqual(parser.parse(b'abc'), 'parsed message')
        parser_lib_entry_point.assert_called_once_with(b'abc')

class test_NMEAProtocolParser(unittest.TestCase):

    def test_parse(self):
        parser_lib_entry_point = MagicMock(return_value='parsed message')
        parser = NMEAProtocolParser(parser_lib_entry_point)
        self.assertEqual(parser.parse(b'abc'), 'parsed message')
        parser_lib_entry_point.assert_called_once_with(b'abc')

class test_StubParserProvider(unittest.TestCase):

    def test_provide_parser(self):
        stub_parser = StubProtocolParser()
        parser_provider = StubParserProvider(stub_parser)

        self.assertEqual(parser_provider.get_parser(ProtocolClass.NONE), stub_parser)

class test_ProtocolReaderProvider(unittest.TestCase):

    def test_provide(self):
        none_parser = Mock()
        none_parser.parse.return_value = "none reader"

        ubx_parser = Mock()
        ubx_parser.parse.return_value = "ubx reader"

        nmea_parser = Mock()
        nmea_parser.parse.return_value = "nmea reader"

        readers = {
            ProtocolClass.NONE : none_parser,
            ProtocolClass.UBX : ubx_parser,
            ProtocolClass.NMEA : nmea_parser,
        }

        provider = ProtocolParserProvider(readers)

        self.assertEqual(provider.get_parser(ProtocolClass.NONE).parse(), "none reader")
        self.assertEqual(provider.get_parser(ProtocolClass.UBX).parse(), "ubx reader")
        self.assertEqual(provider.get_parser(ProtocolClass.NMEA).parse(), "nmea reader")
